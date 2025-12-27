package io.github.stardomains3.omnichat


object ChatServiceGate {
    @Volatile
    var shouldRunService: Boolean = false
}