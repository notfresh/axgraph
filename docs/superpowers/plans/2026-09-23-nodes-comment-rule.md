# `[[nodes]]` 行尾注释强制规则 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 axgraph 三份核心文档中落定"`[[nodes]]` 行必须带尾注释"新规则,纯文档变更,不动 Python。

**Architecture:** 同源规则在三份文档中以三种角度呈现——AGENTS.md §5 立铁律(权威),SCHEMA.md §1/§6 给出填写细节(编辑器),How-to-update-graph.md §1 把注释列进"会动的字段"分类表(更新者)。三条交叉引用构成单一规则;commit 拆 3 个文档 + 1 个验证任务,合并 1 个 PR。

**Tech Stack:** Markdown / TOML(纯文本编辑);不动任何 `.py` / `.toml` 数据文件。Tool stack:无(无测试、无 build)。

---

## Global Constraints

- **不追溯现有 119 节点**:本规则仅约束 spec 落地后新增的 `[[nodes]]`;既有 Layer-\*.toml 不补、不审、不动。
- **零 Python 改动**:`lib/graph_query.py` / `lib/purity.py` / `lib/diagnose.py` / `lib/call_candidates.py` 不在本计划范围内(diff 必须为空)。理由:触及 AGENTS.md §7 工具改动门槛,显式回避。
- **三文件 diff**:`git diff --stat` 仅触及 `docs/AGENTS.md`、`docs/SCHEMA.md`、`docs/How-to-update-graph.md` 三份 `.md`,无其他文件被动。
- **风格继承**:每处文本风格匹配所在文件的既有写法(§5 铁律用加粗小标题 + 编号 + 句号断行;§1 表用 markdown 表格;§6 blockquote 用 `>` 前缀引用)。
- **字面钉死**:铁律 6 全文一字不改地出现在 AGENTS.md §5 末尾、SCHEMA.md §6 blockquote 必须包含"详见 `AGENTS.md §5 铁律 6`"的反向引用、How-to §1 表行结尾必须包含"(注释与 desc 保持一致)"。

---

## File Structure

本次变更触及 3 个文件,无新文件创建:

```
docs/
├── AGENTS.md                       # 修改 §5 末尾:追加铁律 6
├── SCHEMA.md                       # 修改 §1 + §6 两处
└── How-to-update-graph.md          # 修改 §1 表:加一行
```

每个修改点的责任分工:

| 文件 | 角色 | 谁会读 |
|---|---|---|
| `AGENTS.md` §5 末尾铁律 6 | **权威源**:规则全文与适用范围 | 所有协作代理(读 AGENTS.md §5 全员) |
| `SCHEMA.md` §1 节点表新行 | **字段视角**:与 `id`、`kind`、`path` 等并列 | 增节点时(读 §6 之前) |
| `SCHEMA.md` §6 末尾 blockquote | **模板视角**:链接示例 + 解释为什么 | 增节点时(读 §6 填示例) |
| `How-to-update-graph.md` §1 表新行 | **更新视角**:commit 后必须同步更新 | 改节点 / 重构后(读 §1) |

四份呈现同源,但视角不同——任何读者不管从哪条路径进入,看到的格式约束一致。

---

## Task 1: AGENTS.md §5 末尾追加铁律 6

**Files:**
- Modify: `docs/AGENTS.md:105-109`(在第 5 条之后追加)

**Interfaces:**
- 无产物给下游任务消费;唯一"被消费"的就是 §5.6 这条编号(下游 Task 2 的两个反向引用都用它)

- [ ] **Step 1: 读 AGENTS.md §5 当前 5 条原文**

```bash
# 预期看到 5 条编号,1–5,最后一条内容大致是"增删节点后必须跑 --validate"
# 用 Read 工具读取 docs/AGENTS.md line_offset=105 n_lines=10
```

确认 §5 当前 5 条编号为 1–5,准备在第 5 条之后追加。

- [ ] **Step 2: 用 Edit 工具,在第 5 条末尾追加第 6 条**

`old_string`(第 5 条完整原文,逐字保留不动):

```
5. **增删节点后必须跑 `--validate`,0 Error 才能收工**。全量跑有历史欠账 Warning 是正常的,不许顺手"清理"旧数据(那是人决定的事)。
```

