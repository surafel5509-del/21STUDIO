package com.twentyone.engine.ecs

import java.util.concurrent.atomic.AtomicInteger

/** A stable, opaque identifier. IDs are never recycled during a [World] lifetime. */
@JvmInline
value class Entity(val id: Int)

/** Marker for data-only ECS components. */
interface Component

/** Logic unit executed once per fixed simulation tick. */
interface GameSystem {
    fun update(world: World, deltaSeconds: Float)
}

/**
 * Data-oriented entity/component store.
 *
 * Components are indexed by concrete runtime type. Queries return a snapshot sequence of matching
 * entity IDs, which makes it safe for systems to add or remove components while iterating.
 */
class World {
    private val nextId = AtomicInteger(1)
    private val alive = mutableSetOf<Int>()
    private val stores = mutableMapOf<Class<out Component>, MutableMap<Int, Component>>()
    private val systems = mutableListOf<GameSystem>()

    fun create(): Entity = Entity(nextId.getAndIncrement()).also { alive += it.id }

    fun destroy(entity: Entity) {
        if (!alive.remove(entity.id)) return
        stores.values.forEach { it.remove(entity.id) }
    }

    fun isAlive(entity: Entity): Boolean = entity.id in alive
    fun entityCount(): Int = alive.size
    fun addSystem(system: GameSystem): World = apply { systems += system }
    fun removeSystem(system: GameSystem): Boolean = systems.remove(system)
    fun update(deltaSeconds: Float) = systems.toList().forEach { it.update(this, deltaSeconds) }

    inline fun <reified T : Component> put(entity: Entity, component: T): T =
        put(entity, T::class.java, component)

    inline fun <reified T : Component> get(entity: Entity): T? = get(entity, T::class.java)
    inline fun <reified T : Component> remove(entity: Entity): T? = remove(entity, T::class.java)
    inline fun <reified T : Component> has(entity: Entity): Boolean = get<T>(entity) != null
    inline fun <reified T : Component> entitiesWith(): List<Entity> = entitiesWith(T::class.java)

    inline fun <reified A : Component, reified B : Component> query(): List<Entity> =
        entitiesWith(A::class.java).filter { get<B>(it) != null }

    fun <T : Component> put(entity: Entity, type: Class<T>, component: T): T {
        check(isAlive(entity)) { "Cannot attach ${type.simpleName} to dead entity ${entity.id}" }
        store(type)[entity.id] = component
        return component
    }

    fun <T : Component> get(entity: Entity, type: Class<T>): T? = storeOrNull(type)?.get(entity.id)?.let(type::cast)
    fun <T : Component> remove(entity: Entity, type: Class<T>): T? = storeOrNull(type)?.remove(entity.id)?.let(type::cast)
    fun <T : Component> entitiesWith(type: Class<T>): List<Entity> = storeOrNull(type)?.keys?.filter(alive::contains)?.map(::Entity) ?: emptyList()

    @Suppress("UNCHECKED_CAST")
    private fun <T : Component> store(type: Class<T>): MutableMap<Int, Component> =
        stores.getOrPut(type) { mutableMapOf() }

    @Suppress("UNCHECKED_CAST")
    private fun <T : Component> storeOrNull(type: Class<T>): MutableMap<Int, Component>? = stores[type]
}
