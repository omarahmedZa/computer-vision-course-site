import re
from pathlib import Path

def insert_before(text, marker, block, name):
    if marker not in text:
        raise SystemExit(f'{name}: marker not found: {marker[:40]}')
    return text.replace(marker, block + '\n' + marker)

base = Path('lessons')

# Lesson 2
p = base/'002-geometric-transformations-warping.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="warp-anim" width="720" height="200" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls">
    <label>Angle° <input id="wa-a" type="range" min="-45" max="45" step="1" value="20"></label>
    <label>Shear <input id="wa-k" type="range" min="-0.6" max="0.6" step="0.05" value="0.2"></label>
    <label>Scale <input id="wa-s" type="range" min="0.6" max="1.4" step="0.05" value="1"></label>
    <button id="wa-play" type="button">Play</button>
  </div>
  <figcaption><strong>Transforming coordinates (animation/interaction).</strong> A grid deforms under an affine matrix; inverse mapping would sample the original for every output pixel to avoid holes.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('warp-anim'); if(!c) return; var x=c.getContext('2d'), t=0, play=false, raf;
  function draw(){
    var a=+document.getElementById('wa-a').value*Math.PI/180 + (play?Math.sin(t)*0.25:0);
    var k=+document.getElementById('wa-k').value, s=+document.getElementById('wa-s').value;
    var ca=Math.cos(a), sa=Math.sin(a);
    var M=[s*ca, s*(k*ca-sa), 80, s*sa, s*(k*sa+ca), 20];
    x.clearRect(0,0,720,200);
    function map(px,py){return [M[0]*px+M[1]*py+M[2]+120, 160-(M[3]*px+M[4]*py+M[5])];}
    x.strokeStyle='rgba(120,120,120,0.4)';
    for(var i=0;i<=5;i++){ x.beginPath(); for(var j=0;j<=5;j++){var p=map(i*20,j*20); if(j==0)x.moveTo(p[0],p[1]); else x.lineTo(p[0],p[1]);} x.stroke(); }
    for(var j=0;j<=5;j++){ x.beginPath(); for(var i=0;i<=5;i++){var p=map(i*20,j*20); if(i==0)x.moveTo(p[0],p[1]); else x.lineTo(p[0],p[1]);} x.stroke(); }
    x.strokeStyle='rgba(163,35,31,0.9)'; x.lineWidth=2; x.beginPath();
    [[0,0],[100,0],[100,100],[0,100],[0,0]].forEach(function(pt,i){var p=map(pt[0],pt[1]); if(i==0)x.moveTo(p[0],p[1]); else x.lineTo(p[0],p[1]);}); x.stroke(); x.lineWidth=1;
    x.fillStyle=getComputedStyle(document.body).color; x.font='12px ui-monospace,monospace';
    x.fillText('Affine map M (linear + translation). Inverse: for each output (x\',y\') sample input at M^{-1}(x\',y\').', 20, 190);
    if(play){t+=0.03; raf=requestAnimationFrame(draw);}
  }
  ['wa-a','wa-k','wa-s'].forEach(function(id){document.getElementById(id).addEventListener('input',draw);});
  document.getElementById('wa-play').addEventListener('click',function(){play=!play; this.textContent=play?'Pause':'Play'; if(play) draw();});
  draw();
})();
</script>
'''
# insert after forward/inverse explanation paragraph
t = insert_before(t, '<h3>4) Interpolation (resampling)</h3>', vis, 'L2 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. This shows homogeneous transforms, forward vs inverse warping, and nearest/bilinear interpolation on a synthetic image.</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

# Synthetic image
H, W = 80, 100
yy, xx = np.mgrid[0:H, 0:W]
img = np.zeros((H,W), np.float32)
img[(xx//10 + yy//10) % 2 == 0] = 200
img[(xx//10 + yy//10) % 2 == 1] = 60
img[20:50, 30:70] += 40
img = np.clip(img, 0, 255)

def make_M(angle_deg=20, tx=10, ty=5, sx=1.0, sy=1.0, shear=0.2):
    a = np.deg2rad(angle_deg); c,sn = np.cos(a), np.sin(a)
    R = np.array([[c,-sn,0],[sn,c,0],[0,0,1]])
    S = np.array([[sx,0,0],[0,sy,0],[0,0,1]])
    Sh= np.array([[1,shear,0],[0,1,0],[0,0,1]])
    T = np.array([[1,0,tx],[0,1,ty],[0,0,1]])
    return T @ R @ S @ Sh  # apply Sh,S,R,T in that order to point

def sample(img, x, y, mode='bilinear'):
    H,W = img.shape
    if mode == 'nearest':
        xi = np.clip(np.rint(x).astype(int), 0, W-1)
        yi = np.clip(np.rint(y).astype(int), 0, H-1)
        return img[yi, xi]
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = x0+1; y1 = y0+1
    x0c,x1c = np.clip(x0,0,W-1), np.clip(x1,0,W-1)
    y0c,y1c = np.clip(y0,0,H-1), np.clip(y1,0,H-1)
    wa = (x1-x)*(y1-y); wb = (x-x0)*(y1-y); wc = (x1-x)*(y-y0); wd = (x-x0)*(y-y0)
    Ia = img[y0c,x0c]; Ib = img[y0c,x1c]; Ic = img[y1c,x0c]; Id = img[y1c,x1c]
    return wa*Ia + wb*Ib + wc*Ic + wd*Id

M = make_M(angle_deg=25, tx=5, ty=0, shear=0.15)
Minv = np.linalg.inv(M)

# Forward warping (demonstrates holes)
fwd = np.full_like(img, np.nan)
H,W = img.shape
ys, xs = np.mgrid[0:H,0:W]
ones = np.ones_like(xs)
coords = np.stack([xs,ys,ones], axis=0).reshape(3,-1)
dst = (M @ coords)
xd = np.rint(dst[0]/dst[2]).astype(int); yd = np.rint(dst[1]/dst[2]).astype(int)
for i in range(xs.size):
    xdi, ydi = xd[i], yd[i]
    if 0 <= xdi < W and 0 <= ydi < H:
        fwd[ydi, xdi] = img.flat[i]

# Inverse warping
inv_nn = np.zeros_like(img); inv_bl = np.zeros_like(img)
Xd, Yd = np.mgrid[0:H,0:W]
ones = np.ones_like(Xd)
dst = np.stack([Xd,Yd,ones], axis=0).reshape(3,-1)
src = (Minv @ dst)
xs_s = src[0]/src[2]; ys_s = src[1]/src[2]
valid = (xs_s>=0)&(xs_s<=W-1)&(ys_s>=0)&(ys_s<=H-1)
inv_nn.flat[valid] = sample(img, xs_s[valid], ys_s[valid], 'nearest')
inv_bl.flat[valid] = sample(img, xs_s[valid], ys_s[valid], 'bilinear')

fig,axs = plt.subplots(1,4,figsize=(14,3.5))
axs[0].imshow(img,cmap='gray',vmin=0,vmax=255); axs[0].set_title('Source')
axs[1].imshow(np.nan_to_num(fwd,nan=30),cmap='gray',vmin=0,vmax=255); axs[1].set_title('Forward (holes)')
axs[2].imshow(inv_nn,cmap='gray',vmin=0,vmax=255); axs[2].set_title('Inverse + nearest')
axs[3].imshow(inv_bl,cmap='gray',vmin=0,vmax=255); axs[3].set_title('Inverse + bilinear')
for a in axs: a.axis('off')
plt.tight_layout(); plt.show()

# Composition order demo
p = np.array([1,0,1.0])
T = np.array([[1,0,3],[0,1,0],[0,0,1]])
R = np.array([[0,-1,0],[1,0,0],[0,0,1]]) # 90 deg
print('T then R:', (R@T@p)[:2], '  R then T:', (T@R@p)[:2])
</code></pre>
<p><strong>Try in Colab:</strong> replace the affine matrix with a homography (set bottom row to [h31,h32,1] and divide by w), or warp a real image with <code>plt.imread</code>.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L2 py')
p.write_text(t)

# Lesson 3
p = base/'003-corner-and-blob-detection.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="blob-scale" width="720" height="170" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls">
    <label>Blob radius <input id="bs-r" type="range" min="3" max="30" step="1" value="10"></label>
    <label>LoG σ <input id="bs-s" type="range" min="1" max="20" step="0.5" value="6"></label>
    <output id="bs-o"></output>
  </div>
  <figcaption><strong>Scale selection intuition.</strong> A blob produces the strongest center-surround (LoG/DoG) response when filter scale σ matches its characteristic size.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('blob-scale'); if(!c) return; var x=c.getContext('2d');
  function draw(){
    var r=+document.getElementById('bs-r').value, s=+document.getElementById('bs-s').value;
    document.getElementById('bs-o').textContent='radius='+r+', σ='+s.toFixed(1);
    x.clearRect(0,0,720,170);
    var cx=140,cy=85; for(var yy=0;yy<170;yy++) for(var xx=0;xx<280;xx++){ var d=Math.hypot(xx-cx,yy-cy); var v=d<r?40:220; x.fillStyle='rgb('+v+','+v+','+v+')'; x.fillRect(xx,yy,1,1); }
    x.fillStyle=getComputedStyle(document.body).color; x.font='12px ui-monospace,monospace'; x.fillText('blob', 110, 160);
    // response curve across sigma for given radius
    x.strokeStyle='rgba(120,120,120,0.5)'; x.strokeRect(320,20,360,120);
    x.beginPath(); var peakS=r/1.4;
    for(var i=0;i<=100;i++){ var sig=1+i*0.19; var resp=Math.exp(-Math.pow(Math.log(sig/(peakS||1)),2)/0.18); var px=320+i*3.6, py=140-resp*110; if(i==0)x.moveTo(px,py); else x.lineTo(px,py); }
    x.strokeStyle='rgba(163,35,31,0.9)'; x.stroke();
    var rx=320+((s-1)/19)*360, ry=140-Math.exp(-Math.pow(Math.log(s/(peakS||1)),2)/0.18)*110;
    x.fillStyle='rgba(31,95,122,0.9)'; x.beginPath(); x.arc(rx,ry,5,0,Math.PI*2); x.fill();
    x.fillStyle=getComputedStyle(document.body).color; x.fillText('response vs σ (peak near blob scale)', 360, 160);
  }
  ['bs-r','bs-s'].forEach(function(id){document.getElementById(id).addEventListener('input',draw);}); draw();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L3 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. Computes image gradients, a Harris corner response (with NMS), and a simple multi-scale blob response (LoG approximation).</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

# Synthetic image: corners, edges, blobs
H,W = 120,160
img = np.ones((H,W), np.float32)*40
img[20:90,20:70] = 220
img[40:100,90:140] = 220
yy,xx = np.mgrid[0:H,0:W]
for (cy,cx,r,val) in [(30,120,6,20),(80,40,12,20),(60,130,18,240)]:
    img[(yy-cy)**2 + (xx-cx)**2 < r*r] = val
img = np.clip(img,0,255)

def conv2(img,k):
    kh,kw=k.shape; ph,pw=kh//2,kw//2
    p=np.pad(img,((ph,ph),(pw,pw)),mode='edge'); out=np.zeros_like(img,np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            out[i,j]=np.sum(p[i:i+kh,j:j+kw]*k)
    return out

sobelx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]],np.float32)
sobely = np.array([[-1,-2,-1],[0,0,0],[1,2,1]],np.float32)
Ix = conv2(img, sobelx); Iy = conv2(img, sobely)

# Harris
Ixx,Iyy,Ixy = Ix*Ix, Iy*Iy, Ix*Iy
box = np.ones((3,3),np.float32)
Sxx,Syy,Sxy = conv2(Ixx,box), conv2(Iyy,box), conv2(Ixy,box)
k=0.05
det = Sxx*Syy - Sxy*Sxy
trace = Sxx+Syy
R = det - k*(trace**2)

# NMS
th = 0.1*R.max()
corners = np.zeros_like(R,bool)
for i in range(1,H-1):
    for j in range(1,W-1):
        if R[i,j]>th and R[i,j]==R[i-1:i+2,j-1:j+2].max():
            corners[i,j]=True

# Simple blob response: Laplacian of Gaussian approximation (LoG kernel) over scales
def log_kernel(sigma, size=None):
    if size is None: size = int(6*sigma+1)|1
    r = size//2; y,x = np.mgrid[-r:r+1,-r:r+1]
    s2=sigma*sigma
    k = (x*x + y*y - 2*s2)/(s2*s2) * np.exp(-(x*x+y*y)/(2*s2))
    return k - k.mean()

scales=[2,4,6,8,10]
responses=[conv2(img, log_kernel(s)) for s in scales]
stack = np.stack([np.abs(r) for r in responses], axis=0)
best = stack.max(axis=0)

fig,axs = plt.subplots(2,3,figsize=(13,7))
axs[0,0].imshow(img,cmap='gray'); axs[0,0].set_title('Image')
mag = np.sqrt(Ix*Ix+Iy*Iy)
axs[0,1].imshow(mag,cmap='magma'); axs[0,1].set_title('Gradient magnitude')
axs[0,2].imshow(R,cmap='RdBu_r'); axs[0,2].scatter(np.where(corners)[1],np.where(corners)[0],s=10,c='cyan'); axs[0,2].set_title('Harris R + NMS')
axs[1,0].imshow(np.abs(responses[1]),cmap='viridis'); axs[1,0].set_title('LoG response (σ=4)')
axs[1,1].imshow(np.abs(responses[3]),cmap='viridis'); axs[1,1].set_title('LoG response (σ=8)')
axs[1,2].imshow(best,cmap='viridis'); axs[1,2].set_title('Max over scales')
for a in axs.ravel(): a.axis('off')
plt.tight_layout(); plt.show()
</code></pre>
<p><strong>Try in Colab:</strong> adjust <code>k</code>/threshold, use Gaussian weighting in M, or find local extrema across (x,y,σ) in <code>stack</code> for true scale-space blob detection.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L3 py')
p.write_text(t)

# Lesson 4
p = base/'004-sift-feature-detectors-descriptors.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="sift-anim" width="720" height="180" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls"><button id="sift-play" type="button">Play orientation/descriptor steps</button> <output id="sift-o"></output></div>
  <figcaption><strong>SIFT stages (animated).</strong> Detect at scale, assign dominant orientation, then pool gradient orientations into spatial histograms (descriptor).</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('sift-anim'); if(!c) return; var x=c.getContext('2d'), step=0, play=false, raf, tick=0;
  function draw(){
    x.clearRect(0,0,720,180);
    var labels=['1) Scale-space extremum','2) Canonical orientation','3) 4x4 cells × 8-bin histograms'];
    document.getElementById('sift-o').textContent=labels[step];
    x.fillStyle=getComputedStyle(document.body).color; x.font='13px ui-monospace,monospace'; x.fillText(labels[step],20,20);
    // patch
    x.strokeStyle='rgba(120,120,120,0.6)'; x.strokeRect(40,40,100,100);
    x.fillStyle='rgba(31,95,122,0.15)'; x.beginPath(); x.arc(90,90,18,0,Math.PI*2); x.fill();
    if(step>=1){ x.strokeStyle='rgba(163,35,31,0.9)'; x.lineWidth=2; x.beginPath(); x.moveTo(90,90); x.lineTo(130,60); x.stroke(); x.lineWidth=1; x.fillText('dominant orientation', 150, 70); }
    // hist grid
    var ox=260; x.strokeStyle='rgba(120,120,120,0.5)';
    for(var i=0;i<=4;i++){ x.beginPath(); x.moveTo(ox+i*30,40); x.lineTo(ox+i*30,160); x.stroke(); x.beginPath(); x.moveTo(ox,40+i*30); x.lineTo(ox+120,40+i*30); x.stroke(); }
    if(step>=2){
      for(var r=0;r<4;r++) for(var cc=0;cc<4;cc++){
        var cx=ox+cc*30+15, cy=40+r*30+15;
        for(var b=0;b<8;b++){ var ang=b*Math.PI/4; var len=4+((r*3+cc+b)%5)*2; x.strokeStyle='rgba(163,35,31,0.7)'; x.beginPath(); x.moveTo(cx,cy); x.lineTo(cx+Math.cos(ang)*len, cy+Math.sin(ang)*len); x.stroke(); }
      }
      x.fillStyle=getComputedStyle(document.body).color; x.fillText('→ 128-D normalized descriptor', 420, 100);
    }
    if(play){ tick++; if(tick%50==0) step=(step+1)%3; raf=requestAnimationFrame(draw); }
  }
  document.getElementById('sift-play').addEventListener('click',function(){play=!play; this.textContent=play?'Pause':'Play orientation/descriptor steps'; if(play){tick=0; draw();}});
  draw();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L4 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. This demo shows DoG scale-space extrema (simplified), orientation histograms, a toy 128-D SIFT-like descriptor, and ratio-test matching.</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

def gaussian_kernel(s, size=None):
    if size is None: size=int(6*s+1)|1
    r=size//2; y,x=np.mgrid[-r:r+1,-r:r+1]
    k=np.exp(-(x*x+y*y)/(2*s*s)); return k/k.sum()

def conv2(img,k):
    kh,kw=k.shape; ph,pw=kh//2,kw//2
    p=np.pad(img,((ph,ph),(pw,pw)),mode='edge'); out=np.zeros_like(img,np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]): out[i,j]=np.sum(p[i:i+kh,j:j+kw]*k)
    return out

# Synthetic image
H,W=96,96
yy,xx=np.mgrid[0:H,0:W]
img=np.full((H,W),60,np.float32)
img[20:70,25:40]=200; img[30:45,35:75]=200
img[(yy-70)**2+(xx-70)**2<10*10]=220

# DoG pyramid (one octave, few scales)
sigmas=[1.0,1.6,2.56,4.096]
Gs=[conv2(img, gaussian_kernel(s)) for s in sigmas]
DoGs=[Gs[i+1]-Gs[i] for i in range(len(Gs)-1)]

# Simplified keypoint: extrema in middle DoG
D=DoGs[1]; prevD, nextD=DoGs[0], DoGs[2]
kps=[]
for i in range(1,H-1):
    for j in range(1,W-1):
        patch=np.stack([prevD[i-1:i+2,j-1:j+2], D[i-1:i+2,j-1:j+2], nextD[i-1:i+2,j-1:j+2]])
        v=D[i,j]
        if v==patch.max() and v>5: kps.append((i,j))
        if v==patch.min() and v<-5: kps.append((i,j))

# Gradients for orientation/descriptor
sobelx=np.array([[-1,0,1],[-2,0,2],[-1,0,1]],np.float32)
sobely=np.array([[-1,-2,-1],[0,0,0],[1,2,1]],np.float32)
Ix=conv2(Gs[1],sobelx); Iy=conv2(Gs[1],sobely)
mag=np.sqrt(Ix*Ix+Iy*Iy); ori=(np.arctan2(Iy,Ix)+2*np.pi)%(2*np.pi)

def descriptor(i,j):
    # toy 4x4 cells x 8 bins = 128
    desc=np.zeros(128,np.float32)
    for cy in range(4):
        for cx in range(4):
            y0=i-8+cy*4; x0=j-8+cx*4
            hist=np.zeros(8,np.float32)
            for dy in range(4):
                for dx in range(4):
                    y=y0+dy; x=x0+dx
                    if y<0 or x<0 or y>=H or x>=W: continue
                    b=int((ori[y,x]/(2*np.pi))*8)%8
                    hist[b]+=mag[y,x]
            desc[(cy*4+cx)*8:(cy*4+cx+1)*8]=hist
    n=np.linalg.norm(desc)+1e-6; desc/=n
    desc=np.clip(desc,0,0.2); desc/= (np.linalg.norm(desc)+1e-6)
    return desc

# Take a keypoint and create a "second image" rotated/shifted version of its patch conceptually
if not kps: kps=[(40,32),(70,70)]
p=kps[0]; d1=descriptor(p[0],p[1])
# simulate match candidate: similar vs different
d2=d1.copy(); d2[::3]*=0.9; d2/=np.linalg.norm(d2)+1e-6
d3=np.random.rand(128).astype(np.float32); d3/=np.linalg.norm(d3)
def l2(a,b): return np.linalg.norm(a-b)
dist12=l2(d1,d2); dist13=l2(d1,d3)
ratio = min(dist12,dist13)/max(dist12,dist13)

fig,axs=plt.subplots(1,3,figsize=(13,4))
axs[0].imshow(img,cmap='gray'); axs[0].scatter([p[1] for p in kps],[p[0] for p in kps],s=12,c='cyan'); axs[0].set_title('DoG keypoints (simplified)')
axs[1].imshow(DoGs[1],cmap='RdBu_r'); axs[1].set_title('DoG response')
axs[2].bar(np.arange(128),d1,width=1.0); axs[2].set_title('Toy 128-D descriptor')
for a in axs[:2]: a.axis('off')
plt.tight_layout(); plt.show()
print('dist(similar)=%.3f dist(different)=%.3f ratio=%.3f' % (dist12,dist13,ratio))
</code></pre>
<p><strong>Try in Colab:</strong> implement full 26-neighbor extrema, add subpixel localization/contrast filtering, compute dominant orientation from a real gradient histogram, and use OpenCV <code>cv2.SIFT_create()</code> to compare.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L4 py')
p.write_text(t)

# Lesson 5
p = base/'005-model-fitting-hough-ransac.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="ransac-anim" width="720" height="200" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls"><button id="ra-step" type="button">RANSAC iteration</button> <button id="ra-reset" type="button">Reset</button> <output id="ra-o"></output></div>
  <figcaption><strong>RANSAC animation.</strong> Each iteration samples 2 points, fits a line, and counts inliers. The best consensus model (thick) wins over outliers.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('ransac-anim'); if(!c) return; var x=c.getContext('2d'), pts=[], best=null, it=0;
  function gen(){ pts=[]; for(var i=0;i<18;i++){var px=40+i*34; pts.push({x:px,y:150-0.35*px+(Math.random()*8-4),inl:true});}
    for(var i=0;i<7;i++) pts.push({x:40+Math.random()*620,y:20+Math.random()*150,inl:false}); best=null; it=0; draw(); }
  function fit(a,b){var A=b.y-a.y,B=a.x-b.x,C=b.x*a.y-a.x*b.y;var n=Math.hypot(A,B)||1;return{A:A/n,B:B/n,C:C/n,a:a,b:b};}
  function dist(m,p){return Math.abs(m.A*p.x+m.B*p.y+m.C);} 
  function step(){ if(pts.length<2) return; var i=(Math.random()*pts.length)|0,j=(Math.random()*pts.length)|0; if(i==j) j=(j+1)%pts.length; var m=fit(pts[i],pts[j]); var inl=pts.filter(function(p){return dist(m,p)<10;}); it++; if(!best||inl.length>best.inl.length) best={m:m,inl:inl}; draw(m,inl); }
  function draw(cur,curInl){ x.clearRect(0,0,720,200);
    function line(m,col,w){x.strokeStyle=col;x.lineWidth=w; x.beginPath(); for(var px=0;px<720;px+=4){var py=-(m.A*px+m.C)/(m.B||1e-6); if(px==0)x.moveTo(px,py); else x.lineTo(px,py);} x.stroke(); x.lineWidth=1;}
    if(best) line(best.m,'rgba(31,95,122,0.5)',5); if(cur) line(cur,'rgba(163,35,31,0.5)',1.5);
    pts.forEach(function(p){var isB=best&&best.inl.indexOf(p)>=0, isC=curInl&&curInl.indexOf(p)>=0; x.fillStyle=isB?'#1f5f7a':(isC?'#a3231f':'#888'); x.beginPath(); x.arc(p.x,p.y,3.5,0,Math.PI*2); x.fill();});
    document.getElementById('ra-o').textContent='iter '+it+(best?('  best inliers '+best.inl.length+'/'+pts.length):'');
  }
  document.getElementById('ra-step').addEventListener('click',step); document.getElementById('ra-reset').addEventListener('click',gen); gen();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L5 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. Implements a simple Hough line accumulator and RANSAC line fitting on noisy points with outliers.</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

# Generate points: inliers on a line + outliers
rng = np.random.default_rng(0)
x = np.linspace(0, 10, 30)
y_true = 0.6*x + 1.5
y_in = y_true + rng.normal(0, 0.25, size=x.size)
x_out = rng.uniform(0,10,12); y_out = rng.uniform(0,8,12)
X = np.concatenate([x, x_out]); Y = np.concatenate([y_in, y_out])

# --- Hough transform (rho = x cosθ + y sinθ) ---
thetas = np.deg2rad(np.arange(-90, 90))
diag = int(np.ceil(np.hypot(X.max()-X.min(), Y.max()-Y.min()))) + 10
rhos = np.arange(-diag, diag+1)
acc = np.zeros((len(rhos), len(thetas)), dtype=np.int32)
for xi, yi in zip(X,Y):
    rho_vals = (xi*np.cos(thetas) + yi*np.sin(thetas)).astype(int)
    for ti, r in enumerate(rho_vals):
        ri = r + diag
        if 0 <= ri < len(rhos): acc[ri, ti] += 1
peak = np.unravel_index(np.argmax(acc), acc.shape)
rho_p, theta_p = rhos[peak[0]], thetas[peak[1]]

# --- RANSAC line fit (y = m*x + c form for demo) ---
def fit_line(p1, p2):
    (x1,y1),(x2,y2)=p1,p2
    if abs(x2-x1) < 1e-9: return None
    m=(y2-y1)/(x2-x1); c=y1-m*x1; return m,c

def ransac(X,Y, iters=200, thresh=0.35):
    best=None; best_inliers=None
    pts=list(zip(X,Y))
    for _ in range(iters):
        i,j = rng.choice(len(pts), 2, replace=False)
        model = fit_line(pts[i], pts[j])
        if model is None: continue
        m,c = model
        err = np.abs(m*X - Y + c)/np.sqrt(m*m+1)
        inliers = err < thresh
        if best_inliers is None or inliers.sum() > best_inliers.sum():
            best, best_inliers = model, inliers
    # refit on inliers
    Xi,Yi = X[best_inliers], Y[best_inliers]
    A = np.c_[Xi, np.ones_like(Xi)]
    m,c = np.linalg.lstsq(A,Yi,rcond=None)[0]
    return (m,c), best_inliers

(mr,cr), inliers = ransac(X,Y)

fig,axs = plt.subplots(1,2,figsize=(12,4.5))
axs[0].imshow(acc, cmap='hot', aspect='auto', extent=[np.rad2deg(thetas[0]), np.rad2deg(thetas[-1]), rhos[0], rhos[-1]])
axs[0].set_title('Hough accumulator (peak marked)')
axs[0].plot(np.rad2deg(theta_p), rho_p, 'c+', ms=12)
axs[1].scatter(X[~inliers], Y[~inliers], c='gray', label='outliers')
axs[1].scatter(X[inliers], Y[inliers], c='#1f5f7a', label='inliers')
xs = np.linspace(0,10,100)
axs[1].plot(xs, mr*xs+cr, 'r', lw=2, label='RANSAC fit')
axs[1].legend(); axs[1].set_title('RANSAC line fitting')
plt.tight_layout(); plt.show()
print('Hough peak theta(deg)=%.1f rho=%.2f' % (np.rad2deg(theta_p), rho_p))
print('RANSAC inliers: %d/%d  model: y=%.3fx+%.3f' % (inliers.sum(), len(X), mr, cr))
</code></pre>
<p><strong>Try in Colab:</strong> detect multiple lines by suppressing peaks iteratively, fit circles (3D accumulator or RANSAC), or use <code>cv2.HoughLines</code> and a homography RANSAC on feature matches.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L5 py')
p.write_text(t)

# Lesson 6
p = base/'006-image-blending.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="blend-anim" width="720" height="170" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls">
    <label>Feather width <input id="ba-w" type="range" min="0" max="80" step="2" value="30"></label>
    <label>Misalignment (px) <input id="ba-m" type="range" min="0" max="12" step="1" value="0"></label>
    <output id="ba-o"></output>
  </div>
  <figcaption><strong>Blend vs alignment.</strong> Wider feather hides exposure seams but, with misalignment, creates ghosting/double edges — blending cannot replace registration.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('blend-anim'); if(!c) return; var x=c.getContext('2d');
  function stripe(offset, bright){ var a=[]; for(var i=0;i<300;i++){ var v=((Math.floor((i+offset)/20)%2)?170:90)+bright + 20*Math.sin(i*0.2); a.push(Math.max(0,Math.min(255,v))); } return a; }
  function draw(){
    var w=+document.getElementById('ba-w').value, m=+document.getElementById('ba-m').value;
    document.getElementById('ba-o').textContent='feather='+w+'px, misalign='+m+'px';
    var A=stripe(0,0), B=stripe(m,35), seam=150;
    x.clearRect(0,0,720,170);
    for(var y=0;y<60;y++) for(var i=0;i<300;i++){ var alpha=i<seam-w?1:(i>seam+w?0:1-(i-(seam-w))/(2*w||1)); var v=alpha*A[i]+(1-alpha)*B[i]; x.fillStyle='rgb('+v+','+v+','+v+')'; x.fillRect(40+i,40+y,1,1); }
    x.strokeStyle='rgba(163,35,31,0.8)'; x.beginPath(); x.moveTo(40+seam,40); x.lineTo(40+seam,100); x.stroke();
    x.fillStyle=getComputedStyle(document.body).color; x.font='12px ui-monospace,monospace';
    x.fillText('Left: A  |  Right: B (brighter'+(m?(', shifted '+m+'px)'):')') , 40, 120);
    x.fillText('Red line: seam. Increase misalignment to see ghosting even with feather.', 40, 150);
  }
  ['ba-w','ba-m'].forEach(function(id){document.getElementById(id).addEventListener('input',draw);}); draw();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L6 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. Demonstrates alpha/feather blending and a simple Laplacian-pyramid (multi-band) blend on synthetic images with an exposure difference.</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

def make_img(offset=0, bright=0):
    H,W=128,256
    y,x=np.mgrid[0:H,0:W]
    base = (((x+offset)//16 + y//16) % 2)*120 + 60
    detail = 20*np.sin((x+offset)*0.3)*np.sin(y*0.3)
    return np.clip(base + detail + bright, 0, 255).astype(np.float32)

A = make_img(0, 0)
B = make_img(0, 35)  # exposure difference

def feather_blend(A,B,center,width):
    H,W=A.shape; alpha=np.ones((H,W),np.float32)
    ramp=np.clip((np.arange(W)- (center-width))/(2*width+1e-6),0,1)
    alpha *= (1-ramp)
    return alpha*A + (1-alpha)*B, alpha

# Simple Gaussian/Laplacian pyramid (down/up by factor 2)
def down(img):
    k=np.array([1,4,6,4,1],np.float32)/16
    g=np.apply_along_axis(lambda m: np.convolve(m,k,mode='same'), axis=1, arr=img)
    g=np.apply_along_axis(lambda m: np.convolve(m,k,mode='same'), axis=0, arr=g)
    return g[::2,::2]

def up(img, shape):
    out=np.zeros(shape,np.float32)
    out[::2,::2]=img
    k=np.array([1,4,6,4,1],np.float32)/8
    out=np.apply_along_axis(lambda m: np.convolve(m,k,mode='same'), axis=1, arr=out)
    out=np.apply_along_axis(lambda m: np.convolve(m,k,mode='same'), axis=0, arr=out)
    return out

def gaussian_pyr(img, levels):
    G=[img]
    for _ in range(levels): G.append(down(G[-1]))
    return G

def laplacian_pyr(img, levels):
    G=gaussian_pyr(img,levels); L=[]
    for i in range(levels):
        L.append(G[i]-up(G[i+1], G[i].shape))
    L.append(G[-1]); return L

def blend_pyr(LA,LB,GM):
    return [gm*la + (1-gm)*lb for la,lb,gm in zip(LA,LB,GM)]

def collapse(L):
    img=L[-1]
    for i in range(len(L)-2,-1,-1): img = up(img, L[i].shape) + L[i]
    return img

levels=4
center, width = W//2, 20
_, alpha = feather_blend(A,B,center,width)
hard, _ = feather_blend(A,B,center,0)
feath, _ = feather_blend(A,B,center,width)
LA,LB = laplacian_pyr(A,levels), laplacian_pyr(B,levels)
GM = gaussian_pyr(alpha,levels)
pyr = np.clip(collapse(blend_pyr(LA,LB,GM)),0,255)

fig,axs=plt.subplots(2,3,figsize=(13,6))
axs[0,0].imshow(A,cmap='gray',vmin=0,vmax=255); axs[0,0].set_title('A')
axs[0,1].imshow(B,cmap='gray',vmin=0,vmax=255); axs[0,1].set_title('B (brighter)')
axs[0,2].imshow(alpha,cmap='gray'); axs[0,2].set_title('Mask (feathered)')
axs[1,0].imshow(hard,cmap='gray',vmin=0,vmax=255); axs[1,0].set_title('Hard seam')
axs[1,1].imshow(feath,cmap='gray',vmin=0,vmax=255); axs[1,1].set_title('Feather blend')
axs[1,2].imshow(pyr,cmap='gray',vmin=0,vmax=255); axs[1,2].set_title('Multi-band (pyramid)')
for a in axs.ravel(): a.axis('off')
plt.tight_layout(); plt.show()
</code></pre>
<p><strong>Try in Colab:</strong> introduce a few-pixel misalignment between A and B to see ghosting, or blend real images with an alpha mask.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L6 py')
p.write_text(t)

# Lesson 7
p = base/'007-image-registration.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="reg-anim" width="720" height="190" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls"><button id="rg-step" type="button">Step pipeline</button> <button id="rg-reset" type="button">Reset</button> <output id="rg-o"></output></div>
  <figcaption><strong>Registration pipeline (animated).</strong> Detect/match correspondences → estimate transform robustly → warp and overlay to evaluate alignment.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('reg-anim'); if(!c) return; var x=c.getContext('2d'), step=0;
  var labels=['1) Detect & match features','2) Estimate transform (robust)','3) Warp & overlay to check alignment'];
  function draw(){
    x.clearRect(0,0,720,190);
    document.getElementById('rg-o').textContent=labels[step];
    x.fillStyle=getComputedStyle(document.body).color; x.font='13px ui-monospace,monospace'; x.fillText(labels[step],20,20);
    function box(x0,y0,col){x.strokeStyle=col;x.lineWidth=2;x.strokeRect(x0,y0,90,70);x.lineWidth=1;}
    box(40,50,'rgba(120,120,120,0.7)'); box(170,50,'rgba(120,120,120,0.7)');
    x.fillStyle=getComputedStyle(document.body).color; x.fillText('target',55,135); x.fillText('moving',185,135);
    var ptsT=[[60,70],[110,75],[80,105]]; var ptsM=[[190,80],[235,70],[215,110]];
    if(step>=0){ ptsT.forEach(function(p){x.fillStyle='#1f5f7a'; x.beginPath(); x.arc(p[0],p[1],4,0,Math.PI*2); x.fill();}); ptsM.forEach(function(p){x.fillStyle='#a3231f'; x.beginPath(); x.arc(p[0],p[1],4,0,Math.PI*2); x.fill();});
      x.strokeStyle='rgba(120,120,120,0.6)'; for(var i=0;i<3;i++){x.beginPath();x.moveTo(ptsT[i][0],ptsT[i][1]);x.lineTo(ptsM[i][0],ptsM[i][1]);x.stroke();} }
    if(step>=1){ x.fillStyle=getComputedStyle(document.body).color; x.fillText('T (affine/homography) estimated via RANSAC inliers', 300, 70); x.strokeStyle='rgba(31,95,122,0.8)'; x.beginPath(); x.moveTo(270,90); x.lineTo(350,90); x.stroke(); }
    if(step>=2){ x.strokeStyle='rgba(31,95,122,0.7)'; x.strokeRect(430,50,90,70); x.strokeStyle='rgba(163,35,31,0.5)'; x.strokeRect(438,54,90,70); x.fillStyle=getComputedStyle(document.body).color; x.fillText('overlay: aligned', 440, 135); x.fillText('residuals/similarity checked', 300, 110); }
  }
  document.getElementById('rg-step').addEventListener('click',function(){step=(step+1)%3; draw();});
  document.getElementById('rg-reset').addEventListener('click',function(){step=0; draw();}); draw();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L7 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. A synthetic feature-based registration: correspondences → affine estimate with RANSAC-like selection → inverse warp and overlay (uses NumPy/Matplotlib only).</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

# Target and moving (synthetic) images
H,W=120,160
yy,xx=np.mgrid[0:H,0:W]
def draw_shape(shift=(0,0), angle=0, scale=1.0):
    img=np.zeros((H,W),np.float32)
    # simple shapes
    img[30:80,40:110]=120
    img[50:65,60:130]=200
    img[(yy-90)**2 + (xx-60)**2 < 12*12]=180
    # apply transform via inverse sampling
    a=np.deg2rad(angle); c,s=np.cos(a),np.sin(a)
    M=np.array([[scale*c,-scale*s,shift[0]],[scale*s,scale*c,shift[1]],[0,0,1]])
    Minv=np.linalg.inv(M)
    Xd,Yd=np.mgrid[0:W,0:H]
    ones=np.ones_like(Xd)
    src=Minv @ np.stack([Xd,Yd,ones],0).reshape(3,-1)
    xs,ys=src[0]/src[2], src[1]/src[2]
    x0=np.clip(np.floor(xs).astype(int),0,W-1); x1=np.clip(x0+1,0,W-1)
    y0=np.clip(np.floor(ys).astype(int),0,H-1); y1=np.clip(y0+1,0,H-1)
    wx=xs-x0; wy=ys-y0
    Ia=img[y0,x0]; Ib=img[y0,x1]; Ic=img[y1,x0]; Id=img[y1,x1]
    out=((1-wx)*(1-wy)*Ia + wx*(1-wy)*Ib + (1-wx)*wy*Ic + wx*wy*Id).reshape(H,W)
    mask=((xs>=0)&(xs<W-1)&(ys>=0)&(ys<H-1)).reshape(H,W)
    return out, mask, M

target, _, _ = draw_shape((0,0),0,1.0)
# moving is a transformed target
moving, mask_m, M_true = draw_shape((8,5),12,1.05)

# Synthetic correspondences (true + outliers)
src_pts = np.array([[45,35],[100,35],[100,70],[55,75],[60,90],[30,80]],np.float32)
ones=np.ones((len(src_pts),1),np.float32)
tgt_true = (M_true @ np.c_[src_pts,ones].T).T
tgt_pts = (tgt_true[:,:2]/tgt_true[:,2:3]).astype(np.float32)
tgt_pts = tgt_pts + np.random.default_rng(1).normal(0,0.6,tgt_pts.shape).astype(np.float32)
# add outliers
tgt_pts_noisy = tgt_pts.copy(); tgt_pts_noisy[-1] += np.array([25,-20]); tgt_pts_noisy[-2] += np.array([-20,15])

def estimate_affine(src,dst):
    X = np.c_[src, np.ones(len(src))]
    A,_,_,_ = np.linalg.lstsq(X, dst, rcond=None)
    M = np.eye(3); M[:2,:]=A.T; return M

def ransac_affine(src,dst,iters=200,thresh=3.0):
    best=None; best_inl=None
    rng=np.random.default_rng(0)
    for _ in range(iters):
        idx=rng.choice(len(src),3,replace=False)
        M=estimate_affine(src[idx],dst[idx])
        proj=(M @ np.c_[src,np.ones(len(src))].T).T; proj=proj[:,:2]/proj[:,2:3]
        err=np.linalg.norm(proj-dst,axis=1)
        inl=err<thresh
        if best_inl is None or inl.sum()>best_inl.sum(): best,best_inl=M,inl
    if best_inl.sum()>=3: best=estimate_affine(src[best_inl],dst[best_inl])
    return best,best_inl

M_est, inl = ransac_affine(src_pts, tgt_pts_noisy)
Minv = np.linalg.inv(M_est)
Xd,Yd=np.mgrid[0:W,0:H]
src=(Minv @ np.stack([Xd,Yd,np.ones_like(Xd)],0).reshape(3,-1))
xs,ys=src[0]/src[2], src[1]/src[2]
x0=np.clip(np.floor(xs).astype(int),0,W-1); x1=np.clip(x0+1,0,W-1)
y0=np.clip(np.floor(ys).astype(int),0,H-1); y1=np.clip(y0+1,0,H-1)
wx=xs-x0; wy=ys-y0
Ia=moving[y0,x0]; Ib=moving[y0,x1]; Ic=moving[y1,x0]; Id=moving[y1,x1]
warped=((1-wx)*(1-wy)*Ia + wx*(1-wy)*Ib + (1-wx)*wy*Ic + wx*wy*Id).reshape(H,W)
valid=((xs>=0)&(xs<W-1)&(ys>=0)&(ys<H-1)).reshape(H,W)
overlay = 0.5*target + 0.5*np.where(valid,warped,0)

fig,axs=plt.subplots(1,4,figsize=(14,3.5))
axs[0].imshow(target,cmap='gray'); axs[0].scatter(tgt_pts_noisy[:,0],tgt_pts_noisy[:,1],c='cyan',s=20); axs[0].set_title('Target + matches')
axs[1].imshow(moving,cmap='gray'); axs[1].scatter(src_pts[:,0],src_pts[:,1],c='orange',s=20); axs[1].set_title('Moving')
axs[2].imshow(warped,cmap='gray'); axs[2].set_title('Warped moving')
axs[3].imshow(overlay,cmap='gray'); axs[3].set_title('Overlay')
for a in axs: a.axis('off')
plt.tight_layout(); plt.show()
print('Inliers:', inl.sum(), '/', len(inl))
print('Estimated M:\n', M_est)
</code></pre>
<p><strong>Try in Colab:</strong> replace synthetic points with real features (<code>cv2.ORB_create</code>/<code>BFMatcher</code>), estimate a homography with <code>cv2.findHomography(..., cv2.RANSAC)</code>, and compute NCC/SSD in the overlap.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L7 py')
p.write_text(t)

# Lesson 8
p = base/'008-deep-learning-computer-vision.html'
t = p.read_text()
vis = r'''
<figure class="fig">
  <canvas id="cnn-anim" width="720" height="180" style="width:100%;max-width:720px;height:auto;border:1px solid var(--rule);background:var(--card);border-radius:6px"></canvas>
  <div class="fig-controls">
    <label>Depth <input id="ca-d" type="range" min="1" max="4" step="1" value="2"></label>
    <output id="ca-o"></output>
  </div>
  <figcaption><strong>Receptive field growth (interactive).</strong> Stacking 3×3 convolutions (stride 1) expands what each deeper unit “sees,” enabling hierarchical features.</figcaption>
