package com.twentyone.engine.event

import java.util.concurrent.ConcurrentLinkedQueue

/** Marker for events transferred between platform, game, and render boundaries. */
interface EngineEvent

/**
 * Single-producer/multi-consumer friendly event queue. Events are drained at a deterministic
 * fixed-update boundary, preventing Android callbacks from mutating gameplay state directly.
 */
class EventBus {
    private val pending = ConcurrentLinkedQueue<EngineEvent>()
    private val listeners = mutableMapOf<Class<out EngineEvent>, MutableList<(EngineEvent) -> Unit>>()

    fun post(event: EngineEvent) { pending.offer(event) }

    inline fun <reified T : EngineEvent> subscribe(noinline listener: (T) -> Unit): AutoCloseable =
        subscribe(T::class.java, listener)

    fun <T : EngineEvent> subscribe(type: Class<T>, listener: (T) -> Unit): AutoCloseable {
        @Suppress("UNCHECKED_CAST")
        val erased: (EngineEvent) -> Unit = { listener(it as T) }
        val list = listeners.getOrPut(type) { mutableListOf() }
        list += erased
        return AutoCloseable { list.remove(erased) }
    }

    fun dispatch() {
        while (true) {
            val event = pending.poll() ?: return
            listeners[event.javaClass]?.toList()?.forEach { it(event) }
        }
    }
}

/** Explicit registry for long-lived engine services; use scene-owned resources for everything else. */
class ServiceRegistry {
    private val services = mutableMapOf<Class<*>, Any>()
    fun <T : Any> register(type: Class<T>, service: T) { require(type !in services) { "Service ${type.name} is already registered" }; services[type] = service }
    fun <T : Any> get(type: Class<T>): T = type.cast(services[type] ?: error("Service ${type.name} is not registered"))
    inline fun <reified T : Any> get(): T = get(T::class.java)
}
