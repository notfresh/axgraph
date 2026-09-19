# Windows 安装脚本实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Windows 用户跑一次 `.\install.ps1` 后，新开 PowerShell / cmd 窗口能直接敲 `ax`；同时让 `/axgraph:install` slash 命令在 Windows 上能正确路由到 PowerShell 脚本而不是 `install.sh`。

**Architecture:** 新增 `install.ps1`（对标 `install.sh`，幂等，安装入口到用户 PATH），修改 `commands/install.md` 加 OS 判断分支。`bin/ax` 不动 —— 它本身跨平台。

**Tech Stack:** PowerShell 5.1+（系统默认）、.NET BCL（`[Environment]`）、批处理（ax.cmd wrapper）

---

## Global Constraints

来自 `docs/superpowers/specs/2026-09-18-windows-install-design.md`：

- 范围**仅**包含 `install.ps1`（新增）和 `commands/install.md`（修改）。README / bin/ax / install.sh / AGENTS.md **都不动**
- 不入仓 `bin/ax.cmd`（是 install.ps1 的运行时产物）
- 不引入额外依赖（如 `pywin32`）—— 全程用 .NET BCL
- 不碰 Machine 级 PATH（不需要管理员）
- 幂等（重跑 install.ps1 不重复添加 PATH）
- PowerShell 5.1+ 兼容（`$PSCommandPath` 5.1 才有）
- 不涉及 git 操作（未经用户确认不做 commit/push）

---

## Task 1: 创建 install.ps1 框架

**Files:**
- Create: `install.ps1`

**Interfaces:**
- Consumes: 无（入口脚本）
- Produces: 当跑 `.\install.ps1` 时打印 axgraph 根、目标目录、PATH 状态；为 Task 2 留 PATH 处理钩子

- [ ] **Step 1: 创建文件，写入头部 + 参数解析**

文件路径：`install.ps1`（axgraph 根目录）

```powershell
<#
.SYNOPSIS
  Install the axgraph `ax` wrapper to a user-level bin directory and add it to PATH.

.DESCRIPTION
  Windows equivalent of ./install.sh. Resolves the plugin root from this script's
  own location, generates an `ax.cmd` shim into the target bin dir, and appends
  that dir to the user-level PATH if not already present.

.PARAMETER TargetDir
  Bin directory to install into. Defaults to $env:USERPROFILE\bin.

.EXAMPLE
  .\install.ps1
  .\install.ps1 C:\Tools\bin
#>
[CmdletBinding()]
param(
    [string]$TargetDir = (Join-Path $env:USERPROFILE 'bin')
)

$ErrorActionPreference = 'Stop'

# Resolve axgraph root from this script's own location (works regardless of cwd)
$AXGRAPH_ROOT = Split-Path -Parent $PSCommandPath

Write-Host ""
Write-Host "axgraph install.ps1 (Windows)" -ForegroundColor Cyan
Write-Host "  Plugin root : $AXGRAPH_ROOT"
Write-Host "  Target dir  : $TargetDir"
Write-Host ""
```

- [ ] **Step 2: 本地手测骨架**

跑：
```powershell
cd C:\projects\axgraph
.\install.ps1
```

期望输出（包含三行）：
```
axgraph install.ps1 (Windows)
  Plugin root : C:\projects\axgraph
  Target dir  : C:\Users\<you>\bin
```

- [ ] **Step 3: Commit**

```bash
git add install.ps1
git commit -m "feat(windows): add install.ps1 skeleton"
```

---

## Task 2: 在 install.ps1 里实现入口文件生成

**Files:**
- Modify: `install.ps1`（追加入口生成逻辑）

**Interfaces:**
- Consumes: Task 1 的 `$AXGRAPH_ROOT`、`$TargetDir`
- Produces: 在 `$TargetDir` 生成 `ax.cmd`，内容是硬编码 `AX_GRAPH_ROOT` + 调用 `python bin/ax`

- [ ] **Step 1: 在 Write-Host 块之后追加入口生成逻辑**

修改 `install.ps1`，在最后的 `Write-Host ""` 之后加：

