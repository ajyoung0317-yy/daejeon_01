param(
  [Parameter(Mandatory=$true)][string]$InDir,
  [Parameter(Mandatory=$true)][string]$OutDir,
  [Parameter(Mandatory=$true)][string[]]$Names,
  [int]$Tol = 14,
  [int]$Soft = 36
)
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class Cutout {
  static int Dist(byte[] p, int i){ return Math.Max(255-p[i], Math.Max(255-p[i+1], 255-p[i+2])); }
  public static void Run(string src, string dst, int tol, int soft){
    Bitmap orig = new Bitmap(src);
    int w = orig.Width, h = orig.Height;
    Bitmap bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
    using (Graphics g = Graphics.FromImage(bmp)) g.DrawImage(orig, 0, 0, w, h);
    orig.Dispose();
    Rectangle r = new Rectangle(0,0,w,h);
    BitmapData d = bmp.LockBits(r, ImageLockMode.ReadWrite, PixelFormat.Format32bppArgb);
    int stride = d.Stride; byte[] px = new byte[stride*h];
    Marshal.Copy(d.Scan0, px, 0, px.Length);
    bool[] bg = new bool[w*h];
    Queue<int> q = new Queue<int>();
    for (int x=0;x<w;x++){ q.Enqueue(x); q.Enqueue((h-1)*w+x); }
    for (int y=0;y<h;y++){ q.Enqueue(y*w); q.Enqueue(y*w+w-1); }
    while (q.Count>0){
      int k=q.Dequeue(); if (bg[k]) continue;
      int x=k%w, y=k/w; int i=y*stride+x*4;
      if (Dist(px,i) > tol) continue;
      bg[k]=true;
      if (x>0) q.Enqueue(k-1); if (x<w-1) q.Enqueue(k+1);
      if (y>0) q.Enqueue(k-w); if (y<h-1) q.Enqueue(k+w);
    }
    int minx=w,miny=h,maxx=0,maxy=0;
    for (int y=0;y<h;y++) for (int x=0;x<w;x++){
      int k=y*w+x, i=y*stride+x*4;
      if (bg[k]) { px[i+3]=0; continue; }
      bool edge=false;
      for (int dy=-2;dy<=2 && !edge;dy++) for (int dx=-2;dx<=2;dx++){
        int nx=x+dx, ny=y+dy; if (nx<0||ny<0||nx>=w||ny>=h) continue;
        if (bg[ny*w+nx]) { edge=true; break; }
      }
      if (edge){ int a = Math.Min(255, Dist(px,i)*255/soft); if (a<255) px[i+3]=(byte)Math.Max(a,0); }
      if (px[i+3]>0){ if(x<minx)minx=x; if(y<miny)miny=y; if(x>maxx)maxx=x; if(y>maxy)maxy=y; }
    }
    Marshal.Copy(px, 0, d.Scan0, px.Length);
    bmp.UnlockBits(d);
    int pad=6; minx=Math.Max(0,minx-pad); miny=Math.Max(0,miny-pad); maxx=Math.Min(w-1,maxx+pad); maxy=Math.Min(h-1,maxy+pad);
    Bitmap crop = bmp.Clone(new Rectangle(minx,miny,maxx-minx+1,maxy-miny+1), PixelFormat.Format32bppArgb);
    crop.Save(dst, ImageFormat.Png);
    crop.Dispose(); bmp.Dispose();
  }
}
"@
New-Item -ItemType Directory -Force $OutDir | Out-Null
foreach ($n in $Names) {
  $src = Join-Path $InDir "$n.jpg"; $dst = Join-Path $OutDir "$n.png"
  [Cutout]::Run((Resolve-Path $src).Path, [IO.Path]::GetFullPath($dst), $Tol, $Soft)
  "{0} -> {1} bytes" -f $n, (Get-Item $dst).Length
}
