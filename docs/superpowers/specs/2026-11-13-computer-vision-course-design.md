# Computer Vision Course Site — Design Spec

**Date:** 2026-11-13  
**Status:** Approved by user direction ("do your recommendation" after Section 1 approval)  
**Target:** `/home/stave/computer-vision-course`  
**Reference:** `/home/stave/ai-ml-course` (structure, visual/UX, lesson components, interaction patterns)

## 1. Goal and constraints
- Build a complete, teachable static Computer Vision course website modeled on `/home/stave/ai-ml-course`.
- Stack: plain HTML/CSS/JS only. No frontend framework, no build step, no CDN/external dependencies unless already present in reference. Dependency-light and self-contained.
- Deployment: GitHub Pages from **repo root on `main`**. Repo intended to be **private** on GitHub (README documents repo privacy as a GitHub setting and notes Pages visibility/plan considerations). All internal links/assets use correct relative paths for root Pages base path.
- Mirror reference IA/feel: dashboard (`index.html`), structured lesson pages, clear navigation/progression, reusable `assets/`, curriculum-driven organization, lesson components (masthead/topline, sections, keyboxes/formulas, tables, callouts/traps, figures, quizzes/checks, labs, pager/continue). Adapt/reuse visual language and interaction patterns from reference assets (`lesson.css`, `figures.css`, `course.js`, and minimal figure/interaction helpers as needed) pruned to CV needs.
- Quality: clear, correct, original explanatory content; consistent notation/terminology; responsive and readable; accessibility basics (semantic headings, labels/alt where applicable). Do not invent details about reference—follow what is there.

## 2. Project structure
```
/home/stave/computer-vision-course/
  index.html            # course dashboard/map with units, progression, checkpoints, links
  tour.html             # "how to use this course" tour
  lessons/              # 8 core lessons (001-...html ... 008-...html)
  labs/                 # companion interactive demo/lab pages (SVG/canvas/JS)
  assets/
    lesson.css          # adapted from reference
    figures.css         # adapted from reference
    course.js           # adapted/pruned (progress, continue, theme/readbar, quiz hooks)
    cv-demos.js         # small, self-contained helpers for CV interactive labs/figures (if needed)
  output/               # lightweight placeholder download artifacts (no fake binaries)
  decks/                # lightweight placeholder deck artifacts/links
  CURRICULUM.md
  README.md
  docs/superpowers/specs/2026-11-13-computer-vision-course-design.md
```
- `.nojekyll` added only if needed; otherwise omitted and noted.
- `tour.html` tailored to CV content (lessons, figures, labs/demos, checks, how to use).

## 3. Curriculum and IA (8 core lessons + companion labs)
Coherent progression in 4 units with checkpoints, following given topic scope while making prerequisites explicit.

### Unit 1 — Images as signals
- **L01 — Introduction to Computer Vision** (topic 1)
  - Objective: explain what computer vision is, describe the vision pipeline, and represent images as sampled/quantized signals with correct pixel/channel/color/intensity operations.
  - Prereqs: none (math kept intuitive; linear algebra/light notation introduced gently).
  - Covers: what CV is and example tasks; vision pipeline (scene→sensor→image→processing→decision); images as functions/signals, sampling & quantization, resolution/bit depth; pixels, channels, grayscale; color spaces (RGB/HSV/grayscale) and conversions intuition; intensity transforms (brightness/contrast, gamma, thresholding intuition); histograms and contrast; **basic filtering/convolution fundamentals as prerequisites**: kernels, correlation/convolution idea, padding/stride intuition, blur, sharpening, edge emphasis (Sobel/gradient preview) with worked examples.
  - Pitfalls: RGB vs BGR/order, uint8 overflow/clipping, convolution vs correlation flip, border effects.
  - Labs/demos: interactive convolution kernel demo (apply blur/sharpen/edge kernels on a small synthetic image via canvas/SVG grid), histogram/intensity transform explorer.
  - Check: retrieval questions on sampling/quantization, color spaces, and convolution output.

### Unit 2 — Geometry and warping
- **L02 — Geometric Transformations & Image Warping** (topic 2)
  - Objective: model 2D geometric deformations with transformation matrices and restore/warp images using forward vs inverse mapping with interpolation.
  - Prereqs: L01 (pixels/coordinates), basic matrices.
  - Covers: 2D transforms—translation, rotation, scale, shear, affine, projective/homography; homogeneous coordinates and transformation matrices; composing transforms; forward vs inverse warping; interpolation (nearest, bilinear; mention bicubic conceptually); resampling and aliasing intuition; restoring geometrically deformed images (estimate/apply inverse transform).
  - Pitfalls: coordinate origin/conventions, forward warping holes, interpolation blur/aliasing, degrees vs radians.
  - Labs: interactive transform/warping demo (manipulate matrix params, compare forward vs inverse warping and nearest vs bilinear on a grid/image).
  - Check: matrix application, inverse mapping, interpolation choice.

