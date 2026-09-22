plugins { id("com.android.application"); kotlin("android") }
android { namespace = "com.twentyone.studio.sample"; compileSdk = 35
 defaultConfig { applicationId = "com.twentyone.studio.sample"; minSdk = 24; targetSdk = 35; versionCode = 1; versionName = "0.1.0" }
}
kotlin { jvmToolchain(17) }
dependencies { implementation(project(":engine-android")); implementation(project(":engine-opengl")); implementation(project(":engine-assets")); implementation(project(":engine-physics")); implementation(project(":engine-audio")); implementation(project(":engine-ui")); implementation(project(":engine-debug")) }