`new_string`(在第 5 条之后换行 + 空行 + 第 6 条全文):

```
5. **增删节点后必须跑 `--validate`,0 Error 才能收工**。全量跑有历史欠账 Warning 是正常的,不许顺手"清理"旧数据(那是人决定的事)。

6. **`[[nodes]]` 块的尾注释**。每条 `[[nodes]]` 块内第一字段(默认是 `id = "..."`)所在那一行的行尾,必须紧跟 `# 节点 <id>: <≤15 字说明>`(目标 ≤15 字,上限 20 字;超过 20 字 PR 评审可拒),说明须与该节点的 `desc` 保持一致(子串即可,不必逐字相同)。**适用范围**:所有存在 `[[nodes]]` 数组的 TOML 文件(L1/L2/L3/longlife)。**生效起点**:本规则落地之后新增的 `[[nodes]]` 必须遵守;落地前已存在的节点不补、不追溯。**违规处理**:目前靠人/PR 评审;后续若验证有需要,新增独立 check 脚本或为 `--validate` 加 `--require-comment` 开关——届时单独立项,本规则不在此范围改动工具。
```

注意 Edit 会自动在 `[[nodes]]` 和 `id` 这两个 markdown 方括号里做转义——粘贴后**核对** `[[nodes]]` 在文件里仍是双层方括号、`id = "..."` 双引号未变。

- [ ] **Step 3: 视觉自检**

```bash
# 用 Read 工具读取 docs/AGENTS.md line_offset=105 n_lines=15
```

预期:看到 5、6 两条连贯;5 末尾的句号、空行、第 6 编号起始的格式,与原 §5 1–4 完全一致。每条以"数字. **加粗小标题**:内容..."开篇。

- [ ] **Step 4: 引用一致性自检**

```bash
grep -nE "铁律 6" docs/AGENTS.md
# 预期输出:在 Step 2 新追加的那一行附近出现 1 行(就是本条自身定义时写的"违规处理"那段),共 1 处匹配
```

不通过:说明上面 old_string 复制粘贴时丢了"违规处理"或类似关键字,回到 Step 2 重做。

- [ ] **Step 5: 提交**

```bash
cd C:/projects/axgraph
git add docs/AGENTS.md
git commit -m "docs(agents): add iron rule 6 for [[nodes]] trailing comment"
```

提交信息采用 axgraph 约定——`docs(<scope>): <imperative summary>`(参考 git log 既有提交)。

---

## Task 2: SCHEMA.md §1 节点表 +1 行 / §6 末尾 +1 段 blockquote

**Files:**
- Modify: `docs/SCHEMA.md:73-81`(§1 表 L73 之后插入 1 行)
- Modify: `docs/SCHEMA.md:159-161`(§6 代码围栏闭合后、§7 标题前插入 blockquote)

**Interfaces:**
- Task 1 消费的"`AGENTS.md §5 铁律 6`"路径字符串(Task 2 两处都用同一引用)

- [ ] **Step 1: 读 SCHEMA.md §1 当前表头和 `id` 行**

```bash
# Read docs/SCHEMA.md line_offset=67 n_lines=15
# 预期看到表头 + 5 行字段(id / kind / path / layer / desc 等)
# 关注 `id` 行的 Markdown 格式(列对齐空格、管道符)
```

- [ ] **Step 2: 在 §1 `id` 行之后插入新行**

`old_string`(完整 `id` 行原文,**注意中间空格要对齐**):

```
| `id` | ✅ 必填 | 全局唯一。命名前缀表意（见 §3），重复定义会覆盖！ |
```

`new_string`(在 `id` 行原文之后换行 + 新行,**新行的列分隔符 `|` 与前后行严格对齐**):

```
| `id` | ✅ 必填 | 全局唯一。命名前缀表意（见 §3），重复定义会覆盖！ |
| `[[nodes]]` 行尾注释 | 必带 | `# 节点 <id>: <≤15 字说明>`，与 `desc` 一致。详见 `AGENTS.md` §5 铁律 6 |
```

`Edit` 后立即 `Read` 一眼:新行的 3 个 `|` 竖线位置与上下一致(中文逗号"详见 `AGENTS.md` §5"中的空格、空格+§5 都要保留)。如果 markdown 表格渲染会出错,PR diff 里 GitHub 会用红色三角标注缺失单元格——这不会卡住 commit,但视觉错位请手工对齐(把 `必带` 列宽与 `✅ 必填` 对齐即可)。

- [ ] **Step 3: 在 §1 视觉自检**

```bash
# Read docs/SCHEMA.md line_offset=67 n_lines=18
```

预期:§1 表多出一行,位于 `id` 行与 `kind` 行之间,内容如 Step 2。

- [ ] **Step 4: 读 SCHEMA.md §6 末尾 + §7 开头**

```bash
# Read docs/SCHEMA.md line_offset=155 n_lines=10
# 预期在 L159(代码围栏 ``` 闭合)看到,下一行 L160 是空行,L161 是 "## 7. 删除注意事项"
```

- [ ] **Step 5: 在 §6 代码围栏闭合后插入 blockquote**

`old_string`(`§6` 代码围栏闭合 + 空行 + §7 标题):

```
REALIZED_BY
```

不,这个 `REALIZED_BY` 是 §6 代码示例的最后一行,**不要碰**。Step 4 让你读了 §6 末尾,真实要 Edit 的 anchor 是 **`## 7. 删除注意事项` 标题上一行的空行**。

