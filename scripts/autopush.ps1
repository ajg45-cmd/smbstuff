<#
  Gr8Trade export -> GitHub, on a schedule.

  Copies new session CSVs out of the export folder into the repo and pushes
  them, so that whatever machine Claude is running on already has the data.
  Run it once by hand to check it works, then register the scheduled task at
  the bottom of this file and stop thinking about it.

  Setup (once):
    1. Edit $ExportDir and $RepoDir below.
    2. powershell -ExecutionPolicy Bypass -File scripts\autopush.ps1
    3. If that pushed cleanly, register the task (command at the bottom).
#>

$ExportDir = "C:\gr8_export"
$RepoDir   = "C:\code\smbstuff"
$Branch    = "claude/ema9-hotkey-exit-strategy-fumaf3"
$DestRel   = "data\samples"

$ErrorActionPreference = "Stop"
function Log($m) { Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m) }

if (-not (Test-Path $ExportDir)) { Log "no export dir: $ExportDir"; exit 1 }
if (-not (Test-Path $RepoDir))   { Log "no repo dir: $RepoDir";     exit 1 }

$Dest = Join-Path $RepoDir $DestRel
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# Only files that changed, and never today's file while it is still being
# written -- a half-written session would look like a real one to the loader.
$today = (Get-Date).ToString("yyyyMMdd")
$files = Get-ChildItem -Path $ExportDir -Filter *.csv |
         Where-Object { $_.Name -notmatch $today -or (Get-Date).Hour -ge 17 }

$copied = 0
foreach ($f in $files) {
    $target = Join-Path $Dest $f.Name
    if ((-not (Test-Path $target)) -or
        ($f.LastWriteTimeUtc -gt (Get-Item $target).LastWriteTimeUtc)) {
        Copy-Item $f.FullName $target -Force
        $copied++
    }
}
Log "$copied file(s) staged from $($files.Count) export(s)"
if ($copied -eq 0) { Log "nothing new"; exit 0 }

Push-Location $RepoDir
try {
    git rev-parse --abbrev-ref HEAD | Out-Null
    git fetch origin $Branch 2>$null
    git checkout $Branch 2>$null
    git pull --rebase origin $Branch 2>$null

    git add -- "$DestRel/*.csv"
    if (-not (git diff --cached --name-only)) { Log "no tracked changes"; exit 0 }

    git commit -m "Gr8Trade export: $copied session file(s) $(Get-Date -Format yyyy-MM-dd)" | Out-Null

    $ok = $false
    foreach ($wait in 0, 2, 4, 8) {
        if ($wait) { Start-Sleep -Seconds $wait }
        git push origin $Branch 2>$null
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        Log "push failed, retrying in $([Math]::Max($wait * 2, 2))s"
    }
    Log $(if ($ok) { "pushed $copied file(s)" } else { "PUSH FAILED after retries" })
} finally { Pop-Location }

<#
  Register as a weekday task at 17:15 (after the close, so the day's file is
  complete). Run this line once, from an elevated PowerShell:

  schtasks /Create /TN "Gr8 export push" /SC WEEKLY /D MON,TUE,WED,THU,FRI ^
    /ST 17:15 /TR "powershell -ExecutionPolicy Bypass -File C:\code\smbstuff\scripts\autopush.ps1"

  Check it:   schtasks /Query /TN "Gr8 export push"
  Run it now: schtasks /Run   /TN "Gr8 export push"
  Remove it:  schtasks /Delete /TN "Gr8 export push" /F
#>
