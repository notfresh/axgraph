# Windows 安装脚本 (install.ps1) + slash 命令适配 设计

> 日期：2026-09-18
> 范围：新增 `install.ps1`，**更新 `commands/install.md` 让 slash 命令支持 OS 判断**。其他一律不动（README、bin/ax、bin/ax.cmd、AGENTS.md 都不动）。

## 1. 背景

`bin/ax` 是 Python 脚本，跨平台能跑。但用户从 Windows 新开 cmd / PowerShell 直接敲 `ax` 找不到 —— 因为：

- `install.sh` 是 bash，在 Windows 上不能直接跑
- Windows 没有 `~/.local/bin` 这个约定
- Windows 的用户级 PATH 在 `HKCU\Environment` 注册表里，`~/.bashrc` 那套不管用

另外，`commands/install.md` 当前只覆盖 Linux/macOS 视角的 `install.sh`。在 Windows 上跑 `/axgraph:install` slash 命令，AI 拿到这份文档只会执行 `install.sh`，导致 Windows 用户依然装不上。

## 2. 目标

1. Windows 用户跑一次 `.\install.ps1` 后，新开 PowerShell / cmd 窗口敲 `ax --version` 能正常工作。
2. Windows 用户在 host（Kimi / Claude Code）里调 `/axgraph:install` 时，AI 能识别 OS 并调用 `install.ps1`，不再死板跑 `install.sh`。

## 3. 非目标（明确不做）

- ❌ 不入仓 `bin/ax.cmd` —— 没有 install.ps1 时 Windows 原生 cmd 调不到 ax。接受这个限制（跟 install.sh 在 Linux 上的角色完全对称）
- ❌ 不更新 README.md 的 Windows 节
- ❌ 不改 AGENTS.md
- ❌ 不写 uninstall 脚本
- ❌ 不写 GitHub Actions 的 windows-latest job
- ❌ 不引入额外依赖（`pywin32` 等）—— 用 .NET BCL 的 `[Environment]::SetEnvironmentVariable`

## 4. 设计

### 4.1 文件清单

| 文件 | 状态 | 说明 |
|---|---|---|
| `install.ps1` | 新增 | PowerShell 安装脚本，对标 `install.sh` |
| `commands/install.md` | 修改 | 加 OS 判断分支 |
| `bin/ax` | 不动 | Python 主脚本本身跨平台 |
| `install.sh` | 不动 | POSIX 安装脚本 |

### 4.2 `install.ps1` 行为

幂等（重跑覆盖）。步骤：

1. **解析 axgraph 根**
   ```powershell
   $AXGRAPH_ROOT = Split-Path -Parent $PSCommandPath
   ```

2. **目标目录**：默认 `$env:USERPROFILE\bin`，第一个位置参数可覆盖（跟 `install.sh [DIR]` 一致）。

3. **生成入口文件** 到目标目录，调用 `bin/ax` Python 脚本（具体格式由实施时决定：cmd / PowerShell / 或两者的并集，但不入仓 —— 这是 install.ps1 的运行时产物，不在仓库里）。

4. **PATH 处理**
   - 读 `[Environment]::GetEnvironmentVariable("Path", "User")`
   - 判断目标目录是否在其中（不区分大小写）
   - 不在 → 用 `[Environment]::SetEnvironmentVariable("Path", "$existing;$dir", "User")` 追加
   - 在 → 跳过

5. **打印结果**：
   ```
   ✓ install.ps1: <入口文件> → <目标目录>
     Plugin root:  <axgraph 根>
     PATH updated: yes/no
     Open a new PowerShell / cmd window and run: ax --version
   ```
   明确提示用户**开新窗口**（已运行的 PowerShell 进程继承旧 PATH，必须重启）。

### 4.3 `commands/install.md` 改动

在现有 "What to do" 步骤里加 OS 判断：

- **第 1 步**：用 OS 信息判断。`$IsWindows` / `$env:OS` 含 `Windows` → Windows 分支；其他 → 现有 POSIX 流程。
- **新增 Windows 分支（步骤 2-Win）**：
  - PowerShell 调 `& "$AXGRAPH_ROOT\install.ps1"` （不用 `[DIR]` 默认 `$env:USERPROFILE\bin`）
  - 注意：**PowerShell 默认不允许执行 `.ps1`**。AI 在调之前应先 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`（仅当前进程生效，不影响系统策略），或者直接 `powershell -ExecutionPolicy Bypass -File ...`
- **保留原 POSIX 分支（步骤 2-POSIX）**：现有 `./install.sh` 流程不动
- 文档末尾加 "Important context" 一段，说明 Windows 与 POSIX 的对称关系和 PowerShell 执行策略注意事项

文档主体文字大部分保留 —— 只插一段分支判断 + Windows 步骤，不重写。

### 4.4 关键决策

- **不动 Git Bash / WSL 路径** —— 用户在 Git Bash 里调 `ax` 会走 `python bin/ax`（shebang），跟 Windows 原生入口不冲突
- **不碰 Machine 级 PATH** —— 不需要管理员权限
- **ExecutionPolicy 处理** —— 默认 `Restricted`，AI 调 install.ps1 必须显式 bypass；这是标准做法
- **失败模式**：
  - `python` 不在 PATH → 让入口文件调用失败自然报错
  - 没有写入权限 → PowerShell 自动抛错，不需要特判

## 5. 测试

手动验证（本期不做 CI）：

### 5.1 `install.ps1` 直接跑
1. Windows PowerShell 里 `cd` 到 axgraph 根
2. `.\install.ps1`
3. 检查目标目录的入口文件存在
4. `echo $env:Path` 看新路径是否已含目标目录
5. **新开 PowerShell 窗口**（重要！）
6. `ax --version` 应输出 `0.1.0`

### 5.2 `/axgraph:install` slash 命令（Windows host）
1. 在 Windows 上跑 Kimi / Claude Code
2. 在 host 里输入 `/axgraph:install`
3. AI 应识别 Windows，调 `powershell -ExecutionPolicy Bypass -File install.ps1`
4. 验证结果同上

### 5.3 边界用例
- 跑两次 install.ps1 → 应幂等（不重复添加 PATH）
- 删掉入口文件再跑 → 应重新生成
- 传第二个参数 `.\install.ps1 C:\other\bin` → 应装到那个目录
- POSIX 系统跑 `/axgraph:install` → 仍走原 `./install.sh` 流程（不回归）

## 6. 兼容性

| 场景 | 行为 |
|---|---|
| Windows 10/11 + PowerShell 5.1（系统默认） | 正常 |
| PowerShell 7+ (`pwsh`) | 正常 |
| 路径含空格 / 中文 | 正常（全程用引号） |
| Python 不在 PATH | 入口文件失败，提示安装 Python |
| 已经通过 Kimi/Claude Code 装了 axgraph | install.ps1 仍可独立跑，不冲突 |
| POSIX 系统（macOS / Linux） | `/axgraph:install` 走原 install.sh 路径 |

## 7. 实现顺序

1. 在 axgraph 根目录创建 `install.ps1`
2. 修改 `commands/install.md`，加 OS 分支
3. 本地手测（按第 5 节的两条路径）
4. 完事

不涉及 git 操作（按系统规则，未经用户确认不做 commit/push）。
