plugins { id("com.android.library"); kotlin("android") }
android { namespace = "com.twentyone.engine.ui"; compileSdk = 35; defaultConfig { minSdk = 24 } }
kotlin { jvmToolchain(21) }
dependencies { implementation(project(":engine-core")) }
