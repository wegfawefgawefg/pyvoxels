# Rendering Notes

## Current Approach (CPU)

This project currently does **per-pixel ray marching** on the CPU:

1. For each pixel, compute a ray from camera through the viewplane.
2. Step forward along the ray (`NUM_RAY_STEPS`, `MARCH_STEP_SIZE`).
3. Sample voxel occupancy and stop at first hit.
4. Shade based on hit distance.

Approximate cost per frame is proportional to:

`screen_pixels * march_steps`

That is why lowering internal render resolution has a big effect on FPS.

## Why GPU Is a Better Fit

Ray marching is highly parallel for primary rays:

- One thread can handle one pixel/ray.
- Threads mostly read shared voxel data and write one output pixel.
- This maps well to fragment or compute shaders.

## Main GPU Design Challenges

### 1) Voxel Data Layout / Packing

You need a structure the GPU can traverse efficiently:

- Dense `3D texture` (simple, fast sampling, more memory).
- `SSBO` / linear buffer (manual indexing, flexible packing).
- Sparse structures (clipmaps, octrees, bricks) for larger worlds.

Tradeoff is memory usage vs traversal speed and update complexity.

### 2) Memory Bandwidth and Divergence

Different rays take different numbers of steps:

- Some hit quickly.
- Some miss and march to max distance.

This causes branch divergence and cache pressure on GPU.

### 3) Dynamic Updates

If voxels change often, CPU->GPU transfers can become expensive.
Chunking and partial uploads help reduce bandwidth.

## Synchronization Clarification

For basic primary-ray rendering, synchronization is usually minimal:

- Each thread writes to its own pixel.
- No shared write target is required.

Synchronization becomes important when doing shared/global writes
(for example counters, reductions, compaction, building/updating
acceleration structures on-GPU).
