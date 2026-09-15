#!/usr/bin/env python3
"""CALLS 候选提取器（V2：AST 提取 + 人工确认）

从 Layer-3 功能链的函数节点出发，用 Python ast 提取每个函数体里
调用了哪些函数，输出候选 CALLS 边清单（供人工读码确认后入图）。

用法:
    python3 call_candidates.py                 # 扫描所有 Layer-3-*.toml 的函数节点
    python3 call_candidates.py skill_load      # 只扫描文件名匹配的功能链

输出格式:
    func.xxx.yyy (文件:行号)
      → 调用 zzz [链路内 ✓ / 链路外]  (来源: import 映射)
"""
import ast
import os
import sys
try:
    import tomllib  # Python 3.11+ stdlib
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # 3.10 backport
    except ImportError:
        sys.exit(
            "call_candidates.py: Python 3.10 detected and `tomli` is not installed.\n"
            "Fix: `pip install tomli`   (or upgrade to Python 3.11+)."
        )
from pathlib import Path

# 被分析的源码根（不是 axgraph 插件根）。优先顺序：
#   1. 命令行 --project-root
#   2. 环境变量 AX_GRAPH_PROJECT_ROOT
#   3. 当前工作目录
# 这样 init 后的任意项目里跑 `ax extract` 都能找到自己的源码树。
PROJECT_ROOT = Path(os.environ.get("AX_GRAPH_PROJECT_ROOT", ".")).resolve()


def load_func_nodes(base_dir: Path = None):
    """从所有 Layer-3-*.toml 加载函数节点。

    axgraph init 生成的目录布局是：
        .axgraph/
            SCHEMA.md
            base-dir-<项目名>/
                Layer-1-Graph.toml
                Layer-2-Graph.toml
                Layer-3-Graph-<feature>.toml   ← 我们要扫这些
                base.toml

    所以 glob 要递归一层；跨 base-dir-* 的多个 base 也都要扫到。
    """
    funcs = []
    if base_dir is None:
        base_dir = PROJECT_ROOT / ".axgraph"
    # 递归搜 .axgraph/ 下所有 Layer-3-*.toml（覆盖任意 base-* 子目录）
    files = sorted(base_dir.glob("**/Layer-3-*.toml"))
    for p in files:
        try:
            d = tomllib.load(open(p, "rb"))
        except Exception as e:
            print(f"⚠️  TOML parse failed: {p}: {e}", file=sys.stderr)
            continue
        for n in d.get("nodes", []):
            if n.get("kind") == "function":
                funcs.append(n)
    return funcs


def file_import_map(py_path):
    """提取文件的 import 映射: 本地名 -> (模块路径, 原名)"""
    mapping = {}
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return mapping
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mapping[a.asname or a.name] = (a.name, a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            # 相对导入：数点
            dots = node.level
            if dots:
                # 相对当前文件所在包，简化处理：直接用节点 path 上下文
                mod = mod or ""
            for a in node.names:
                local = a.asname or a.name
                mapping[local] = (f"{mod}.{a.name}" if mod else a.name, a.name)
    return mapping


def find_func_node(tree, name, lineno):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name and node.lineno == lineno:
                return node
    # 容错：只按名字找（若行号漂移）
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    return None


def extract_calls(func_node):
    """提取函数体里的所有调用表达式（名字），按出现顺序"""
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                calls.append(f.id)
            elif isinstance(f, ast.Attribute):
                calls.append(ast.unparse(f))
    return calls


def main():
    filter_kw = sys.argv[1] if len(sys.argv) > 1 else ""
    funcs = load_func_nodes()
    if filter_kw:
        funcs = [n for n in funcs if filter_kw in n["id"] or filter_kw in n.get("path", "")]

    # 链路函数全集（用于标记"链路内调用"）
    chain_ids = {n["id"] for n in load_func_nodes()}
    # id -> (模块路径点分, 函数名)：func.agent.skill_commands._load_skill_payload
    id_meta = {}
    for n in load_func_nodes():
        rest = n["id"][len("func."):]  # agent.skill_commands._load_skill_payload
        parts = rest.split(".")
        fname = parts[-1]
        mod = ".".join(parts[:-1])
        id_meta[n["id"]] = (mod, fname)

    print(f"扫描 {len(funcs)} 个函数节点（链路函数共 {len(chain_ids)} 个）\n")
    for n in funcs:
        path = n["path"]  # agent/skill_commands.py:138
        py_rel, lineno = path.split(":")
        py_path = PROJECT_ROOT / py_rel
        if not py_path.exists():
            print(f"⚠️  文件不存在: {py_rel}\n")
            continue
        imap = file_import_map(py_path)
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="ignore"))
        fn = find_func_node(tree, n["id"].rsplit(".", 1)[-1], int(lineno))
        if fn is None:
            print(f"⚠️  AST 找不到函数: {n['id']} @ {py_rel}:{lineno}\n")
            continue

        calls = extract_calls(fn)
        print(f"▸ {n['id']} ({py_rel}:{lineno})")
        # 去重保序
        seen = set()
        for c in calls:
            if c in seen or c.startswith("self.") or c.startswith("cls."):
                continue
            seen.add(c)
            # 解析调用目标：import 映射
            base = c.split(".")[0]
            if base in imap:
                mod, orig = imap[base]
                # 重建完整调用: mod.orig(.剩余)
                full = f"{mod}.{orig}" + c[len(base):]
                hit = next((i for i in chain_ids if i.endswith("." + full.split(".")[-1]) and id_meta[i][0].replace(".", "/") in full.replace(".", "/")), None)
                in_chain = "链路内 ✓" if hit else "链路外"
                src = f"来源: {mod}"
            else:
                full = c
                hit = next((i for i in chain_ids if id_meta[i][1] == c.split(".")[-1]), None)
                in_chain = "链路内 ✓" if hit else "链路外"
                src = "来源: ?"
            print(f"    → {c}  [{in_chain}]  {src}")
        print()


if __name__ == "__main__":
    main()
