// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.0.2" apply false
    id("com.android.library") version "8.0.2" apply false
    id("org.jetbrains.kotlin.android") version "1.8.0" apply false
    id("com.google.dagger.hilt.android") version "2.45" apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
        maven { url = uri("https://maven.google.com") }
    }
}

// تحديد الإصدارات والإعدادات المشتركة
ext {
    // SDK Versions
    set("compileSdk", 34)
    set("targetSdk", 34)
    set("minSdk", 24)
    set("versionCode", 1)
    set("versionName", "0.1.0-alpha")

    // Library Versions
    set("kotlinVersion", "1.8.0")
    set("androidxCoreVersion", "1.10.1")
    set("appCompatVersion", "1.6.1")
    set("materialVersion", "1.9.0")
    set("lifecycleVersion", "2.6.1")
    set("roomVersion", "2.5.2")
    set("retrofitVersion", "2.9.0")
    set("okHttpVersion", "4.11.0")
    set("hiltVersion", "2.45")
    set("coroutinesVersion", "1.7.1")
    set("composeVersion", "1.5.0")
    set("exoPlayerVersion", "1.1.1")
    set("ffmpegVersion", "4.4-LTS")
    set("tensorflowVersion", "2.10.0")
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
