# TwentyOne 2D Engine

A modular Kotlin Android 2D game-engine foundation for API 24+ games. Rendering uses a GLES 2 surface, not Canvas. The project targets API 35 and keeps the simulation deterministic through a fixed 60 Hz game loop.

## Modules

| Module | Responsibility |
| --- | --- |
| `engine-core` | ECS, math, fixed timestep loop, scenes, animation, saves |
| `engine-android` | activity lifecycle and concurrent multi-touch input queue |
| `engine-opengl` | GLES surface, camera, shader lifecycle and batched sprite ordering |
| `engine-assets` | coroutine-backed asset bitmap cache |
| `engine-physics` | colliders, rigid-body data, AABB testing, spatial hash |
| `engine-audio` | SoundPool effects and MediaPlayer music |
| `engine-ui` | allocation-light in-game retained UI nodes |
| `engine-debug` | metrics and Android log bridge |
| `app` | GLES sample application |

## Build

```bash
gradle :engine-core:test
gradle :app:assembleDebug
```

An Android SDK with platform 35 is required for Android modules. Open the repository root as a standalone Gradle project in Android Studio.

## Usage

```kotlin
val world = World()
val player = world.create()
world.put(player, Rigidbody(velocity = Vec2(3f, 0f)))
world.addSystem(object : GameSystem {
    override fun update(world: World, deltaSeconds: Float) { /* game logic */ }
})

val loop = GameLoop(world) { interpolation -> spriteBatch.flush() }
val saveJson = SaveCodec.encode(SaveGame("slot-1", mapOf("coins" to "15")))
```

Load a texture asynchronously with `assets.texture("sprites/player.png")`; use `AudioEngine.play` for a SoundPool effect. `InputQueue.drain` must be called from the game thread, preserving Android UI-thread input ownership.

## Performance notes

* Systems receive fixed delta time; avoid blocking and allocations inside `update`.
* Reuse vectors through `Vec2Pool` for temporary work and clear `SpriteBatch` each frame.
* Use texture atlases in production and sort transparent sprites by layer as required by your art pipeline.
* Keep physics hash cells close to a typical collider size; layer expensive systems behind culling.

See [architecture.md](docs/architecture.md) for ownership and extension points.

## Delivery plan

The engine is being built in testable production milestones. The current code implements the
foundation layer; the renderer, gameplay, and tooling expansions are tracked explicitly in the
[production roadmap](docs/roadmap.md). This avoids presenting stubs as completed editor features.
