package com.twentyone.engine.ui

import com.twentyone.engine.math.Vec2

data class UiRect(var position: Vec2 = Vec2(), var size: Vec2 = Vec2()) { fun contains(point: Vec2) = point.x in position.x..position.x + size.x && point.y in position.y..position.y + size.y }
open class UiNode(val bounds: UiRect = UiRect()) { val children = mutableListOf<UiNode>(); var visible = true; fun add(child: UiNode) = apply { children += child } }
class Button(bounds: UiRect, private val onClick: () -> Unit) : UiNode(bounds) { fun touch(point: Vec2): Boolean { if (visible && bounds.contains(point)) { onClick(); return true }; return false } }
class Label(var text: String, bounds: UiRect = UiRect()) : UiNode(bounds)
