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

# --- Generate the ax.cmd shim ---
if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

$shimPath = Join-Path $TargetDir 'ax.cmd'
$tmpPath  = "$shimPath.tmp"

$shimContent = @"
@echo off
set "AX_GRAPH_ROOT=$AXGRAPH_ROOT"
python "%AX_GRAPH_ROOT%\bin\ax" %*
"@

# Atomic write: write to .tmp then move
[System.IO.File]::WriteAllText($tmpPath, $shimContent, [System.Text.Encoding]::ASCII)
Move-Item -Path $tmpPath -Destination $shimPath -Force

Write-Host "  Shim        : $shimPath" -ForegroundColor Green

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

Write-Host ""
Write-Host "Done. To use \`ax\` in a new shell, open a new PowerShell / cmd window." -ForegroundColor Cyan
Write-Host "Test: ax --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "Uninstall: Remove-Item '$shimPath'" -ForegroundColor DarkGray
Write-Host "          (also remove $TargetDir from user PATH if desired)"
Write-Host ""