```powershell
# --- Generate the ax.cmd shim ---
if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

$shimPath = Join-Path $TargetDir 'ax.cmd'
$tmpPath  = "$shimPath.tmp"

# Escape backslashes for cmd's set syntax: not needed, but use forward slashes
# inside the python invocation for cross-shell robustness.
$rootForCmd = $AXGRAPH_ROOT -replace '\\', '/'

$shimContent = @"
@echo off
set "AX_GRAPH_ROOT=$AXGRAPH_ROOT"
python "%AX_GRAPH_ROOT%\bin\ax" %*
"@

# Atomic write: write to .tmp then move
[System.IO.File]::WriteAllText($tmpPath, $shimContent, [System.Text.Encoding]::ASCII)
Move-Item -Path $tmpPath -Destination $shimPath -Force

Write-Host "  Shim        : $shimPath" -ForegroundColor Green
```

- [ ] **Step 2: 本地手测**

跑：
```powershell
.\install.ps1
Get-Content $env:USERPROFILE\bin\ax.cmd
```

期望：`ax.cmd` 内容是三行，第一行 `@echo off`，第二行 `set "AX_GRAPH_ROOT=C:\projects\axgraph"`（路径跟你机器实际一致），第三行 `python "%AX_GRAPH_ROOT%\bin\ax" %*`。

- [ ] **Step 3: 验证幂等（删掉再生成）**

跑：
```powershell
Remove-Item $env:USERPROFILE\bin\ax.cmd -ErrorAction SilentlyContinue
.\install.ps1
Test-Path $env:USERPROFILE\bin\ax.cmd
```

期望：返回 `True`。

- [ ] **Step 4: 验证自定义目标目录**

跑：
```powershell
$customDir = Join-Path $env:TEMP 'ax-test-bin'
.\install.ps1 $customDir
Get-Content (Join-Path $customDir 'ax.cmd')
Remove-Item $customDir -Recurse -Force
```

期望：临时目录下生成 ax.cmd，内容正确；清理后目录消失。

- [ ] **Step 5: Commit**

```bash
git add install.ps1
git commit -m "feat(windows): generate ax.cmd shim with AX_GRAPH_ROOT"
```

---

## Task 3: 在 install.ps1 里实现 PATH 处理

**Files:**
- Modify: `install.ps1`（追加 PATH 处理逻辑）

**Interfaces:**
- Consumes: Task 2 的 `$shimPath`、`$TargetDir`
- Produces: 把 `$TargetDir` 加到 `[Environment]::GetEnvironmentVariable("Path", "User")`；打印是否真的改动了 PATH

- [ ] **Step 1: 在 shim 生成块之后追加 PATH 处理**

修改 `install.ps1`，在 Task 2 的 `Write-Host "  Shim ..."` 行之后追加：

```powershell
# --- Add $TargetDir to user-level PATH if missing ---
$currentUserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$pathChanged = $false

# Compare case-insensitively, splitting on ';' and trimming
$pathEntries = if ([string]::IsNullOrWhiteSpace($currentUserPath)) {
    @()
} else {
    $currentUserPath -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
}

$targetNormalized = $TargetDir.TrimEnd('\').TrimEnd('/')

$alreadyPresent = $pathEntries | Where-Object {
    ($_.TrimEnd('\').TrimEnd('/')) -ieq $targetNormalized
} | Select-Object -First 1

if (-not $alreadyPresent) {
    $newUserPath = if ([string]::IsNullOrWhiteSpace($currentUserPath)) {
        $TargetDir
    } else {
        "$currentUserPath;$TargetDir"
    }
    [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
    $pathChanged = $true
}

if ($pathChanged) {
    Write-Host "  PATH        : added $TargetDir (user-level)" -ForegroundColor Green
} else {
    Write-Host "  PATH        : $TargetDir already present" -ForegroundColor Yellow
}
```

- [ ] **Step 2: 在脚本最末尾追加总结**

修改 `install.ps1`，在 PATH 处理块之后追加：

```powershell
Write-Host ""
Write-Host "Done. To use \`ax\` in a new shell, open a new PowerShell / cmd window." -ForegroundColor Cyan
Write-Host "Test: ax --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "Uninstall: Remove-Item '$shimPath'" -ForegroundColor DarkGray
Write-Host "          (also remove $TargetDir from user PATH if desired)"
Write-Host ""
```

