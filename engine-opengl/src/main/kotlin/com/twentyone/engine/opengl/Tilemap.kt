package com.twentyone.engine.opengl

/** Immutable tile layer data. A negative tile value denotes an empty cell. */
class TileLayer(val width: Int, val height: Int, val tiles: IntArray, val z: Int = 0) {
    init { require(width > 0 && height > 0 && tiles.size == width * height) }
    operator fun get(x: Int, y: Int): Int = if (x !in 0 until width || y !in 0 until height) -1 else tiles[y * width + x]
}

data class Tilemap(val tileWidth: Float, val tileHeight: Float, val layers: List<TileLayer>)

/** Computes visible tile ranges before submitting tiles to a sprite batch. */
class TilemapCuller {
    fun visible(layer: TileLayer, left: Int, bottom: Int, right: Int, top: Int): Sequence<Triple<Int, Int, Int>> = sequence {
        for (y in bottom.coerceAtLeast(0)..top.coerceAtMost(layer.height - 1)) {
            for (x in left.coerceAtLeast(0)..right.coerceAtMost(layer.width - 1)) {
                val tile = layer[x, y]
                if (tile >= 0) yield(Triple(x, y, tile))
            }
        }
    }
}