</figure>
<script>
(function(){
  var c=document.getElementById('cnn-anim'); if(!c) return; var x=c.getContext('2d');
  function draw(){
    var d=+document.getElementById('ca-d').value, rf=1+2*d;
    document.getElementById('ca-o').textContent='depth='+d+' → receptive field '+rf+'×'+rf;
    x.clearRect(0,0,720,180);
    var cell=10, ox=40, oy=30, N=11;
    for(var yy=0;yy<N;yy++) for(var xx=0;xx<N;xx++){ x.fillStyle=((xx+yy)%2)?'#d9d9d9':'#f2f2f2'; x.fillRect(ox+xx*cell,oy+yy*cell,cell,cell); }
    var cx=5,cy=5, r0=cx-Math.floor(rf/2);
    x.fillStyle='rgba(31,95,122,0.18)'; x.fillRect(ox+r0*cell,oy+r0*cell,rf*cell,rf*cell);
    x.strokeStyle='#1f5f7a'; x.lineWidth=2; x.strokeRect(ox+r0*cell,oy+r0*cell,rf*cell,rf*cell);
    x.fillStyle='rgba(163,35,31,0.35)'; x.fillRect(ox+cx*cell,oy+cy*cell,cell,cell);
    x.lineWidth=1;
    x.fillStyle=getComputedStyle(document.body).color; x.font='12px ui-monospace,monospace';
    x.fillText('input grid', ox, oy+N*cell+16);
    for(var i=1;i<=d;i++){ var bx=220+(i-1)*110, by=50; x.strokeStyle='rgba(120,120,120,0.7)'; x.strokeRect(bx,by,70,50); x.fillText('conv'+i+' (3×3)', bx+2, by+65); if(i>1){x.beginPath();x.moveTo(bx-40,75);x.lineTo(bx,75);x.stroke();} }
    x.beginPath(); x.moveTo(ox+N*cell,85); x.lineTo(220,75); x.stroke();
    x.fillText('Each layer aggregates a 3×3 neighborhood of the previous one.', 220, 150);
  }
  document.getElementById('ca-d').addEventListener('input',draw); draw();
})();
</script>
'''
t = insert_before(t, '<h2>Worked examples</h2>', vis, 'L8 vis')
py = r'''
<h2>Python in Colab: implement the lesson</h2>
<p>Run in Google Colab. Builds a tiny CNN forward pass (convolution, ReLU, pooling), visualizes learned-like filter responses and receptive-field growth, and trains a minimal classifier concept on synthetic data (NumPy-only).</p>
<pre><code>import numpy as np
import matplotlib.pyplot as plt

