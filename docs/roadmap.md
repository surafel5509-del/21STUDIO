# Production roadmap

This repository is structured as a long-lived engine codebase rather than a claim of feature parity
with a mature editor-led engine. The following roadmap makes the next implementation increments
reviewable and testable.

## Foundation (implemented)

- Kotlin multi-module build with an API 24 Android target.
- Fixed-step ECS simulation, scene lifecycle, events/services, input state and save codec.
- GLES2 surface/shader ownership, camera and ordered sprite submission API.
- AABB/circle contact generation, impulses, triggers, layers, raycast API, spatial hash.
- Asset cache/preload API, SoundPool/MediaPlayer wrapper, retained UI primitives and debug metrics.

## Renderer milestone

1. GL texture upload/destruction queue bound to the render thread.
2. Dynamic VBO/IBO sprite batch with atlas regions, scissor/viewport stack, blend states and draw-call tests.
3. Bitmap font atlas generation, TTF rasterization cache, tilemesh VBO cache, post-process chain and GPU debug overlays.

## Gameplay milestone

1. Collision enter/stay/exit tracking, swept collision/continuous mode, joints and deterministic broad-phase benchmarks.
2. Input gestures (tap, long press, drag, swipe, pinch), gamepad mapping and rebinding persistence.
3. Animation graph/state-machine authoring, timelines, prefab/entity serialization and hot-reload development protocol.

## Tooling milestone

1. Android Studio sample suite: platformer, top-down RPG and shooter.
2. Golden-frame instrumentation tests on emulators, performance traces and memory-allocation budgets.
3. Optional plugins for Box2D, Oboe and cloud-save providers with isolated dependencies.

Each milestone requires public API documentation, unit tests, Android instrumentation coverage where
platform behavior is involved, and a sample-game integration before it is considered complete.
