# Public API quick reference

* `World.create`, `World.put`, `World.get`, and `World.addSystem` build ECS gameplay without engine inheritance.
* `GameLoop.frame(deltaSeconds)` advances fixed simulation and calls its renderer with interpolation.
* `SceneStack` owns load/pause/resume/unload transitions.
* `AssetManager.texture(path)` loads cached asset bitmaps off the main thread.
* `SpatialHash` provides broad-phase AABB candidate lookup.
* `EngineSurfaceView` initializes a GLES 2 renderer; `SpriteShader` is the default textured/tinted shader.
* `AudioEngine` owns SoundPool effects and one MediaPlayer music channel. Always call `close` when the game ends.
