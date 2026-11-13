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

## Deploy to GitHub Pages (root on `main`)

This site is designed to be served from the **repository root on the `main` branch** with correct relative paths.

1. **Create a GitHub repository** (the owner requested a **private** repo).  
   - On GitHub: New repository → set visibility to **Private** → create (without adding files that conflict, or add and reconcile).
   - *Note:* GitHub Pages availability/visibility for private repositories depends on your GitHub plan and Pages settings (on some plans a Pages site from a private repo may be publicly accessible). Review your repository’s Pages visibility settings after enabling.

2. **Push this project to `main`:**
   ```bash
   cd /path/to/computer-vision-course
   git init
   git add .
   git commit -m "Initial Computer Vision course site"
   git branch -M main
   git remote add origin git@github.com:<your-username>/<your-repo>.git
   git push -u origin main
   ```
   (Use an HTTPS remote if preferred.)

3. **Enable GitHub Pages:**
   - In the repo: **Settings → Pages**
   - **Build and deployment → Source:** Deploy from a branch
   - **Branch:** `main` / **Folder:** `/ (root)` → Save

4. **Verify:** after Pages builds, open the published URL shown in Settings → Pages and confirm the dashboard loads, navigation/lesson/lab links work, and assets render.

### Updating
Edit files, commit, and push to `main`:
```bash
git add -A
git commit -m "Update course content"
git push
```

## Design notes
- Plain HTML/CSS/JS; progress/continue state (if used) is stored locally in the browser and never leaves the device.
- Visuals/demos favor self-contained SVG/canvas/inline scripts consistent with the reference style.
- `output/` and `decks/` contain lightweight placeholders (no fabricated compiled PDFs/PPTX) to mirror the reference’s download structure. Replace with real artifacts if/when you generate them.
