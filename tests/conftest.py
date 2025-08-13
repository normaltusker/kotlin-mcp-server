#!/usr/bin/env python3
"""
Shared test configuration and fixtures for all test modules
"""

import tempfile
from pathlib import Path

import pytest

from kotlin_mcp_server import KotlinMCPServer


@pytest.fixture(scope="session")
def temp_project_dir():
    """Create a temporary project directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup handled by tempfile


@pytest.fixture
def server_instance():
    """Create a fresh server instance for each test"""
    server = KotlinMCPServer("test-server")
    server.set_project_path(tempfile.mkdtemp())
    return server


@pytest.fixture
def sample_kotlin_file_content():
    """Sample Kotlin file content for testing"""
    return """
package com.example.test

class TestClass {
    fun doSomething(): String {
        return "Hello, World!"
    }
}
"""


@pytest.fixture
def sample_android_manifest():
    """Sample Android manifest content for testing"""
    return """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.test">

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>
</manifest>"""


@pytest.fixture
def sample_gradle_build():
    """Sample Gradle build file content for testing"""
    return """
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.test"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.8.0'
    implementation 'androidx.appcompat:appcompat:1.5.0'
    implementation 'com.google.android.material:material:1.6.1'
}
"""
