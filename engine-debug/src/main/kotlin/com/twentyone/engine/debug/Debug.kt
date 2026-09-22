package com.twentyone.engine.debug

import android.util.Log
class DebugMetrics { var fps = 0f; var drawCalls = 0; var entities = 0; fun resetFrame() { drawCalls = 0 } }
object EngineLog { var enabled = true; fun d(message: String) { if (enabled) Log.d("21Engine", message) }; fun e(message: String, error: Throwable? = null) { if (enabled) Log.e("21Engine", message, error) } }
