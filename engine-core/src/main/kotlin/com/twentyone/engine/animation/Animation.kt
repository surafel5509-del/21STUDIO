package com.twentyone.engine.animation

fun interface Easing { fun apply(t: Float): Float }
object Easings { val linear = Easing { it }; val easeOutQuad = Easing { 1f - (1f - it) * (1f - it) } }
class Tween(private val duration: Float, private val easing: Easing = Easings.linear, private val apply: (Float) -> Unit) { private var elapsed = 0f; var finished = false; private set; fun update(delta: Float) { if (finished) return; elapsed = (elapsed + delta).coerceAtMost(duration); apply(easing.apply(elapsed / duration)); finished = elapsed >= duration } }
data class SpriteAnimation(val frames: List<String>, val frameDuration: Float, var elapsed: Float = 0f, var frame: Int = 0, var looping: Boolean = true) { fun update(delta: Float) { elapsed += delta; while (elapsed >= frameDuration) { elapsed -= frameDuration; frame++; if (frame == frames.size) frame = if (looping) 0 else frames.lastIndex } } }