# --- Tiny CNN building blocks (NumPy) ---
def conv2(x, k, bias=0.0, stride=1, padding=1):
    # x: HxW, k: khxkw
    if padding:
        x=np.pad(x,((padding,padding),(padding,padding)),mode='constant')
    kh,kw=k.shape; H,W=x.shape
    oh=(H-kh)//stride+1; ow=(W-kw)//stride+1
    out=np.zeros((oh,ow),np.float32)
    for i in range(oh):
        for j in range(ow):
            patch=x[i*stride:i*stride+kh, j*stride:j*stride+kw]
            out[i,j]=np.sum(patch*k)+bias
    return out

def relu(x): return np.maximum(0,x)
def maxpool2(x, size=2, stride=2):
    H,W=x.shape; oh=(H-size)//stride+1; ow=(W-size)//stride+1
    out=np.zeros((oh,ow),np.float32)
    for i in range(oh):
        for j in range(ow):
            out[i,j]=np.max(x[i*stride:i*stride+size, j*stride:j*stride+size])
    return out

# Synthetic "image"
H,W=32,32
yy,xx=np.mgrid[0:H,0:W]
img=np.zeros((H,W),np.float32)
img[8:24,10:14]=1.0; img[10:14,10:22]=1.0  # a 'T'-like shape
img += 0.05*np.random.default_rng(0).standard_normal((H,W))

