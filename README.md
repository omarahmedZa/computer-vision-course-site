# Computer Vision — course website

A dependency-light, static educational website for an introductory Computer Vision course. It explains core CV topics from first principles — intuition, math/algorithms, worked examples, visual/interactive demos, pitfalls, and checks — in a structure and visual style modeled on [`/home/stave/ai-ml-course`](../ai-ml-course).

## What’s inside

| Path | What it is |
|---|---|
| `index.html` | Course dashboard/map with units, progression, checkpoints, lesson & lab links |
| `tour.html` | Short “how to use this course” tour |
| `lessons/` | 8 core lessons (HTML), one per curriculum topic |
| `labs/` | Companion interactive demos/labs (self-contained SVG/canvas/JS) |
| `assets/` | Shared styles/scripts (`lesson.css`, `figures.css`, `course.js`, demo helpers) adapted from the reference course |
| `CURRICULUM.md` | Modules, lessons, prerequisites, objectives, labs, checkpoints |
| `output/`, `decks/` | Lightweight placeholder download artifacts (no compiled binaries) |
| `docs/superpowers/specs/` | Design/spec notes |

## Curriculum (8 topics)

1. **Introduction to Computer Vision** — vision pipeline, images as signals (sampling/quantization), pixels/channels, color spaces, intensity transforms, histograms, and convolution/filtering fundamentals.
2. **Geometric Transformations & Image Warping** — 2D transforms/affine/homography, matrices, forward vs inverse warping, interpolation, restoring geometric deformation.
3. **Corner and Blob Detection** — gradients/structure, Harris corners, LoG/DoG and scale-space blobs, NMS.
4. **Feature Detectors/Descriptors (SIFT)** — scale-space extrema, keypoint localization/orientation, descriptors, invariances, matching basics.
5. **Model Fitting (Hough Transform, RANSAC)** — Hough voting for lines/circles, robust estimation with RANSAC, inliers/outliers.
6. **Image Blending** — alpha/feathering, Gaussian/Laplacian pyramid blending concepts, seams and exposure differences.
7. **Image Registration** — feature matching, transform estimation, warping/resampling, similarity measures, end-to-end pipeline.
8. **Deep Learning–Based Computer Vision** — learned representations, CNN fundamentals (conv/pooling/receptive fields), training basics, and links to classical CV.

See [CURRICULUM.md](CURRICULUM.md) for units, prerequisites, objectives, and lab mapping.

## Local preview

No build step and no external dependencies. Serve the repo root with any static file server and open it in a browser:

```bash
cd /path/to/computer-vision-course
python3 -m http.server 8000
```

Then visit: <http://localhost:8000/>

(Opening `index.html` directly via `file://` also works for most pages, but a local server is the most reliable way to mirror deployed behavior.)

## Deployment status

- **Private source repository:** <https://github.com/omarahmedZa/computer-vision-course>
- **Live site (GitHub Pages):** <https://omarahmedza.github.io/computer-vision-course-site/>
- **Public Pages mirror repository:** <https://github.com/omarahmedZa/computer-vision-course-site>

The source repository is **private** as requested. On the current GitHub plan, GitHub Pages cannot be enabled for a private repository, so the same static site is published to a separate **public** mirror repository (`computer-vision-course-site`) served from its root on `main`. This keeps the source private while providing a working Pages URL.

## Deploy / update

The project is already initialized and has both remotes configured:

```bash
cd /home/stave/computer-vision-course
git remote -v
# origin  -> private source repo
# pages   -> public Pages mirror repo
```

To publish content changes:

```bash
git add -A
git commit -m "Update course content"
git push origin main    # private source
git push pages main     # public Pages mirror (triggers the Pages build)
```

The GitHub Pages site is configured as **Deploy from a branch → `main` → `/ (root)`**. After pushing, check the deployment status under **Settings → Pages** (or the Actions/Pages build output) and confirm the dashboard, lessons, labs, and assets load at the live URL.

If you later upgrade to a plan that supports Pages on private repositories, you can enable Pages directly on the private repo with the same root-on-`main` configuration and retire the public mirror.

## Design notes
- Plain HTML/CSS/JS; progress/continue state (if used) is stored locally in the browser and never leaves the device.
- Visuals/demos favor self-contained SVG/canvas/inline scripts consistent with the reference style.
- `output/` and `decks/` contain lightweight placeholders (no fabricated compiled PDFs/PPTX) to mirror the reference’s download structure. Replace with real artifacts if/when you generate them.
