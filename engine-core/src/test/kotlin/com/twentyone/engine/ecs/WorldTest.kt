package com.twentyone.engine.ecs

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse

private data class Health(val points: Int) : Component
private data class Player(val value: Unit = Unit) : Component

class WorldTest {
    @Test fun storesQueriesAndDestroysComponents() {
        val world = World()
        val entity = world.create()
        world.put(entity, Health(10))
        world.put(entity, Player())
        assertEquals(10, world.get<Health>(entity)?.points)
        assertEquals(listOf(entity), world.query<Health, Player>())
        world.destroy(entity)
        assertFalse(world.isAlive(entity))
        assertEquals(0, world.entitiesWith<Health>().size)
    }

    @Test fun runsRegisteredSystems() {
        var calls = 0
        val world = World().addSystem(object : GameSystem {
            override fun update(world: World, deltaSeconds: Float) { calls++ }
        })
        world.update(.016f)
        assertEquals(1, calls)
    }
}
