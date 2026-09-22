plugins { id("com.android.library"); kotlin("android") }
android { namespace = "com.twentyone.engine.assets"; compileSdk = 35; defaultConfig { minSdk = 24 } }
kotlin { jvmToolchain(21) }
dependencies { implementation(project(":engine-core")) }
dependencies { implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0") }