# Hand-set filters resembling learned early edges
k_vert=np.array([[-1,0,1],[-2,0,2],[-1,0,1]],np.float32)
k_horiz=np.array([[-1,-2,-1],[0,0,0],[1,2,1]],np.float32)
k_diag=np.array([[0,1,2],[-1,0,1],[-2,-1,0]],np.float32)

f1_v=relu(conv2(img,k_vert)); f1_h=relu(conv2(img,k_horiz)); f1_d=relu(conv2(img,k_diag))
p1_v=maxpool2(f1_v); p1_h=maxpool2(f1_h)
# second layer combines pooled maps (simple)
f2 = relu(conv2(p1_v, np.array([[1,0,-1],[1,0,-1],[1,0,-1]],np.float32)) + 0.5*conv2(p1_h, np.array([[1,1,1],[0,0,0],[-1,-1,-1]],np.float32)))

fig,axs=plt.subplots(2,4,figsize=(13,6))
axs[0,0].imshow(img,cmap='gray'); axs[0,0].set_title('Input')
axs[0,1].imshow(f1_v,cmap='magma'); axs[0,1].set_title('Layer1: vertical filter')
axs[0,2].imshow(f1_h,cmap='magma'); axs[0,2].set_title('Layer1: horizontal filter')
axs[0,3].imshow(f1_d,cmap='magma'); axs[0,3].set_title('Layer1: diagonal filter')
axs[1,0].imshow(p1_v,cmap='magma'); axs[1,0].set_title('After pool (RF grows)')
axs[1,1].imshow(p1_h,cmap='magma'); axs[1,1].set_title('After pool')
axs[1,2].imshow(f2,cmap='magma'); axs[1,2].set_title('Layer2: combined features')
# receptive field illustration
rf1=3; rf2= (rf1-1)+2*2  # approx for conv+pool+conv
axs[1,3].text(0.05,0.6,'Receptive field (3x3 stack, stride1): 3,5,7,...\nPooling/stride increase it faster.\nDeeper units see larger context.', fontsize=11)
axs[1,3].axis('off')
for a in axs.ravel():
    if a is not axs[1,3]: a.axis('off')
