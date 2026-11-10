# 게시물 폴더에 넣은 원본 사진(한글 파일명)을 images\ 에 영문 이름으로 복사해요. 원본은 그대로 둬요.
# 사용법:
#   powershell -ExecutionPolicy Bypass -File prep_images.ps1 -Folder "posts\07_제목_리뷰"
#   powershell -ExecutionPolicy Bypass -File prep_images.ps1 -Folder "..." -Prefix m   (개봉작 스틸컷은 m, 포스터는 p)
# 긴 변이 1600px보다 큰 jpg/png는 1600px로 줄여요. webp 등 다른 형식은 그대로 복사해요.
# images\ 에 이미 r1, r2 … 가 있으면 다음 번호부터 이어서 붙여요. 마지막에 "원본 -> 새 이름" 표를 보여 줘요.
# 사진을 나중에 더 넣었다면 새 사진만 따로 폴더에 두고 돌리거나, 직접 복사해요(다시 돌리면 전부 또 복사돼요).
param(
  [Parameter(Mandatory = $true)][string]$Folder,
  [string]$Prefix = "r",
  [int]$MaxSide = 1600
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
$Folder = (Resolve-Path $Folder).Path
$dest = Join-Path $Folder "images"
New-Item -ItemType Directory -Force $dest | Out-Null

$exts = ".jpg", ".jpeg", ".png", ".webp"
$src = Get-ChildItem -File $Folder | Where-Object { $exts -contains $_.Extension.ToLower() -and $_.Name -notmatch '^\d+(_\w+)?\.png$' } | Sort-Object Name

$n = 1
while (Get-ChildItem $dest -Filter "$Prefix$n.*" -ErrorAction SilentlyContinue) { $n++ }

foreach ($f in $src) {
  $ext = $f.Extension.ToLower(); if ($ext -eq ".jpeg") { $ext = ".jpg" }
  $name = "$Prefix$n$ext"
  $target = Join-Path $dest $name
  if ($ext -eq ".jpg" -or $ext -eq ".png") {
    $img = [System.Drawing.Image]::FromFile($f.FullName)
    $scale = [Math]::Min(1.0, $MaxSide / [Math]::Max($img.Width, $img.Height))
    if ($scale -lt 1.0) {
      $bw = [int]($img.Width * $scale); $bh = [int]($img.Height * $scale)
      $bmp = New-Object System.Drawing.Bitmap $bw, $bh
      $g = [System.Drawing.Graphics]::FromImage($bmp)
      $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $g.DrawImage($img, 0, 0, $bw, $bh)
      $img.Dispose()
      if ($ext -eq ".jpg") {
        $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
        $p = New-Object System.Drawing.Imaging.EncoderParameters 1
        $p.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 90L
        $bmp.Save($target, $codec, $p)
      } else { $bmp.Save($target, [System.Drawing.Imaging.ImageFormat]::Png) }
      $g.Dispose(); $bmp.Dispose()
    } else { $img.Dispose(); Copy-Item $f.FullName $target }
  } else { Copy-Item $f.FullName $target }
  Write-Host ("{0}  ->  images\{1}" -f $f.Name, $name)
  $n++
}
if (-not $src) { Write-Host "no photos found in $Folder" }