- **Checkpoint 1** after Unit 1–2 foundations.

### Unit 3 — Local features and matching
- **L03 — Corner and Blob Detection** (topic 3)
  - Objective: explain why features matter and detect corners/blobs using gradients/structure tensors (Harris) and scale-space blob responses (LoG/DoG intuition).
  - Prereqs: L01 (gradients/filtering), L02 helpful for invariance motivation.
  - Covers: why features matter (matching, tracking, recognition, registration); image gradients and local structure; Harris corner detector—second-moment/structure matrix, corner response, thresholding, non-maximum suppression; blob detection—scale-space intuition, Laplacian of Gaussian, Difference of Gaussians, scale selection, NMS across space/scale.
  - Pitfalls: edge vs corner response, scale dependence, threshold/sensitivity.
  - Labs: Harris response/NMS visualization on synthetic patterns; blob scale-space/DoG response demo.

- **L04 — Feature Detectors/Descriptors (SIFT)** (topic 4)
  - Objective: describe SIFT’s pipeline from scale-space extrema to descriptors and explain its invariances and basic matching.
  - Prereqs: L03.
  - Covers: scale-space extrema detection; keypoint localization/refinement and orientation assignment; descriptor construction (gradient histograms, normalization); invariances (scale/rotation/illumination) and limits; matching basics (distance, ratio test intuition).
  - Pitfalls: claiming invariance to affine/viewpoint beyond limits, mismatches without ratio/geometric checks.
  - Labs: descriptor/matching intuition demo (patch gradients→histogram concept, distance comparison) as lightweight SVG/canvas illustration.

- **L05 — Model Fitting (Hough Transform, RANSAC)** (topic 5)
  - Objective: fit geometric models (lines/circles) with Hough voting and robustly estimate models with RANSAC under outliers.
  - Prereqs: L01 (edges), L03/L04 (points/matches).
  - Covers: parameter spaces and voting; Hough transform for lines (and circle intuition), accumulator, peak detection; inlier/outlier concepts; RANSAC algorithm steps, iterations/probability intuition, consensus/inliers, applications to robust fitting.
  - Pitfalls: accumulator resolution/quantization, Hough cost, RANSAC iteration/threshold choice, degenerate samples.
  - Labs: interactive Hough line voting demo (points→(ρ,θ) accumulator) and RANSAC line-fitting demo (inliers/outliers, iterations).

- **Checkpoint 2** after Unit 3.

### Unit 4 — Composition, alignment, and learning
- **L06 — Image Blending** (topic 6)
  - Objective: combine overlapping images smoothly by reasoning about alpha/feathering and multi-scale (pyramid/Laplacian) blending and seams/exposure differences.
  - Prereqs: L01, L02.
  - Covers: naive cut-and-paste seams; alpha blending and feathering/masks; exposure/illumination differences; Gaussian and Laplacian pyramids intuition; multi-band/Laplacian pyramid blending concepts; seam considerations (awareness, conceptual).
  - Pitfalls: hard masks, mismatched exposure, ghosting from misalignment (link to L07).
  - Labs: alpha/feathering and simple pyramid-level blending visualization on synthetic strips/images.

- **L07 — Image Registration** (topic 7)
  - Objective: explain and execute the end-to-end registration pipeline: detect/match features, estimate transforms, warp/resample, and evaluate alignment.
  - Prereqs: L02, L03, L04, L05.
  - Covers: what registration is and use cases; feature detection/matching recap; transform estimation (affine/homography) via correspondences; robust estimation (RANSAC) in registration; warping/resampling; similarity measures (SSD/SAD/NCC/MI intuition); end-to-end pipeline and failure modes.
  - Pitfalls: too few/inaccurate matches, wrong motion model, parallax/non-planar scenes.
  - Labs: end-to-end registration pipeline demo (correspondences → estimated transform → warped overlay/alignment) with controllable match quality.
  - Checkpoint 3.

