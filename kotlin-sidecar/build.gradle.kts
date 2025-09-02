plugins {
    kotlin("jvm") version "1.9.10"
    application
    id("com.diffplug.spotless") version "6.20.0"
    id("com.github.johnrengelman.shadow") version "8.1.1"
}

group = "com.kotlinmcp"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
    implementation("com.google.code.gson:gson:2.10.1")
    implementation("org.jetbrains.kotlinx:kotlinx-cli:0.3.6")

    // Kotlin Analysis API
    implementation("org.jetbrains.kotlin:kotlin-compiler-embeddable:1.9.10")
    implementation("org.jetbrains.kotlin:kotlin-analysis-api-standalone:1.9.10")

    // Diff utils
    implementation("io.github.java-diff-utils:java-diff-utils:4.12")

    // Logging
    implementation("org.slf4j:slf4j-simple:2.0.7")

    // Test
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

application {
    mainClass.set("com.kotlinmcp.sidecar.MainKt")
}

tasks.shadowJar {
    archiveBaseName.set("kotlin-sidecar")
    archiveClassifier.set("")
    archiveVersion.set("")
    manifest {
        attributes["Main-Class"] = "com.kotlinmcp.sidecar.MainKt"
    }
}

tasks.test {
    useJUnitPlatform()
}

spotless {
    kotlin {
        ktlint("0.50.0")
    }
}

kotlin {
    jvmToolchain(17)
}

tasks.register<JavaExec>("runSidecar") {
    group = "application"
    classpath = sourceSets.main.get().runtimeClasspath
    mainClass.set("com.kotlinmcp.sidecar.MainKt")
}
