package com.twentyone.engine.opengl

import android.content.Context
import android.opengl.GLES20
import android.opengl.GLSurfaceView
import android.opengl.Matrix
import com.twentyone.engine.math.Transform
import javax.microedition.khronos.egl.EGLConfig
import javax.microedition.khronos.opengles.GL10

data class Camera(var x: Float = 0f, var y: Float = 0f, var zoom: Float = 1f, var rotation: Float = 0f, var viewportWidth: Float = 1f, var viewportHeight: Float = 1f) { fun matrix(out: FloatArray) { Matrix.setIdentityM(out, 0); Matrix.translateM(out, 0, -x, -y, 0f); Matrix.scaleM(out, 0, zoom, zoom, 1f); Matrix.rotateM(out, 0, -rotation, 0f, 0f, 1f) } }
data class Sprite(val texture: Int, val transform: Transform, val z: Int = 0, val tint: Int = 0xffffffff.toInt())
/** Render queue sorted by texture then layer, suitable for a GPU sprite batch implementation. */
class SpriteBatch { private val sprites = mutableListOf<Sprite>(); var drawCalls = 0; fun submit(sprite: Sprite) { sprites += sprite }; fun flush() { sprites.sortWith(compareBy<Sprite> { it.texture }.thenBy { it.z }); if (sprites.isNotEmpty()) drawCalls++; sprites.clear() } }
class EngineSurfaceView(context: Context, private val renderFrame: () -> Unit) : GLSurfaceView(context) { init { setEGLContextClientVersion(2); setRenderer(object : Renderer { override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) { GLES20.glClearColor(.04f, .06f, .1f, 1f) }; override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) { GLES20.glViewport(0, 0, width, height) }; override fun onDrawFrame(gl: GL10?) { GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT); renderFrame() } }); renderMode = RENDERMODE_CONTINUOUSLY } }
