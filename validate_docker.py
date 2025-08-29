#!/usr/bin/env python3
"""
Docker Configuration Validator for Kotlin MCP Server
Validates Docker setup files and provides recommendations
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class DockerValidator:
    """Validates Docker configuration and setup"""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []

    def check_docker_files(self) -> bool:
        """Check if Docker configuration files exist and are valid"""
        print("🐳 Checking Docker configuration files...")

        # Check Dockerfile
        dockerfile_path = self.project_root / "Dockerfile"
        if not dockerfile_path.exists():
            self.issues.append("Dockerfile not found")
            return False

        # Validate Dockerfile content
        dockerfile_content = dockerfile_path.read_text()
        required_elements = [
            "FROM python:",
            "WORKDIR /app",
            "COPY requirements.txt",
            "RUN pip install",
            "COPY . .",
            "CMD",
        ]

        for element in required_elements:
            if element not in dockerfile_content:
                self.issues.append(f"Dockerfile missing: {element}")

        # Check for security best practices
        if "USER mcpuser" not in dockerfile_content:
            self.warnings.append("Dockerfile should use non-root user")

        if "HEALTHCHECK" not in dockerfile_content:
            self.recommendations.append("Add HEALTHCHECK to Dockerfile")

        print("✅ Dockerfile validation complete")
        return True

    def check_docker_compose(self) -> bool:
        """Check docker-compose.yml configuration"""
        print("🔧 Checking Docker Compose configuration...")

        compose_path = self.project_root / "docker-compose.yml"
        if not compose_path.exists():
            self.issues.append("docker-compose.yml not found")
            return False

        try:
            import yaml  # type: ignore

            with open(compose_path) as f:
                compose_config = yaml.safe_load(f)

            # Check required services
            if "services" not in compose_config:
                self.issues.append("No services defined in docker-compose.yml")
                return False

            services = compose_config["services"]

            # Check for main service
            main_service_exists = any("kotlin-mcp" in name for name in services.keys())

            if not main_service_exists:
                self.issues.append("No kotlin-mcp service found in docker-compose.yml")

            # Check for volume mounts
            for service_name, service_config in services.items():
                if "volumes" not in service_config:
                    self.warnings.append(f"Service {service_name} has no volume mounts")

            print("✅ Docker Compose validation complete")
            return True

        except ImportError:
            self.warnings.append("PyYAML not installed - skipping detailed compose validation")
            return True
        except Exception as e:
            self.issues.append(f"Error parsing docker-compose.yml: {e}")
            return False

    def check_dockerignore(self) -> bool:
        """Check .dockerignore file"""
        print("📋 Checking .dockerignore...")

        dockerignore_path = self.project_root / ".dockerignore"
        if not dockerignore_path.exists():
            self.recommendations.append("Create .dockerignore file to optimize builds")
            return True

        content = dockerignore_path.read_text()
        recommended_ignores = ["__pycache__/", ".git/", "*.log", ".venv/", ".pytest_cache/"]

        for ignore_pattern in recommended_ignores:
            if ignore_pattern not in content:
                self.recommendations.append(f"Add '{ignore_pattern}' to .dockerignore")

        print("✅ .dockerignore validation complete")
        return True

    def check_requirements_compatibility(self) -> bool:
        """Check if requirements.txt is compatible with Docker"""
        print("📦 Checking Python requirements compatibility...")

        req_path = self.project_root / "requirements.txt"
        if not req_path.exists():
            self.issues.append("requirements.txt not found")
            return False

        content = req_path.read_text()

        # Check for potentially problematic packages
        problematic_packages = {
            "opencv-python": "Consider using opencv-python-headless for Docker",
            "tkinter": "GUI packages may not work in headless containers",
            "pyqt": "GUI packages may not work in headless containers",
        }

        for package, warning in problematic_packages.items():
            if package in content.lower():
                self.warnings.append(f"{package}: {warning}")

        # Check for version pinning
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("#")
        ]
        unpinned = [
            line for line in lines if ">=" not in line and "==" not in line and "~=" not in line
        ]

        if unpinned:
            self.recommendations.append(f"Consider pinning versions for: {', '.join(unpinned[:3])}")

        print("✅ Requirements compatibility check complete")
        return True

    def check_docker_installation(self) -> Tuple[bool, str]:
        """Check if Docker is installed and accessible"""
        print("🔍 Checking Docker installation...")

        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Docker found: {version}")
                return True, version
            else:
                return False, "Docker command failed"
        except FileNotFoundError:
            return False, "Docker not installed"
        except subprocess.TimeoutExpired:
            return False, "Docker command timed out"
        except Exception as e:
            return False, f"Error checking Docker: {e}"

    def check_docker_compose_installation(self) -> Tuple[bool, str]:
        """Check if Docker Compose is available"""
        print("🔧 Checking Docker Compose installation...")

        # Try docker-compose command
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Docker Compose found: {version}")
                return True, version
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try docker compose command (newer versions)
        try:
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Docker Compose (plugin) found: {version}")
                return True, version
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return False, "Docker Compose not found"

    def validate_build_context(self) -> bool:
        """Validate Docker build context"""
        print("📁 Validating build context...")

        required_files = ["kotlin_mcp_server.py", "requirements.txt", "pyproject.toml"]

        for file_name in required_files:
            if not (self.project_root / file_name).exists():
                self.issues.append(f"Required file missing: {file_name}")

        # Check for large files that should be ignored
        large_dirs = ["__pycache__", ".git", "htmlcov", ".pytest_cache"]
        for dir_name in large_dirs:
            if (self.project_root / dir_name).exists():
                self.recommendations.append(f"Ensure {dir_name} is in .dockerignore")

        print("✅ Build context validation complete")
        return len(self.issues) == 0

    def generate_setup_commands(self) -> List[str]:
        """Generate Docker setup commands based on platform"""
        commands = []

        # Detect platform
        import platform

        system = platform.system().lower()

        if system == "darwin":  # macOS
            commands.extend(
                [
                    "# macOS Docker Installation:",
                    "brew install --cask docker",
                    "# Or download from: https://docs.docker.com/desktop/mac/install/",
                    "",
                ]
            )
        elif system == "linux":
            commands.extend(
                [
                    "# Linux Docker Installation:",
                    "sudo apt update",
                    "sudo apt install docker.io docker-compose",
                    "sudo systemctl start docker",
                    "sudo systemctl enable docker",
                    "sudo usermod -aG docker $USER",
                    "# Log out and back in for group changes to take effect",
                    "",
                ]
            )
        elif system == "windows":
            commands.extend(
                [
                    "# Windows Docker Installation:",
                    "# Download Docker Desktop from: https://docs.docker.com/desktop/windows/install/",
                    "# Or use chocolatey: choco install docker-desktop",
                    "",
                ]
            )

        commands.extend(
            [
                "# Build and run the Kotlin MCP Server:",
                "./docker-setup.sh build",
                "./docker-setup.sh start",
                "",
                "# Or manually:",
                "docker build -t kotlin-mcp-server .",
                "docker-compose up -d kotlin-mcp-server",
            ]
        )

        return commands

    def run_validation(self) -> bool:
        """Run complete Docker validation"""
        print("🚀 Starting Docker validation for Kotlin MCP Server")
        print("=" * 60)

        success = True

        # Check Docker installation
        docker_installed, docker_msg = self.check_docker_installation()
        if not docker_installed:
            self.warnings.append(f"Docker: {docker_msg}")

        compose_installed, compose_msg = self.check_docker_compose_installation()
        if not compose_installed:
            self.warnings.append(f"Docker Compose: {compose_msg}")

        # Check configuration files
        success &= self.check_docker_files()
        success &= self.check_docker_compose()
        success &= self.check_dockerignore()
        success &= self.check_requirements_compatibility()
        success &= self.validate_build_context()

        # Print results
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)

        if self.issues:
            print("❌ ISSUES FOUND:")
            for issue in self.issues:
                print(f"   • {issue}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        if self.recommendations:
            print("💡 RECOMMENDATIONS:")
            for rec in self.recommendations:
                print(f"   • {rec}")
            print()

        if not docker_installed or not compose_installed:
            print("🛠️  SETUP COMMANDS:")
            for cmd in self.generate_setup_commands():
                print(f"   {cmd}")
            print()

        if success and not self.issues:
            print("🎉 Docker configuration is valid!")
            if docker_installed and compose_installed:
                print("✅ Ready to build and run with Docker!")
            else:
                print("📦 Install Docker to proceed with containerized deployment")
        else:
            print("🔧 Please fix the issues above before proceeding")

        return success and not self.issues


def main() -> int:
    """Main validation function"""
    validator = DockerValidator()
    success = validator.run_validation()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
