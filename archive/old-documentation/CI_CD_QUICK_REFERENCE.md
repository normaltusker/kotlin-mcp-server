# CI/CD Quick Reference Guide

## 🚀 Available GitHub Actions Workflows

### 1. **Main CI** (`ci.yml`)
**Triggers:** Push to main/develop/AI-Enhancements, PRs to main  
**Purpose:** Core testing across multiple Python versions

```bash
# What it does:
- Tests Python 3.10, 3.11, 3.12
- Runs modular tests by category
- Validates server functionality
- Uploads coverage to Codecov
```

### 2. **Quality Assurance** (`quality-assurance.yml`)  
**Triggers:** Push to main/develop, PRs to main  
**Purpose:** Code quality, security, and comprehensive testing

```bash
# What it does:
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- Performance testing
- Integration testing
```

### 3. **Modular Tests** (`test-modular.yml`)
**Triggers:** Changes to tests/ or Python files  
**Purpose:** Parallel testing by module with detailed coverage

```bash
# Test matrix:
- core: Server core functionality
- ai: AI/LLM integration
- generators: Code generation
- tools: Build/Gradle tools
- utils: Utilities
- integration: API/UI tests
```

### 4. **Tool Validation** (`tool-validation.yml`)
**Triggers:** Daily 2 AM UTC + Push/PR  
**Purpose:** Validate all 31 tools are working

```bash
# What it validates:
- All 31 tools are registered
- Tool schemas are correct
- Basic functionality works
- Error handling works
- Generates tool report
```

## 🧪 Running Tests Locally

### Quick Test Commands
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific modules
pytest tests/ai/ -v                    # AI tests only
pytest tests/tools/ -v                 # Build tools only
pytest tests/generators/ -v            # Code generation only

# Run by marker
pytest tests/ -m security -v           # Security tests
pytest tests/ -m performance -v        # Performance tests
pytest tests/ -m integration -v        # Integration tests
```

### Coverage Reports
```bash
# Generate HTML coverage (view in browser)
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Terminal coverage report
pytest tests/ --cov=. --cov-report=term-missing

# XML for CI tools
pytest tests/ --cov=. --cov-report=xml
```

## 📊 Monitoring CI Status

### GitHub Actions Status
- Check the **Actions** tab in GitHub repository
- Green ✅ = All tests passing
- Red ❌ = Tests failing (click for details)
- Yellow 🟡 = In progress

### Coverage Tracking
- **Codecov**: Automatic upload from CI
- **HTML Reports**: Downloaded from workflow artifacts
- **Current Coverage**: ~35% (see TEST_REORGANIZATION_SUMMARY.md)

## 🔧 Local Development Workflow

### Before Committing
```bash
# 1. Run relevant tests
pytest tests/ -v

# 2. Check formatting
black . --check
isort . --check

# 3. Run linting
flake8 . --exclude=htmlcov,__pycache__,.git

# 4. Optional: Run security check
bandit -r . --exclude=htmlcov,__pycache__,.git
```

### Fixing Issues
```bash
# Auto-fix formatting
black .
isort .

# Run specific test that failed
pytest tests/specific_test.py::TestClass::test_method -v

# Debug with prints (use --capture=no)
pytest tests/test_file.py -v -s
```

## 🎯 CI/CD Best Practices

### For Pull Requests
1. ✅ Ensure all tests pass locally first
2. ✅ Add tests for new functionality
3. ✅ Update documentation if needed
4. ✅ Check CI status before requesting review

### For New Tools
1. ✅ Add tool to appropriate module
2. ✅ Add tests in correct tests/ subdirectory  
3. ✅ Update tool count in validation workflow
4. ✅ Ensure tool appears in handle_list_tools()

### For Debugging Failed CI
1. 🔍 Check the **Actions** tab for detailed logs
2. 🔍 Download artifacts (test results, coverage)
3. 🔍 Run the same command locally
4. 🔍 Check for environment differences

## 📈 Performance Expectations

### Test Execution Times
- **Core tests**: ~30-60 seconds
- **Full test suite**: ~2-3 minutes
- **CI pipeline**: ~5-12 minutes total
- **Tool validation**: ~3-5 minutes

### Coverage Targets
- **Minimum**: 30% overall
- **Target**: 50% overall  
- **Module specific**: See GITHUB_ACTIONS_UPDATES.md

## 🚨 Common Issues & Solutions

### Test Failures
```bash
# Issue: Import errors
# Solution: Check PYTHONPATH and imports

# Issue: Async test failures  
# Solution: Ensure proper @pytest.mark.asyncio

# Issue: Temp directory issues
# Solution: Check cleanup in test fixtures
```

### CI Failures
```bash
# Issue: Python version incompatibility
# Solution: Test locally with multiple versions

# Issue: Dependency conflicts
# Solution: Check requirements.txt versions

# Issue: Timeout errors
# Solution: Check test performance markers
```

### Coverage Issues
```bash
# Issue: Low coverage on new code
# Solution: Add comprehensive tests

# Issue: Coverage not uploading
# Solution: Check Codecov token and XML generation
```

## 📚 Additional Resources

- **Test Documentation**: `tests/README.md`
- **Test Organization**: `TEST_REORGANIZATION_SUMMARY.md`
- **GitHub Actions Updates**: `GITHUB_ACTIONS_UPDATES.md`
- **pytest Configuration**: `pytest.ini`

## 🔄 Workflow Updates

### Adding New Workflows
1. Create `.github/workflows/new-workflow.yml`
2. Follow existing pattern for Python setup
3. Add appropriate triggers and matrix
4. Test locally first

### Modifying Existing Workflows  
1. Update the specific workflow file
2. Test changes on feature branch
3. Monitor first run carefully
4. Document changes in this guide

---

**Quick Status Check:**
```bash
# See current test status
pytest tests/ --tb=no -q

# See coverage summary
pytest tests/ --cov=. --cov-report=term | grep TOTAL
```
