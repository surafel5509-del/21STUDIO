pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "TwentyOne2DEngine"
include(":app", ":engine-core", ":engine-android", ":engine-opengl", ":engine-audio", ":engine-physics", ":engine-ui", ":engine-assets", ":engine-debug")