### Unit 5 — From classical to deep learning
- **L08 — Deep Learning–Based Computer Vision** (topic 8)
  - Objective: connect classical CV to learned representations and explain introductory CNN mechanics and training, relating DL to prior classical tasks.
  - Prereqs: L01 (convolution intuition), L03–L07 concepts.
  - Covers: from hand-crafted features to learned representations; CNN fundamentals—convolutions as learned filters, feature maps, padding/stride, pooling, receptive fields, hierarchies; training basics—loss, gradient-based optimization (high level), overfitting/regularization intuition; how modern DL approaches relate to/extend classical tasks (detection/features, alignment/stitching, dense prediction) at introductory level; limitations and when classical methods remain useful.
  - Pitfalls: treating CNNs as magic, ignoring data/compute/label needs, confusing correlation with understanding.
  - Labs: receptive-field/feature-hierarchy visualization and/or simple learned-vs-handcrafted filter comparison (conceptual interactive figure).
  - Checkpoint 4 (course wrap).

## 4. Page and component design (mirroring reference)
- **Shared shell:** sticky `.topline` nav (course map, prev/next or lesson position pill, progress/theme controls as applicable), `.readbar`, semantic `<main>` with constrained measure. Adapt `lesson.css`/`figures.css` variables, typography, spacing, dark/light behavior to match reference feel.
- **Dashboard (`index.html`):** hero/kicker/title/subtitle, continue/start CTA, progress/ring or summary (adapted from `course.js` state model simplified for 8 lessons + labs/checkpoints), unit sections with topic rows (number, dot/status, link, objective, meta), checkpoint rows, labs/downloads sections, “how to use”/tour link. `data-lesson`, `data-lab`, `data-unit` attributes for progress hooks.
- **Lesson pages:** masthead (kicker unit/topic, h1, objective), consistent section structure—Why this matters, One core idea, How it actually works (stepwise), Worked example(s), The trap (callout + tell), Retrieval check (quiz/details with self-check hooks if retained), Lab links/grid, Next/prev navigation/pager. Components: `numstrip`, `keybox`/`formula`, tables, callouts, figures/SVG/canvas blocks, code/pre where useful (minimal, self-contained), `.labnav`.
- **Lab pages:** focused interactive demo, brief explanation, controls/readouts, back/related-lesson links; use `figures.css`/control styles and small `cv-demos.js` or inline per-page script (no deps). Accessible labels.
- **`course.js` adaptation:** keep lightweight localStorage progress/continue/theme patterns where they fit 8 lessons/labs; prune notebook/lab-specific machinery not needed. Ensure no broken references if features omitted.
- **Visuals:** prefer SVG/canvas/inline figures generated in-page; use small deterministic synthetic images/patterns (grids, gradients, checkerboards) drawn via canvas so no external image assets required.

## 5. Supporting materials
- `CURRICULUM.md`: full outline (units, lessons, prereqs, objectives, lab/demo mapping, checkpoints).
- `README.md`: course description, structure, local preview (`python3 -m http.server 8000` from root and open http://localhost:8000), and exact GitHub Pages deployment steps for root-on-`main` in a **private** repo (create repo, push, Settings→Pages→Deploy from branch `main` / root) with note on Pages visibility/plan behavior for private repos.
- `output/` and `decks/`: minimal placeholder files/README-style notes or HTML placeholders linked as downloads only if they add value and mirror reference pattern; clearly marked as placeholders (no fake PDFs/PPTX).
- `tour.html`: concise tour of lesson structure, figures, labs, and checks.

## 6. Verification / acceptance
- Every topic 1–8 has a complete lesson covering fundamentals and core method with intuition, math/steps, worked examples, visuals/interactive illustration where helpful, pitfalls, and recap/check-for-understanding.
- Companion labs/demos exist and are linked for topics where they add value (at least convolution/intensity, warping/interpolation, Harris/blob, SIFT/matching intuition, Hough/RANSAC, blending, registration pipeline, CNN/receptive-field concept).
- Dashboard navigation works end-to-end; relative paths correct for local serve and root Pages deploy.
- Style/structure mirrors reference course-site design; pages responsive/readable with basic accessibility.
- README includes setup/preview and working GitHub Pages deployment steps. CURRICULUM.md complete.

## 7. Implementation notes
- Copy/adapt reference `assets/lesson.css`, `assets/figures.css`, and a simplified `assets/course.js` as baseline; remove unused selectors/logic; adjust branding/text hooks for CV course.
- Keep JS minimal and page-local where possible for demos; avoid global breakage.
- Write original CV content; verify key formulas/algorithm steps for correctness (convolution, homography, Harris, SIFT stages, Hough/RANSAC, Laplacian pyramid concept, registration pipeline, CNN basics). Notation consistent (e.g. \(I(x,y)\), homogeneous coords, matrices).
- Test by opening via local HTTP server and checking links/assets render.