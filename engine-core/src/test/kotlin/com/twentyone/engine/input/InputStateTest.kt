package com.twentyone.engine.input

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class InputStateTest {
    @Test fun actionMapTracksPressedAndHeldKeys() {
        val input = InputState()
        input.bind(ActionBinding(action = "jump", keyCodes = setOf(62)))
        input.onKey(62, true)
        assertTrue(input.wasPressed("jump"))
        assertTrue(input.isDown("jump"))
        input.beginFrame()
        assertFalse(input.wasPressed("jump"))
        assertTrue(input.isDown("jump"))
        input.onKey(62, false)
        assertFalse(input.isDown("jump"))
    }
}
