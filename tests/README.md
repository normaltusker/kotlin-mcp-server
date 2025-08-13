# Kotlin MCP Server - Test Suite

This directory contains the modular test suite for the Kotlin MCP Server project.

## 🚀 Quick Start

Run all tests:
```bash
python3 -m pytest tests/ -v
```

Run tests with coverage:
```bash
python3 -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term
```

Run specific test modules:
```bash
# Test only AI functionality
python3 -m pytest tests/ai/ -v

# Test only Gradle tools
python3 -m pytest tests/tools/test_gradle_tools.py -v

# Test only security utilities
python3 -m pytest tests/utils/ -v
```

## 📁 Test Structure

```
tests/
├── conftest.py                        # Shared fixtures and configuration
├── test_server_core.py                # Core server functionality
├── test_api_tools.py                  # External API integration
├── test_ui_layout_tools.py            # UI/Layout components
├── ai/
│   └── test_llm_integration.py        # AI/LLM features
├── generators/
│   └── test_kotlin_generator.py       # Code generation
├── tools/
│   ├── test_gradle_tools.py           # Gradle build system
│   ├── test_project_analysis.py       # Code analysis & quality
│   └── test_build_optimization.py     # Architecture setup
└── utils/
    └── test_security.py               # Security utilities
```

## 📊 Coverage Information

Current test coverage: **34.74%**

### Module Coverage:
- **AI/LLM Integration**: 76.38%
- **Security Utils**: 66.67%
- **Core Server**: 41.50%
- **Gradle Tools**: 38.10%
- **Kotlin Generator**: 36.96%
- **Project Analysis**: 31.58%
- **Build Optimization**: 11.82%

## 🧪 Test Categories

### Core Functionality
- Server initialization and configuration
- Tool registration and routing
- Error handling and edge cases

### Code Generation
- Kotlin class/interface/data class creation
- Android component generation (Activity, Fragment, Service, etc.)
- UI component creation (layouts, views, drawables)

### Build & Project Management
- Gradle tasks and dependency management
- Project analysis and code quality tools
- Architecture setup (MVVM, Room, Retrofit, etc.)

### AI Integration
- AI-powered code generation
- Code review and analysis
- Refactoring suggestions
- Documentation generation

### Security
- Data encryption/decryption
- Password hashing and verification
- Secure storage configuration

## 🔧 Running Specific Tests

### By Module:
```bash
# AI functionality
pytest tests/ai/ -v

# Kotlin generation
pytest tests/generators/ -v

# Build tools
pytest tests/tools/ -v

# Security utilities
pytest tests/utils/ -v
```

### By Test Name Pattern:
```bash
# All tests containing "kotlin"
pytest tests/ -k "kotlin" -v

# All tests containing "security"
pytest tests/ -k "security" -v

# All tests containing "gradle"
pytest tests/ -k "gradle" -v
```

### With Coverage for Specific Modules:
```bash
# Coverage for AI module only
pytest tests/ai/ --cov=ai --cov-report=term

# Coverage for tools only
pytest tests/tools/ --cov=tools --cov-report=term
```

## 📝 Adding New Tests

1. **Choose the appropriate directory** based on functionality
2. **Follow the naming convention**: `test_[module_name].py`
3. **Use the shared fixtures** from `conftest.py`
4. **Follow the test class pattern**: `TestModuleName`
5. **Add comprehensive test cases** including edge cases and error scenarios

### Example Test Structure:
```python
import pytest
from kotlin_mcp_server import KotlinMCPServer

class TestNewModule:
    @pytest.fixture
    def server(self):
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_basic_functionality(self, server):
        result = await server.handle_call_tool("tool_name", {"arg": "value"})
        assert "content" in result
        assert isinstance(result["content"], list)
```

## 🎯 Next Steps

1. **Increase coverage** for build optimization and project analysis modules
2. **Add integration tests** for complex workflows
3. **Add performance benchmarks** for tool execution
4. **Mock external dependencies** to improve test isolation
5. **Add parameterized tests** for tool variations

## 📚 Documentation

- See `TEST_REORGANIZATION_SUMMARY.md` for detailed reorganization information
- Check individual test files for specific functionality coverage
- Review `conftest.py` for available shared fixtures and utilities
