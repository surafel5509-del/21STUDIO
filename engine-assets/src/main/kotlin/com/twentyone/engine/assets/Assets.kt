package com.twentyone.engine.assets

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.ConcurrentHashMap

data class AssetProgress(val completed: Int, val total: Int) { val fraction: Float get() = if (total == 0) 1f else completed.toFloat() / total }

data class TextureRegion(val texturePath: String, val x: Int = 0, val y: Int = 0, val width: Int, val height: Int)
class AssetManager(private val context: Context) { private val bitmaps = ConcurrentHashMap<String, Bitmap>(); suspend fun texture(path: String): Bitmap = bitmaps[path] ?: withContext(Dispatchers.IO) { context.assets.open(path).use { stream -> requireNotNull(BitmapFactory.decodeStream(stream)) { "Unsupported bitmap asset: $path" } }.also { bitmaps[path] = it } }; suspend fun preload(paths: Collection<String>, onProgress: (AssetProgress) -> Unit = {}) { paths.forEachIndexed { index, path -> texture(path); onProgress(AssetProgress(index + 1, paths.size)) } }; fun unload(path: String) { bitmaps.remove(path)?.recycle() }; fun clear() { bitmaps.values.forEach(Bitmap::recycle); bitmaps.clear() } }
