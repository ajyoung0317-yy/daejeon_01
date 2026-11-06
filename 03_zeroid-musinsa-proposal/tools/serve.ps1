param([int]$Port = 8765, [string]$Root = (Split-Path $PSScriptRoot -Parent))
$types = @{ '.html'='text/html; charset=utf-8'; '.png'='image/png'; '.jpg'='image/jpeg'; '.css'='text/css'; '.js'='text/javascript'; '.pdf'='application/pdf' }
$l = New-Object System.Net.HttpListener
$l.Prefixes.Add("http://localhost:$Port/")
$l.Start()
Write-Host "Serving $Root on http://localhost:$Port/"
while ($l.IsListening) {
  $ctx = $l.GetContext()
  $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
  if ($rel -eq '') { $rel = 'zeroid_musinsa_proposal.html' }
  $path = [IO.Path]::GetFullPath((Join-Path $Root $rel))
  if ($path.StartsWith($Root) -and (Test-Path $path -PathType Leaf)) {
    $bytes = [IO.File]::ReadAllBytes($path)
    $t = $types[[IO.Path]::GetExtension($path)]; if (-not $t) { $t = 'application/octet-stream' }
    $ctx.Response.ContentType = $t
    $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  } else { $ctx.Response.StatusCode = 404 }
  $ctx.Response.Close()
}
