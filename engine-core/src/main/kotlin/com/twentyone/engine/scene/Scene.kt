package com.twentyone.engine.scene

interface Scene { fun load() {}; fun unload() {}; fun pause() {}; fun resume() {}; fun update(deltaSeconds: Float) {} }
class SceneStack { private val scenes = ArrayDeque<Scene>(); val current get() = scenes.lastOrNull(); fun push(scene: Scene) { current?.pause(); scenes.addLast(scene); scene.load(); scene.resume() }; fun pop() { scenes.removeLastOrNull()?.unload(); current?.resume() }; fun replace(scene: Scene) { pop(); push(scene) }; fun update(deltaSeconds: Float) { current?.update(deltaSeconds) } }
