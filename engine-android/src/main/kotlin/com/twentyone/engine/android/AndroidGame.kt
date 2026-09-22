package com.twentyone.engine.android

import android.app.Activity
import android.opengl.GLSurfaceView
import android.os.Bundle
import android.view.MotionEvent
import android.view.KeyEvent
import com.twentyone.engine.input.InputPhase
import com.twentyone.engine.math.Vec2
import java.util.concurrent.ConcurrentLinkedQueue

sealed interface InputEvent {
    data class Touch(val pointerId: Int, val phase: InputPhase, val position: Vec2, val timeNanos: Long) : InputEvent
    data class Key(val keyCode: Int, val down: Boolean) : InputEvent
}
class InputQueue { private val events = ConcurrentLinkedQueue<InputEvent>(); fun offer(event: InputEvent) { events.offer(event) }; fun drain(consume: (InputEvent) -> Unit) { while (true) consume(events.poll() ?: break) } }
/** Android lifecycle bridge. Subclasses only supply the GL view and may consume queued input on the game thread. */
abstract class GameActivity : Activity() {
    protected val input = InputQueue()
    protected abstract fun createGameView(): GLSurfaceView
    override fun onCreate(state: Bundle?) { super.onCreate(state); setContentView(createGameView()) }
    override fun onTouchEvent(event: MotionEvent): Boolean {
        val phase = when (event.actionMasked) { MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> InputPhase.DOWN; MotionEvent.ACTION_MOVE -> InputPhase.MOVE; MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> InputPhase.UP; else -> InputPhase.CANCEL }
        input.offer(InputEvent.Touch(event.getPointerId(event.actionIndex), phase, Vec2(event.getX(event.actionIndex), event.getY(event.actionIndex)), System.nanoTime()))
        return true
    }
    override fun dispatchKeyEvent(event: KeyEvent): Boolean { input.offer(InputEvent.Key(event.keyCode, event.action == KeyEvent.ACTION_DOWN)); return super.dispatchKeyEvent(event) }
}
