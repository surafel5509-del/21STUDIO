# Engine architecture

## Execution model

`GameLoop` advances the ECS with a fixed timestep and produces an interpolation fraction for rendering. Android callbacks only enqueue input; simulation code consumes that queue at a deterministic tick boundary. GLES resources are created and used exclusively on the `GLSurfaceView` renderer thread.

## ECS and plugins

`World` is the sole owner of entity lifetime and component storage. Components are data-only. A plugin contributes components plus one or more `GameSystem` implementations; it does not need to modify core. Queries are snapshotted so structural changes do not invalidate a system's iteration.

## Physics

`PhysicsSystem` integrates velocity/acceleration, applies damping, filters collision layers, detects AABB/circle contacts, dispatches trigger contacts, and resolves non-trigger contacts through positional correction and impulses. It also exposes a closest-hit raycast. `SpatialHash` is available to custom broad-phase systems and uses floor-based grid coordinates to handle negative world space.

## Rendering

The OpenGL module owns the render surface, camera matrices, batch ordering and shader lifecycle. Gameplay submits sprites in render order; production render systems should upload atlas textures once and issue batched vertex/index buffers per texture. Canvas is intentionally not part of the scene renderer.

## Ownership

`AudioEngine` and `AssetManager` own resources and must be cleared/closed with the Android activity lifecycle. Scenes own game content through `load`, `pause`, `resume`, and `unload`, so transitions do not leak entities or audio handles.
