package com.twentyone.engine.time
import com.twentyone.engine.ecs.GameSystem
import com.twentyone.engine.ecs.World
import kotlin.test.Test
import kotlin.test.assertEquals
class GameLoopTest { @Test fun accumulatesFixedSteps() { var updates = 0; val world = World().apply { addSystem(object : GameSystem { override fun update(world: World, deltaSeconds: Float) { updates++ } }) }; GameLoop(world, .1f, render = {}).frame(.25f); assertEquals(2, updates) } }
