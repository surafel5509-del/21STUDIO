package com.twentyone.engine.input

import com.twentyone.engine.math.Vec2

enum class InputPhase { DOWN, MOVE, UP, CANCEL }
data class PointerEvent(val pointerId: Int, val phase: InputPhase, val position: Vec2, val timeNanos: Long)
data class ActionBinding(val action: String, val keyCodes: Set<Int> = emptySet(), val pointerPhases: Set<InputPhase> = emptySet())

/** Frame-local input state and declarative action map, independent of Android APIs. */
class InputState {
    private val downKeys = mutableSetOf<Int>()
    private val pressedKeys = mutableSetOf<Int>()
    private val pointers = mutableMapOf<Int, Vec2>()
    private val bindings = mutableMapOf<String, ActionBinding>()
    fun beginFrame() { pressedKeys.clear() }
    fun bind(binding: ActionBinding) { bindings[binding.action] = binding }
    fun onKey(keyCode: Int, down: Boolean) { if (down && downKeys.add(keyCode)) pressedKeys += keyCode; if (!down) downKeys -= keyCode }
    fun onPointer(event: PointerEvent) { if (event.phase == InputPhase.UP || event.phase == InputPhase.CANCEL) pointers.remove(event.pointerId) else pointers[event.pointerId] = event.position.copy() }
    fun isDown(action: String): Boolean = bindings[action]?.keyCodes?.any(downKeys::contains) == true
    fun wasPressed(action: String): Boolean = bindings[action]?.keyCodes?.any(pressedKeys::contains) == true
    fun pointer(id: Int): Vec2? = pointers[id]?.copy()
    fun activePointerCount(): Int = pointers.size
}