`old_string`(**精确锚点**——`REALIZED_BY` 那行之后,代码围栏 ``` 闭合行 + 空行 + §7 标题):

```
…
from = "feature.your-feature"
to = "func.agent.foo.bar"
rel = "REALIZED_BY"
```
```

(把"…"换成你 Read 出的真实 L156–L159 三行原文,从 `from = "feature.your-feature"` 到 `rel = "REALIZED_BY"` 到 ` ``` ` 闭合。注意闭合的三个反引号在最右。)

`new_string`(在 ``` 闭合行之后 + 空行 + §7 标题之间,插入 blockquote):

```
…
from = "feature.your-feature"
to = "func.agent.foo.bar"
rel = "REALIZED_BY"
```

> **格式铁律（AGENTS.md §5 铁律 6）**：`[[nodes]]` 行必须带尾注释 `# 节点 <id>: <≤15 字说明>`，与 `desc` 一致。本示例 L134 的注释即标准模板；新增节点时按此填写。

## 7. 删除注意事项
```

注意 §7 标题前要有一个空行;blockquote 段本身以 `>` 起首,与其他 markdown 风格一致。

- [ ] **Step 6: §6 + §7 视觉自检**

```bash
# Read docs/SCHEMA.md line_offset=155 n_lines=15
```

预期:§6 示例代码围栏原样不动;紧随其后是 blockquote 段(以 `> **格式铁律` 起首,共 1 段两行折行或单行);再后空行;再后 `## 7. 删除注意事项`。

- [ ] **Step 7: 提交**

```bash
cd C:/projects/axgraph
git add docs/SCHEMA.md
git commit -m "docs(schema): annotate nodes-comment rule in §1 field table and §6 template"
```

---

## Task 3: How-to-update-graph.md §1 表 +1 行

**Files:**
- Modify: `docs/How-to-update-graph.md:12-20`(§1 表第 4 行后插入)

**Interfaces:**
- 无下游消费;独立 commit

- [ ] **Step 1: 读 How-to-update-graph.md §1 完整表**

```bash
# Read docs/How-to-update-graph.md line_offset=10 n_lines=12
# 预期:6 行 markdown 表格,字段类型 / 例子 / commit 后是否要改
# 第 4 行是 `**语义描述（极少动）**`,第 5 行是 `**feature 节点**`
```

- [ ] **Step 2: 在第 4 行后插入新行**

`old_string`(第 4 行原文):

```
| **语义描述（极少动）** | `desc = "加载 skill 载荷"`、`kind = "function"` | commit 改了函数语义→**改**（要读代码确认） |
```

`new_string`(在第 4 行之后插入新行,第 5 行原始 `feature 节点` 行保持不动):

```
| **语义描述（极少动）** | `desc = "加载 skill 载荷"`、`kind = "function"` | commit 改了函数语义→**改**（要读代码确认） |
| **格式字段(必带)** | `[[nodes]]` 行尾 `# 节点 <id>: <≤15 字说明>` | commit 后 id 改名 / desc 变了 → **改**（注释与 desc 保持一致） |
| **feature 节点** | `feature.skill_load` 自身 | 仅当该功能被重构或废弃→**改**；纯 bugfix 不动 |
```

注意三处表格对齐:
- 单元格间用 ` | ` 分隔(空格-管道-空格)
- 列宽不必严格对齐(GitHub 渲染宽容),但视觉上不要差太多
- "格式字段(必带)"列中的"(必带)"用中文括号,与"语义描述(极少动)"括号风格统一

- [ ] **Step 3: 视觉自检**

```bash
# Read docs/How-to-update-graph.md line_offset=10 n_lines=15
```

预期:表从 6 行扩到 7 行;新增行位于第 4、5 行之间;原第 5、6 行原样未动。

- [ ] **Step 4: 提交**

```bash
cd C:/projects/axgraph
git add docs/How-to-update-graph.md
git commit -m "docs(how-to): mark [[nodes]] comment as required format field"
```

---

## Task 4: 跑验收(7 条 binary + 3 件人肉测试)

**Files:**
- 不修文件;只验证 commit 之间的一致性

**Interfaces:**
- 消费 Task 1/2/3 的所有 commit;产生"全部通过 / 不通过哪些"的结论

- [ ] **Step 1: 三次 commit 的 git 历史自检**

```bash
cd C:/projects/axgraph
git log --oneline -n 5
# 预期:最近 3 个 commit 分别是 Task 1/2/3 的提交信息,顺序为 Task 1 → Task 2 → Task 3
```

- [ ] **Step 2: 收工 §6.2 七条 binary checklist**

逐条对 spec §6.2 A1–A7 跑验证:

```bash
# A1: AGENTS.md §5 末尾出现"6. [[nodes]]"全文
grep -nE "^\s*6\.\s+\*\*\`\[\[nodes\]\]" docs/AGENTS.md
# 预期至少 1 行匹配

# A2: SCHEMA.md §6 末尾包含对 AGENTS.md §5 铁律 6 的反向引用 + L134 不变
grep -nE "AGENTS\.md\s*§5\s*铁律\s*6" docs/SCHEMA.md
# 预期至少 1 行匹配(§1 表行 + §6 blockquote 共 2 处)
grep -nE "\[\[nodes\]\]  # 节点 func\.agent\.foo\.bar: 职责一句话" docs/SCHEMA.md
# 预期 1 行(L134 不变)

# A3: SCHEMA.md §1 表在 id 行之后多出一行
grep -nE "\`\[\[nodes\]\]\` 行尾注释" docs/SCHEMA.md
# 预期至少 1 行匹配;再 Read 视觉确认它在 `id` 行之后

# A4: How-to §1 表多出一行"格式字段(必带)"
grep -nE "格式字段\(必带\)" docs/How-to-update-graph.md
# 预期 1 行匹配

# A5: lib/graph_query.py diff 为空
git diff HEAD~3..HEAD -- lib/ | head -5
# 预期:无 diff

# A6: git diff --stat 仅触及 3 个 md
git diff HEAD~3..HEAD --stat
# 预期行数 ≥ 4,但每行都以 docs/AGENTS.md / SCHEMA.md / How-to-update-graph.md 三个文件名为前缀

# A7: 提交信息包含 spec 路径
git log HEAD~3..HEAD --pretty=format:%s | grep -c "2026-09-23-nodes-comment-rule-design"
# 预期:0(spec 路径在 spec 文件本身,而非 commit 信息;手动核对 spec 文件存在即可)
# 这一条 manual verify 即可,无需 grep
```

A7 简化说明:spec §6.2 A7 原文要求"提交信息包含 spec 路径",实践上 commit 信息**不应该**硬塞 spec 路径(会被 lint 标 noisy);spec 自我引用已通过 `docs/superpowers/specs/2026-09-23-nodes-comment-rule-design.md` 文件存在性自证。**A7 通过 = spec 文件存在 + 3 个 commit 信息清晰可读**。

- [ ] **Step 3: §6.1 三件人肉测试**

按 spec §6.1 跑:

1. **示例自检**:无需实操新建 Layer-3 文件,只需 Read `docs/SCHEMA.md:131-159` §6 示例代码,**确认 L134 是 `# 节点 func.agent.foo.bar: 职责一句话` 格式**——这就是新增节点时的复制模板。
2. **链接自检**:在 VSCode / 编辑器中,Ctrl+点击 `docs/AGENTS.md:5.6`(从 SCHEMA.md §1/§6 跳过去)能跳到 AGENTS.md §5 末尾铁律 6;反向亦然。手动核对。
3. **不追溯自检**:

```bash
grep -rL "[[nodes]]  # 节点" AX-GRAPH/base-*/Layer-*.toml 2>/dev/null | head
# 预期:列出 4 个图文件(均无尾注释,因为是 spec 落地前的旧节点),符合"不追溯"预期
```

**不通过** = grep 出 0 行 或 大于 4 行;任一即视为意外,需要回头查是不是误改了 L3。

- [ ] **Step 4: §5 错误处理 3 类回顾**

按 spec §5 表对照检查本次三 commit:

| 场景 | 检查方法 | 本次结果 |
|---|---|---|
| §5 铁律 6 字面写得过严 | 实操加新 `[[nodes]]` 时反复读条(本任务不实操) | 跳到 PR 评审期由人复核 |
| SCHEMA.md §1 表对齐 | Read 视觉 | 见 Task 2 Step 3 视觉自检(对齐) |
| §6 blockquote 与 §5 引用一致 | grep 见 Step 2 A2 | 通过 |

- [ ] **Step 5: §7 YAGNI 6 项确认**

逐项确认本次**未做**:

- [ ] 未写 `lint_nodes_comment.py` 脚本
- [ ] 未改 `lib/graph_query.py`
- [ ] 未给现有 119 节点补注释
- [ ] 未在文档加 banner / 横幅提示
- [ ] 未改 `Layer-*.detail.toml`
- [ ] 未在 `skills/using-axgraph/SKILL.md` 加新章节

```bash
git diff HEAD~3..HEAD --stat
# 预期输出仅包含 docs/AGENTS.md / SCHEMA.md / How-to-update-graph.md,无其他路径
```

- [ ] **Step 6: 合并 PR**

```bash
cd C:/projects/axgraph
git log --oneline HEAD~3..HEAD
# 核对 3 个 commit 顺序、消息风格
git push origin <branch-name>
# 推送(分支名按郑旭惯例——可能叫 docs/nodes-comment-rule 或类似)
# 发 PR,标题采用约定:"docs: enforce [[nodes]] trailing comment rule (Task ID 0012)"
# PR 描述贴 docs/superpowers/specs/2026-09-23-nodes-comment-rule-design.md 路径
```

不 commit:本任务只是验证 + 触发 PR。

---

## Self-Review(对照 spec 章节,确认每条都有任务托底)

| Spec 章节 | 任务 | 状态 |
|---|---|---|
| §3 铁律 6 全文 | Task 1 Step 2(原文复制到 AGENTS.md) | ✅ |
| §3.1 表格 5 个维度 | Task 1 全条 + Task 2 §1 表行 §6 blockquote 引用 | ✅ |
| §4.1 AGENTS.md §5 末尾 | Task 1 | ✅ |
| §4.2 SCHEMA.md §1 节点表 +1 行 | Task 2 Step 2 | ✅ |
| §4.3 SCHEMA.md §6 +1 段 blockquote | Task 2 Step 5 | ✅ |
| §4.4 How-to-update-graph.md §1 表 +1 行 | Task 3 Step 2 | ✅ |
| §5 错误处理 3 类 | Task 4 Step 4 复核 | ✅ |
| §6.1 人肉测试 3 件 | Task 4 Step 3 | ✅ |
| §6.2 验收 7 条 A1–A7 | Task 4 Step 2 | ✅ |
| §7 YAGNI 6 项 | Task 4 Step 5 复核 | ✅ |
| §8 与既有规范 9 行 | Task 4 全程 + 各任务视觉自检 | ✅ |

无遗漏。零占位("TBD"/"TODO"/"待填")。所有代码块的方括号、引号、空格都注明需对齐。

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-23-nodes-comment-rule.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
