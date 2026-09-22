package com.twentyone.engine.save

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable data class SaveGame(val slot: String, val values: Map<String, String>)
object SaveCodec { private val json = Json { ignoreUnknownKeys = true }; fun encode(save: SaveGame) = json.encodeToString(SaveGame.serializer(), save); fun decode(source: String) = json.decodeFromString(SaveGame.serializer(), source) }
