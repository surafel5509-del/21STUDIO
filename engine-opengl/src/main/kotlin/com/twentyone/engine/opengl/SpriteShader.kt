package com.twentyone.engine.opengl

import android.opengl.GLES20

/** Default GLES 2 textured-sprite program with premultiplied-alpha compatible tinting. */
class SpriteShader : AutoCloseable {
    val program: Int = link(VERTEX, FRAGMENT)
    val positionAttribute = GLES20.glGetAttribLocation(program, "aPosition")
    val uvAttribute = GLES20.glGetAttribLocation(program, "aUv")
    val matrixUniform = GLES20.glGetUniformLocation(program, "uMatrix")
    val tintUniform = GLES20.glGetUniformLocation(program, "uTint")
    fun bind() = GLES20.glUseProgram(program)
    override fun close() { GLES20.glDeleteProgram(program) }
    private fun link(vertex: String, fragment: String): Int { val v = compile(GLES20.GL_VERTEX_SHADER, vertex); val f = compile(GLES20.GL_FRAGMENT_SHADER, fragment); return GLES20.glCreateProgram().also { GLES20.glAttachShader(it, v); GLES20.glAttachShader(it, f); GLES20.glLinkProgram(it); GLES20.glDeleteShader(v); GLES20.glDeleteShader(f) } }
    private fun compile(type: Int, source: String) = GLES20.glCreateShader(type).also { GLES20.glShaderSource(it, source); GLES20.glCompileShader(it) }
    private companion object { const val VERTEX = "attribute vec2 aPosition; attribute vec2 aUv; uniform mat4 uMatrix; varying vec2 vUv; void main(){ vUv=aUv; gl_Position=uMatrix*vec4(aPosition,0.0,1.0); }"; const val FRAGMENT = "precision mediump float; uniform sampler2D uTexture; uniform vec4 uTint; varying vec2 vUv; void main(){ gl_FragColor=texture2D(uTexture,vUv)*uTint; }" }
}