plt.tight_layout(); plt.show()

# --- Minimal "training" concept: linear classifier on pooled features (gradient descent) ---
rng=np.random.default_rng(0)
def make_sample(label):
    im=np.zeros((16,16),np.float32)
    if label==0: im[4:12,7:9]=1.0  # vertical bar
    else: im[7:9,4:12]=1.0         # horizontal bar
    im += 0.1*rng.standard_normal(im.shape)
    return im

def features(im):
    v=relu(conv2(im,k_vert)).mean(); h=relu(conv2(im,k_horiz)).mean(); return np.array([v,h,1.0])
X=[]; y=[]
for _ in range(120):
    lab=rng.integers(0,2); X.append(features(make_sample(lab))); y.append(lab)
X=np.stack(X); y=np.array(y,np.float32)
w=np.zeros(3,np.float32); lr=0.5
for epoch in range(200):
    logits=X@w; p=1/(1+np.exp(-logits))
    grad=X.T@(p-y)/len(y); w-=lr*grad
pred=(1/(1+np.exp(-(X@w)))>0.5).astype(int)
print('train accuracy:', (pred==y).mean())
</code></pre>
<p><strong>Try in Colab:</strong> replace hand-set kernels with learnable parameters, add more layers/classes, or use PyTorch (<code>torch.nn.Conv2d</code>) on CIFAR-10/MNIST to compare with this from-scratch intuition.</p>
'''
t = insert_before(t, '<h2>Labs &amp; next steps</h2>', py, 'L8 py')
p.write_text(t)

print('patched 2-8')
