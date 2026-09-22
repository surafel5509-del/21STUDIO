package com.twentyone.engine.opengl

import com.twentyone.engine.math.Vec2

data class Particle(var position: Vec2 = Vec2(), var velocity: Vec2 = Vec2(), var age: Float = 0f, var lifetime: Float = 1f, var active: Boolean = false)

/** Fixed-capacity particle pool; spawning never allocates during gameplay. */
class ParticleEmitter(capacity: Int) {
    private val particles = Array(capacity) { Particle() }
    fun emit(position: Vec2, velocity: Vec2, lifetime: Float): Boolean {
        val particle = particles.firstOrNull { !it.active } ?: return false
        particle.position.set(position); particle.velocity.set(velocity); particle.lifetime = lifetime; particle.age = 0f; particle.active = true
        return true
    }
    fun update(deltaSeconds: Float) { particles.forEach { if (it.active) { it.age += deltaSeconds; if (it.age >= it.lifetime) it.active = false else it.position.add(it.velocity.x * deltaSeconds, it.velocity.y * deltaSeconds) } } }
    fun active(): Sequence<Particle> = particles.asSequence().filter(Particle::active)
}
