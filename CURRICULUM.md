# CURRICULUM

8 lessons, 4 units, 4 checkpoints, plus companion interactive labs. Ordered so each topic builds on the image, geometry, and feature foundations it needs. Minutes are approximate reading/interaction time per lesson.

**Standing rule:** later lessons reference earlier concepts (sampling, convolution, homogeneous transforms, gradients, correspondences) rather than re-teaching them from scratch.

---

## Unit 1 — Images as signals
*What an image is, how it is represented, and how local operations transform it.*

| # | Topic | Objective — you can… | Prereq | Min |
|---|-------|----------------------|--------|-----|
| 1 | Introduction to Computer Vision | explain what CV is, describe the vision pipeline, and represent images as sampled/quantized signals with correct pixel, channel, color-space, histogram, and convolution operations | — | 18 |

**Companion labs:** L1a Convolution & kernels · L1b Intensity transforms & histograms

**Checkpoint 1** — after Lesson 1 (image representation, color, filtering/convolution).

## Unit 2 — Geometry and warping
*How images deform, and how to model and reverse those deformations.*

| # | Topic | Objective — you can… | Prereq | Min |
|---|-------|----------------------|--------|-----|
| 2 | Geometric Transformations & Image Warping | model 2D geometric deformations with transformation matrices and restore/warp images using forward vs inverse mapping with interpolation | 1 | 16 |

**Companion labs:** L2a Transform matrices & composition · L2b Forward vs inverse warping & interpolation

**Checkpoint 2** — after Lesson 2 (transforms, homogeneous coordinates, warping, interpolation).

## Unit 3 — Local features and robust fitting
*Finding repeatable structures, describing them, and fitting models despite outliers.*

| # | Topic | Objective — you can… | Prereq | Min |
|---|-------|----------------------|--------|-----|
| 3 | Corner and Blob Detection | explain why features matter and detect corners/blobs using gradients, the Harris structure tensor, non-maximum suppression, and scale-space (LoG/DoG) responses | 1 | 15 |
| 4 | Feature Detectors/Descriptors (SIFT) | describe SIFT’s pipeline from scale-space extrema to descriptors and explain its invariances and basic matching | 3 | 16 |
| 5 | Model Fitting (Hough Transform, RANSAC) | fit geometric models with Hough voting and robustly estimate models with RANSAC under outliers | 1, 3 | 15 |

**Companion labs:** L3a Harris corner response & NMS · L3b Blob/scale-space intuition · L4a SIFT descriptor & matching intuition · L5a Hough voting · L5b RANSAC line fitting

**Checkpoint 3** — after Lesson 5 (features, descriptors, matching, Hough, RANSAC).

## Unit 4 — Composition, alignment, and learning
*Combining and aligning images, then connecting classical vision to deep learning.*

| # | Topic | Objective — you can… | Prereq | Min |
|---|-------|----------------------|--------|-----|
| 6 | Image Blending | combine overlapping images smoothly using alpha/feathering and multi-scale (pyramid/Laplacian) blending while reasoning about seams and exposure differences | 1, 2 | 14 |
| 7 | Image Registration | explain and execute the end-to-end registration pipeline: detect/match features, estimate transforms robustly, warp/resample, and evaluate alignment | 2, 3, 4, 5 | 16 |
| 8 | Deep Learning–Based Computer Vision | connect classical CV to learned representations and explain introductory CNN mechanics and training, relating DL to the classical tasks above | 1, 3–7 | 17 |

**Companion labs:** L6a Alpha & feathering · L6b Pyramid blending intuition · L7a End-to-end registration pipeline · L8a Convolutional features & receptive fields

**Checkpoint 4** — after Lesson 8 (blending, registration, CNN fundamentals, classical↔DL connections).

---

## Lesson format (each lesson)
- Why this matters
- The one core idea
- How it actually works (step-by-step)
- Worked example(s)
- The trap (common misconception/pitfall)
- Retrieval check (self-check questions with answers)
- Lab/demo links and next steps

## Supporting materials
- `index.html` — dashboard with progression, units, checkpoints, lesson/lab links
- `tour.html` — short guide to using the course
- `labs/` — self-contained interactive demos (SVG/canvas/JS, no dependencies)
- `output/`, `decks/` — lightweight placeholders mirroring reference download sections (no fabricated binaries)
