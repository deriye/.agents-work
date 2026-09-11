#requires -version 5.1
# Rewrites OpenCode desktop .dat state files without a UTF-8 BOM and with LF
# line endings, so the app can parse them again (a BOM makes the app fall back
# to an empty project list and refuse to persist, dropping projects each launch).
# Content is preserved byte-for-byte except BOM removal and CRLF->LF.
# Run with OpenCode desktop FULLY CLOSED.
$ErrorActionPreference = 'Stop'
if (Get-Process OpenCode -ErrorAction SilentlyContinue) {
  Write-Host "ERROR: OpenCode is still running. Fully quit it and re-run." -ForegroundColor Red; exit 1
}
$dir = Join-Path $env:APPDATA 'ai.opencode.desktop'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$bak = Join-Path $env:LOCALAPPDATA "Temp\opencode\global-bom-fix-$stamp"
New-Item -ItemType Directory -Path $bak -Force | Out-Null

# Fix opencode.global.dat plus any opencode.window.*.dat that carry a BOM.
$targets = @()
$g = Join-Path $dir 'opencode.global.dat'
if (Test-Path $g) { $targets += $g }
Get-ChildItem $dir -Filter 'opencode.window.*.dat' -ErrorAction SilentlyContinue | ForEach-Object { $targets += $_.FullName }

foreach ($f in $targets) {
  $bytes = [System.IO.File]::ReadAllBytes($f)
  $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
  $name = Split-Path $f -Leaf
  if (-not $hasBom) { Write-Host ("SKIP (no BOM): " + $name) -ForegroundColor DarkGray; continue }

  Copy-Item $f (Join-Path $bak $name) -Force
  # strip BOM
  $noBom = New-Object byte[] ($bytes.Length - 3)
  [Array]::Copy($bytes, 3, $noBom, 0, $bytes.Length - 3)
  $text = [System.Text.Encoding]::UTF8.GetString($noBom)
  # normalize CRLF -> LF
  $text = $text -replace "`r`n", "`n"
  # write WITHOUT BOM
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($f, $text, $utf8NoBom)

  # verify
  $chk = [System.IO.File]::ReadAllBytes($f)
  $stillBom = ($chk.Length -ge 3 -and $chk[0] -eq 0xEF -and $chk[1] -eq 0xBB -and $chk[2] -eq 0xBF)
  $firstHex = ($chk[0..1] | ForEach-Object { $_.ToString('X2') }) -join ' '
  if ($stillBom) { Write-Host ("FAILED (BOM remains): " + $name) -ForegroundColor Red }
  else { Write-Host ("FIXED: " + $name + "  (now starts " + $firstHex + ")") -ForegroundColor Green }
}
Write-Host ""
Write-Host ("Backup: " + $bak) -ForegroundColor DarkGray
Write-Host "Done. Relaunch OpenCode desktop; your projects should persist now." -ForegroundColor Green
