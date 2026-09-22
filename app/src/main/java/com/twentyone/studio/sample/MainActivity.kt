package com.twentyone.studio.sample

import android.opengl.GLSurfaceView
import com.twentyone.engine.android.GameActivity
import com.twentyone.engine.ecs.World
import com.twentyone.engine.opengl.EngineSurfaceView
import com.twentyone.engine.time.GameLoop

/** Minimal sample: a 60 Hz ECS loop driven from a GLES 2 surface. */
class MainActivity : GameActivity() {
    private val world = World()
    private var lastNanos = 0L
    private lateinit var loop: GameLoop
    override fun createGameView(): GLSurfaceView { loop = GameLoop(world, render = { /* submit sprites to SpriteBatch here */ }); return EngineSurfaceView(this) { val now = System.nanoTime(); val delta = if (lastNanos == 0L) 0f else (now - lastNanos) / 1_000_000_000f; lastNanos = now; loop.frame(delta) } }
}
