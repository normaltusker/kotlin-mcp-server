#!/usr/bin/env python3
"""Intelligent UI Testing Tools.

Scaffolds Android UI testing environments for Espresso and Compose with
optional accessibility and screenshot testing support.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentUITestSetupTool(IntelligentToolBase):
    """Set up UI testing infrastructure with smart Gradle updates."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        framework = arguments.get("test_framework", "espresso")
        include_accessibility = arguments.get("include_accessibility", False)
        include_screenshot = arguments.get("include_screenshot_testing", False)

        build_file = self._ensure_build_file()
        self._ensure_dependencies(
            build_file, framework, include_accessibility, include_screenshot
        )

        created_files = self._scaffold_tests(framework)

        return {
            "success": True,
            "framework": framework,
            "accessibility": include_accessibility,
            "screenshot_testing": include_screenshot,
            "updated_build_file": str(build_file.relative_to(self.project_path)),
            "created_files": created_files,
        }

    def _ensure_build_file(self) -> Path:
        candidates = ["build.gradle.kts", "build.gradle"]
        for name in candidates:
            path = self.project_path / name
            if path.exists():
                return path
        path = self.project_path / "build.gradle"
        path.write_text(
            "plugins {\n    id 'com.android.application'\n}\n\nandroid {}\n\ndependencies {}\n"
        )
        return path

    def _ensure_dependencies(
        self,
        build_file: Path,
        framework: str,
        include_accessibility: bool,
        include_screenshot: bool,
    ) -> None:
        content = build_file.read_text()

        def add_dependency(dep: str) -> None:
            nonlocal content
            if dep not in content:
                if "dependencies {" in content:
                    content = content.replace(
                        "dependencies {", f"dependencies {{\n    {dep}"
                    )
                else:
                    content += f"\ndependencies {{\n    {dep}\n}}\n"

        if framework in ("espresso", "both"):
            add_dependency(
                'androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")'
            )
        if framework in ("compose", "both"):
            add_dependency(
                'androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.0")'
            )
            add_dependency(
                'debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.0")'
            )
        if include_accessibility:
            add_dependency(
                'androidTestImplementation("androidx.test.espresso:espresso-accessibility:3.5.1")'
            )
        if include_screenshot:
            add_dependency(
                'androidTestImplementation("com.karumi:shot-android:5.15.0")'
            )

        build_file.write_text(content)

    def _scaffold_tests(self, framework: str) -> List[str]:
        test_dir = (
            self.project_path
            / "src"
            / "androidTest"
            / "kotlin"
            / "com"
            / "example"
            / "uitest"
        )
        test_dir.mkdir(parents=True, exist_ok=True)
        created: List[str] = []

        if framework in ("espresso", "both"):
            file_path = test_dir / "EspressoSampleTest.kt"
            if not file_path.exists():
                file_path.write_text(self._espresso_sample())
                created.append(str(file_path.relative_to(self.project_path)))

        if framework in ("compose", "both"):
            file_path = test_dir / "ComposeSampleTest.kt"
            if not file_path.exists():
                file_path.write_text(self._compose_sample())
                created.append(str(file_path.relative_to(self.project_path)))

        return created

    def _espresso_sample(self) -> str:
        return (
            "package com.example.uitest\n\n"
            "import androidx.test.ext.junit.runners.AndroidJUnit4\n"
            "import androidx.test.rule.ActivityTestRule\n"
            "import org.junit.Rule\n"
            "import org.junit.Test\n"
            "import org.junit.runner.RunWith\n"
            "import androidx.test.espresso.Espresso.onView\n"
            "import androidx.test.espresso.assertion.ViewAssertions.matches\n"
            "import androidx.test.espresso.matcher.ViewMatchers.isDisplayed\n"
            "import androidx.test.espresso.matcher.ViewMatchers.withContentDescription\n\n"
            "@RunWith(AndroidJUnit4::class)\n"
            "class EspressoSampleTest {\n"
            "    @get:Rule val rule = ActivityTestRule(MainActivity::class.java)\n"
            "    @Test fun sample() {\n"
            "        onView(withContentDescription(\"app\")).check(matches(isDisplayed()))\n"
            "    }\n"
            "}\n"
        )

    def _compose_sample(self) -> str:
        return (
            "package com.example.uitest\n\n"
            "import androidx.compose.ui.test.junit4.createComposeRule\n"
            "import androidx.compose.ui.test.onNodeWithText\n"
            "import org.junit.Rule\n"
            "import org.junit.Test\n\n"
            "class ComposeSampleTest {\n"
            "    @get:Rule val composeTestRule = createComposeRule()\n"
            "    @Test fun sample() {\n"
            "        composeTestRule.setContent { }\n"
            "        composeTestRule.onNodeWithText(\"Hello\").assertExists()\n"
            "    }\n"
            "}\n"
        )