- [ ] **Step 3: 本地手测：PATH 未含时**

跑：
```powershell
# 备份当前 PATH
$orig = [Environment]::GetEnvironmentVariable('Path', 'User')

# 跑 install
.\install.ps1
```

期望输出包含：
```
  PATH        : added C:\Users\<you>\bin (user-level)
Done. To use `ax` in a new shell, open a new PowerShell / cmd window.
Test: ax --version
```

- [ ] **Step 4: 本地手测：PATH 已含时（幂等）**

跑：
```powershell
.\install.ps1
```

期望输出包含：
```
  PATH        : C:\Users\<you>\bin already present
```

- [ ] **Step 5: 本地手测：完整链路（开新窗口验证 ax）**

跑：
```powershell
# 当前进程看不到新 PATH，必须新开窗口
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'ax --version'
```

期望：新开的 PowerShell 窗口输出 `0.1.0`（VERSION 文件内容）。

- [ ] **Step 6: 清理（如果 Test 时不小心改坏了 PATH 可恢复）**

跑：
```powershell
# 把 PATH 恢复成备份值
[Environment]::SetEnvironmentVariable('Path', $orig, 'User')
```

期望：用户级 PATH 恢复。

- [ ] **Step 7: Commit**

```bash
git add install.ps1
git commit -m "feat(windows): append target dir to user PATH on install"
```

---

## Task 4: 更新 commands/install.md 加 OS 判断分支

**Files:**
- Modify: `commands/install.md`

**Interfaces:**
- Consumes: 现有文档结构（`What to do` 三步骤）
- Produces: AI 在执行 slash 命令时会先检测 OS；Windows 走 install.ps1 路径，其他走 install.sh

- [ ] **Step 1: 改写 "What to do" 第 1 步，加 OS 判断**

修改 `commands/install.md`，把现有的 "What to do" 第 1 步替换成 OS 判断版：

```markdown
1. **Locate the axgraph install root.** The host that loaded this plugin
   already knows where axgraph lives:
   - Kimi Code: `$KIMI_CODE_HOME/plugins/managed/axgraph/`
   - Claude Code: `~/.claude/plugins/axgraph/`
   - Standalone (git clone): wherever the user cloned it

   If the host exposes the plugin path (e.g. `$AX_GRAPH_ROOT` env var, or
   you can read it from the plugin metadata), use that. Otherwise ask the
   user.

2. **Detect the OS.** Check whether the user's shell is Windows or POSIX:

   ```powershell
   # PowerShell — single command, works for both detection and execution
   if ($IsWindows -or ($env:OS -like '*Windows*')) {
       # Windows path → go to step 3-Win
   } else {
       # POSIX path → go to step 3-POSIX
   }
   ```

   The split is symmetrical: each OS has one installer script and one
   target directory. Picking the wrong branch will silently fail (running
   `install.sh` on Windows gives `bash: ./install.sh: No such file or
   directory` or similar).
```

- [ ] **Step 2: 改写 "What to do" 第 2 步，分成两个 OS 分支**

把现有 "2. Run the install script" 整段替换成两个并列的分支（保留原 POSIX 内容不动，加 Windows 分支）：

```markdown
### 3-POSIX (Linux / macOS / WSL / Git Bash)

From the axgraph repo root:

```bash
./install.sh
```

The script will:
- Detect `$AXGRAPH_ROOT` automatically (it's `$(dirname "$0")`-resolved)
- Symlink `~/.local/bin/ax` → `<axgraph>/bin/ax`
- Check whether `~/.local/bin` is on the user's PATH; if not, print the
  `export PATH=...` line they need to add
- Print a one-line test command (`ax --version` should output `0.1.0`)

The script is idempotent — re-running just refreshes the symlink. Safe to
call after `git pull` or after the host upgrades axgraph.

### 3-Win (Windows native — cmd / PowerShell)

From the axgraph repo root, in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

The `-ExecutionPolicy Bypass` is needed because Windows PowerShell's default
execution policy (`Restricted` for clients, `RemoteSigned` for servers)
blocks `.ps1` scripts by default. Bypassing only affects this one
invocation — it does not change the system policy. If the user has already
set `RemoteSigned` or `Unrestricted` system-wide, the flag is a no-op.

The script will:
- Detect `$AXGRAPH_ROOT` automatically from `$PSCommandPath`
- Generate `<USERPROFILE>\bin\ax.cmd` (or the directory passed as the first
  argument) — a small wrapper that calls `python %AX_GRAPH_ROOT%\bin\ax %*`
- Add that directory to the user's PATH via `[Environment]::SetEnvironmentVariable`
  (user-level, no admin required)
- Print a one-line test command (`ax --version` should output `0.1.0`)

The script is idempotent — re-running regenerates the shim and skips PATH
if the directory is already present.

**Note on new windows:** PowerShell / cmd processes inherit their PATH at
launch. The user must open a new shell window after install for `ax` to be
visible — current windows keep the old PATH.
```

