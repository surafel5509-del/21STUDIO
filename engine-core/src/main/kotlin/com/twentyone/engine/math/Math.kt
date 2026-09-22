package com.twentyone.engine.math

import kotlin.math.cos
import kotlin.math.sin

data class Vec2(var x: Float = 0f, var y: Float = 0f) {
    fun set(other: Vec2) = apply { x = other.x; y = other.y }
    fun set(x: Float, y: Float) = apply { this.x = x; this.y = y }
    fun add(dx: Float, dy: Float) = apply { x += dx; y += dy }
    fun add(other: Vec2) = add(other.x, other.y)
    fun scale(value: Float) = apply { x *= value; y *= value }
    fun dot(other: Vec2): Float = x * other.x + y * other.y
    fun lengthSquared(): Float = dot(this)
    fun copy() = Vec2(x, y)
}

data class Transform(
    var position: Vec2 = Vec2(),
    var rotationDegrees: Float = 0f,
    var scale: Vec2 = Vec2(1f, 1f),
    var anchor: Vec2 = Vec2(.5f, .5f),
)

/** Bounded reusable pool for temporary vectors; never retain a borrowed value between frames. */
class Vec2Pool(initialSize: Int = 64) {
    private val free = ArrayDeque<Vec2>(initialSize)
    init { repeat(initialSize) { free.addLast(Vec2()) } }
    fun obtain(): Vec2 = free.removeLastOrNull() ?: Vec2()
    fun free(vector: Vec2) { vector.set(0f, 0f); free.addLast(vector) }
}

fun Vec2.rotate(degrees: Float): Vec2 {
    val radians = Math.toRadians(degrees.toDouble())
    val newX = x * cos(radians).toFloat() - y * sin(radians).toFloat()
    y = x * sin(radians).toFloat() + y * cos(radians).toFloat()
    x = newX
    return this
}
