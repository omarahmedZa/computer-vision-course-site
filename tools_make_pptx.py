import zipfile, os

def esc(s):
    return (s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;'))

def slide_xml(title, bullets):
    paras = f'''<a:p><a:r><a:rPr lang="en-US" sz="3200" b="1"/><a:t>{esc(title)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>'''
    for b in bullets:
        paras += f'''<a:p><a:pPr lvl="0"/><a:r><a:rPr lang="en-US" sz="2000"/><a:t>{esc(b)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>'''
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    <p:sp><p:nvSpPr><p:cNvPr id="2" name="Content"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="457200" y="457200"/><a:ext cx="8229600" cy="5943600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody>
    </p:sp>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

def make_pptx(path, slides):
    # minimal layout/master/theme to satisfy viewers
    ns_ct = 'http://schemas.openxmlformats.org/package/2006/content-types'
    ns_pr = 'http://schemas.openxmlformats.org/package/2006/relationships'
    content_types = [ '<?xml version="1.0" encoding="UTF-8"?>', f'<Types xmlns="{ns_ct}">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>']
    for i in range(1,len(slides)+1):
        content_types.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    content_types.append('</Types>')

    rels = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="{ns_pr}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''

    sld_ids = ''.join([f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1,len(slides)+1)])
    pres = f'''<?xml version="1.0" encoding="UTF-8"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdM"/></p:sldMasterIdLst>
  <p:sldIdLst>{sld_ids}</p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>'''

    pres_rels_items = ''.join([f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1,len(slides)+1)])
    pres_rels = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="{ns_pr}">
  {pres_rels_items}
  <Relationship Id="rIdM" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rIdT" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>'''

    slide_master = '''<?xml version="1.0" encoding="UTF-8"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr/></p:spTree></p:cSld>
<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>'''
    sm_rels = f'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns_pr}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'''
    slide_layout = '''<?xml version="1.0" encoding="UTF-8"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>'''
    sl_rels = f'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns_pr}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''
    theme = '''<?xml version="1.0" encoding="UTF-8"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Theme"><a:themeElements>
<a:clrScheme name="Default"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F497D"/></a:dk2><a:lt2><a:srgbClr val="EEECE1"/></a:lt2><a:accent1><a:srgbClr val="4F81BD"/></a:accent1><a:accent2><a:srgbClr val="C0504D"/></a:accent2><a:accent3><a:srgbClr val="9BBB59"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4><a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Default"><a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Default"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''

    slide_rels = f'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns_pr}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','\n'.join(content_types))
        z.writestr('_rels/.rels', rels)
        z.writestr('ppt/presentation.xml', pres)
        z.writestr('ppt/_rels/presentation.xml.rels', pres_rels)
        z.writestr('ppt/slideMasters/slideMaster1.xml', slide_master)
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels', sm_rels)
        z.writestr('ppt/slideLayouts/slideLayout1.xml', slide_layout)
        z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels', sl_rels)
        z.writestr('ppt/theme/theme1.xml', theme)
        for i,(title,buls) in enumerate(slides,1):
            z.writestr(f'ppt/slides/slide{i}.xml', slide_xml(title,buls))
            z.writestr(f'ppt/slides/_rels/slide{i}.xml.rels', slide_rels)

decks = [
 ("01", [
  ("Lesson 01: Introduction to Computer Vision", ["What CV is and the vision pipeline", "Images as sampled, quantized signals", "Pixels, channels, color spaces, histograms", "Intensity transforms and convolution fundamentals"]),
  ("Vision Pipeline & Image Signal", ["Acquire → preprocess → extract → model → decide", "Sampling sets resolution (H×W); quantization sets bit depth", "Grayscale H×W, color H×W×C (e.g. RGB)", "Histogram summarizes tone but not spatial layout"]),
  ("Color, Transforms, Convolution", ["RGB, luma/gray, HSV: different coordinate views", "Point-wise: g=αI+β, gamma; clamp to valid range", "Convolution: weighted neighborhood sum with kernel K", "Blur, sharpen, Sobel gradients; correlation vs convolution flip"]),
  ("Pitfalls & Takeaways", ["Channel order/range/encoding matter (RGB/BGR, uint8/float)", "Watch overflow/clipping and border handling", "Asymmetric kernels: flip convention matters", "Filtering is the basis for edges, features, and CNNs"]),
 ]),
 ("02", [
  ("Lesson 02: Geometric Transformations & Warping", ["2D transforms and homogeneous matrices", "Forward vs inverse warping", "Interpolation and restoration"]),
  ("Transforms & Matrices", ["Translation, rotation, scale, shear, affine, homography", "Homogeneous p=[x,y,1]^T enables matrix composition", "p' = H p; order matters: (B·A)p", "Homography models plane-to-plane perspective"]),
  ("Warping & Interpolation", ["Forward warping can create holes/overwrites", "Inverse warping: sample source at T^{-1}(p') for every output", "Nearest: preserves values; Bilinear: smooth blend", "Restoration: choose model → estimate → inverse warp"]),
  ("Pitfalls & Takeaways", ["Coordinate/angle conventions must be consistent", "Use inverse mapping for dense image warping", "Choose interpolation by signal (labels vs photos)", "Handle bounds and invalid source samples"]),
 ]),
 ("03", [
  ("Lesson 03: Corner and Blob Detection", ["Why local features matter", "Gradients and local structure", "Harris corners and NMS", "LoG/DoG blobs and scale space"]),
  ("Gradients & Harris", ["Flat vs edge vs corner (aperture intuition)", "Structure tensor M from Ix^2, Iy^2, IxIy", "R = det(M) - k(trace(M))^2; threshold + NMS", "Corner: strong change in two directions"]),
  ("Blobs & Scale Space", ["L(x,y,σ)=Gσ*I builds scale space", "LoG/normalized LoG finds characteristic scale", "DoG approximates LoG efficiently", "Detect extrema in space and scale"]),
  ("Pitfalls & Takeaways", ["Edge magnitude alone is not a corner", "Tune thresholds/windows; apply NMS", "Single-scale detectors miss size variation", "Detection feeds descriptors and registration"]),
 ]),
 ("04", [
  ("Lesson 04: SIFT Detectors/Descriptors", ["Scale-space keypoints", "Orientation and descriptor", "Invariances and matching"]),
  ("SIFT Pipeline", ["DoG extrema in (x,y,σ)", "Localize/refine; reject low-contrast & edge-like points", "Canonical orientation from gradient histogram", "128-D descriptor: 4x4 cells x 8 orientation bins"]),
  ("Invariance & Matching", ["Scale via σ, rotation via canonical frame", "Gradient+normalization for illumination robustness", "Match by distance; ratio test d1/d2 < τ", "Verify geometry (e.g. RANSAC) for reliability"]),
  ("Pitfalls & Takeaways", ["Not invariant to large viewpoint/occlusion", "Ambiguity in repetitive textures without ratio test", "Distinctiveness and stability matter more than count"]),
 ]),
 ("05", [
  ("Lesson 05: Model Fitting (Hough, RANSAC)", ["Fitting amid noise and outliers", "Hough voting in parameter space", "RANSAC consensus estimation"]),
  ("Hough Transform", ["Points vote for compatible parameters", "Line: ρ = x cosθ + y sinθ (sinusoid per point)", "Accumulator peaks → detected models", "Circles/other shapes: higher-dimensional accumulators"]),
  ("RANSAC", ["Sample minimal set → fit model → count inliers (τ)", "Keep best consensus, refit on inliers", "Iterations depend on inlier ratio w and sample size s", "Robust to outliers vs least-squares on all points"]),
  ("Pitfalls & Takeaways", ["Hough: bin resolution/range and multi-model cases", "RANSAC: threshold, iterations, degenerate samples", "Foundations for robust registration/geometry"]),
 ]),
 ("06", [
  ("Lesson 06: Image Blending", ["Combining images smoothly", "Alpha/feathering", "Pyramid/multi-band blending"]),
  ("Alpha & Feathering", ["I = αA + (1-α)B", "Hard seams show exposure/photometric differences", "Feathering smooths transition but can ghost if misaligned", "Mask width trades seam visibility vs blur/ghosting"]),
  ("Pyramid Blending", ["Gaussian pyramid: multi-scale blur/downsample", "Laplacian pyramid: band-pass detail layers", "Blend bands with mask pyramid (wide low-freq, narrow high-freq)", "Reduces seams while preserving detail"]),
  ("Pitfalls & Takeaways", ["Blending does not fix geometric misalignment", "Large photometric differences may need normalization", "Choose seam/blend strategy to context"]),
 ]),
 ("07", [
  ("Lesson 07: Image Registration", ["Aligning images end-to-end", "Correspondences and transforms", "Warping, similarity, evaluation"]),
  ("Registration Pipeline", ["Detect & describe features → match correspondences", "Choose model (affine/homography) for the scene", "Estimate T robustly (RANSAC) and refit on inliers", "Inverse warp + interpolation into target frame"]),
  ("Measures & Models", ["Affine preserves parallelism; homography for planar perspective", "Similarity: SSD/SAD, NCC, Mutual Information", "Evaluate by residuals, overlays, difference maps", "Model mismatch/parallax limits global transforms"]),
  ("Pitfalls & Takeaways", ["Outliers require robust estimation", "Wrong motion model leaves systematic error", "Good metric ≠ correct local alignment; inspect visually"]),
 ]),
 ("08", [
  ("Lesson 08: Deep Learning–Based Computer Vision", ["From hand-crafted to learned representations", "CNN fundamentals and training basics", "Links to classical CV tasks"]),
  ("CNN Fundamentals", ["Learned local filters with weight sharing", "Convolution, nonlinearity, padding/stride, pooling", "Feature hierarchies: edges/textures → parts/semantics", "Receptive field grows with depth/stride/pooling"]),
  ("Training & Connections", ["Loss + gradient-based optimization (backprop)", "Generalization, overfitting, augmentation/regularization", "Extends classical: features, alignment, dense prediction", "Classical geometry (RANSAC/warping) still valuable"]),
  ("Pitfalls & Takeaways", ["Performance depends on data, labels, and evaluation", "Sensitive to distribution shift; not guaranteed understanding", "Hybrid pipelines combine learning with explicit geometry"]),
 ]),
]

for num, slides in decks:
    make_pptx(f'decks/lesson-{num}.pptx', slides)
print('ok', len(decks))