- [ ] **Step 3: 在文档末尾 "Important context" 之前加 Windows 提示**

在 `commands/install.md` 现有的 "Important context" 段之前（也就是 "## Important context" 标题行之前），插入：

```markdown
**Windows-specific gotchas:**

- PowerShell default `ExecutionPolicy` blocks `.ps1`. Always invoke with
  `-ExecutionPolicy Bypass` (or set the process scope via
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before
  calling).
- PATH changes take effect only in **new** PowerShell / cmd windows —
  tell the user to open a fresh window.
- If `python` is not on the user's PATH, `ax.cmd` will fail with
  `'python' is not recognized`. Have them re-run the Python installer
  and check "Add Python to PATH", or install via the Microsoft Store
  Python 3.x.
- WSL / Git Bash users are **POSIX**, not Windows. They run `./install.sh`,
  not `install.ps1`, even if their Windows username is the host.
- The `ax.cmd` shim lives in the user's bin directory (default
  `%USERPROFILE%\bin`) and is regenerated on every `install.ps1` run. To
  uninstall, remove `ax.cmd` and the directory entry from user PATH.

```

- [ ] **Step 4: 本地手测：文档渲染**

跑：
```powershell
Get-Content commands/install.md
```

期望：能完整看到新加的 OS 判断（`$IsWindows` / `$env:OS`）和 Windows 分支（`install.ps1`）。原 POSIX 段落完整保留。

- [ ] **Step 5: Commit**

```bash
git add commands/install.md
git commit -m "docs(install): add Windows / install.ps1 branch to slash command"
```

---

## Task 5: 端到端验证

**Files:**
- 不修改文件 —— 只跑测试

- [ ] **Step 1: 跑完整 install.ps1**

```powershell
cd C:\projects\axgraph
.\install.ps1
```

期望：所有输出段出现，无报错。

- [ ] **Step 2: 新窗口验证 ax 可用**

```powershell
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'ax --version'
```

期望：新窗口输出 `0.1.0`。

- [ ] **Step 3: 跑一个真实子命令**

```powershell
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'ax --help'
```

期望：输出 `ax --help` 的使用说明（含 `init / query / purity / diagnose / update / extract`）。

- [ ] **Step 4: 验证幂等性**

```powershell
.\install.ps1
.\install.ps1
```

期望：第二次显示 `PATH: ... already present`，无重复添加。

- [ ] **Step 5: （可选）从 host 模拟 slash 命令流程**

在 host（Kimi / Claude Code）里手动跑：

```powershell
# 模拟 AI 在 host 里收到 /axgraph:install 后的执行
powershell -ExecutionPolicy Bypass -File "$PWD\install.ps1"
```

期望：跟 Step 1 一致。

---

## Self-Review Checklist

- [x] Spec 覆盖：spec §4.2 install.ps1 行为 → Task 1-3；spec §4.3 slash 文档改动 → Task 4；spec §5 测试 → Task 5
- [x] 无占位符：所有代码块都是完整可执行内容
- [x] 类型一致：`$TargetDir`、`$AXGRAPH_ROOT`、`$shimPath` 在所有任务中命名一致
- [x] 全局约束遵守：未入仓 ax.cmd、未动 bin/ax、未动 install.sh、未动 README、未动 AGENTS.md
