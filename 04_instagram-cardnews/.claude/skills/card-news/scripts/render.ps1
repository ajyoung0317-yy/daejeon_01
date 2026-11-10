# 카드뉴스 HTML을 1080x1350 PNG로 저장해요.
# 사용법:
#   powershell -ExecutionPolicy Bypass -File render.ps1 -Html "posts\07_제목\review.html"
#     → 같은 폴더에 01.png, 02.png ... 저장 (장 수는 <section class="card"> 개수로 자동 계산)
#   powershell -ExecutionPolicy Bypass -File render.ps1 -Html "...\review.html" -Check
#     → 가운데 기준선을 그린 확인용 카드를 _check\ 에 저장하고, 전체를 한 장에 모은 _check\sheet.png 를 만들어요
param(
  [Parameter(Mandatory = $true)][string]$Html,
  [int]$Count = 0,
  [switch]$Check
)

$ErrorActionPreference = "Stop"
$Html = (Resolve-Path $Html).Path
$dir  = Split-Path -Parent $Html

$chrome = @(
  "C:\Program Files\Google\Chrome\Application\chrome.exe",
  "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { throw "Chrome or Edge not found" }

if ($Count -le 0) {
  $Count = ([regex]::Matches([IO.File]::ReadAllText($Html, [Text.Encoding]::UTF8), '<section class="card')).Count
}

$out = $dir
$query = ""
if ($Check) {
  $out = Join-Path $dir "_check"
  New-Item -ItemType Directory -Force $out | Out-Null
  $query = "?guide"
}

# Chrome이 경고를 stderr로 내보내도 멈추지 않게 해요
$ErrorActionPreference = "Continue"
$url = ([System.Uri]$Html).AbsoluteUri
$files = @()
foreach ($i in 1..$Count) {
  $png = Join-Path $out ("{0:D2}.png" -f $i)
  & $chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 `
    --window-size=1080,1350 --virtual-time-budget=5000 `
    "--screenshot=$png" "$url$query#$i" 2>$null | Out-Null
  $files += $png
  Write-Host "saved $png"
}

if ($Check) {
  # 확인용: 모든 카드를 작게 줄여 한 장에 모아요 (한 줄에 5장)
  Add-Type -AssemblyName System.Drawing
  $cols = [Math]::Min(5, $Count); $rows = [Math]::Ceiling($Count / $cols)
  $w = 324; $h = 405; $gap = 12; $label = 34
  $sheet = New-Object System.Drawing.Bitmap ($cols * ($w + $gap) + $gap), ($rows * ($h + $gap + $label) + $gap)
  $g = [System.Drawing.Graphics]::FromImage($sheet)
  $g.Clear([System.Drawing.Color]::FromArgb(30, 30, 30))
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $font = New-Object System.Drawing.Font "Arial", 16, ([System.Drawing.FontStyle]::Bold)
  for ($k = 0; $k -lt $files.Count; $k++) {
    $img = [System.Drawing.Image]::FromFile($files[$k])
    $x = $gap + ($k % $cols) * ($w + $gap)
    $y = $gap + [Math]::Floor($k / $cols) * ($h + $gap + $label)
    $g.DrawString(("{0}" -f ($k + 1)), $font, [System.Drawing.Brushes]::White, $x, $y + 4)
    $g.DrawImage($img, $x, $y + $label, $w, $h)
    $img.Dispose()
  }
  $sheetPath = Join-Path $out "sheet.png"
  $sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $sheet.Dispose()
  Write-Host "sheet $sheetPath"
}
