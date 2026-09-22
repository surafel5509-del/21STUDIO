package com.twentyone.engine.time

import com.twentyone.engine.ecs.World

/** Fixed-rate simulation driver. The host invokes [frame] from its game thread. */
class GameLoop(private val world: World, private val fixedStepSeconds: Float = 1f / 60f, private val maxFrameSeconds: Float = .25f, private val beforeUpdate: () -> Unit = {}, private val render: (interpolation: Float) -> Unit) {
    private var accumulator = 0f
    private var paused = false
    fun pause() { paused = true }
    fun resume() { paused = false }
    fun frame(deltaSeconds: Float) { if (paused) return; accumulator += deltaSeconds.coerceIn(0f, maxFrameSeconds); while (accumulator >= fixedStepSeconds) { beforeUpdate(); world.update(fixedStepSeconds); accumulator -= fixedStepSeconds }; render(accumulator / fixedStepSeconds) }
}
