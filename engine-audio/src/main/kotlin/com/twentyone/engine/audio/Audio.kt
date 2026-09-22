package com.twentyone.engine.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.media.SoundPool

class AudioEngine(context: Context) : AutoCloseable { private val sounds = SoundPool.Builder().setMaxStreams(16).setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).build()).build(); private var music: MediaPlayer? = null; fun loadSound(resId: Int) = sounds.load(context, resId, 1); fun play(sound: Int, volume: Float = 1f, pitch: Float = 1f, loop: Boolean = false) = sounds.play(sound, volume, volume, 1, if(loop) -1 else 0, pitch); fun playMusic(resId: Int, loop: Boolean = true) { music?.release(); music = MediaPlayer.create(context, resId).apply { isLooping = loop; start() } }; fun pauseMusic() { music?.pause() }; override fun close() { music?.release(); sounds.release() } }
