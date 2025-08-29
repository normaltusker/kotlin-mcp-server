# GitHub Actions Workflows

This repository uses a streamlined CI/CD pipeline with the following workflows:

## Active Workflows

### 1. Essential CI (`ci-streamlined.yml`)
**Primary CI pipeline** - Runs on every push and PR
- ✅ Multi-Python version testing (3.10, 3.11, 3.12)
- ✅ Code quality checks (black, isort, flake8)
- ✅ Comprehensive test suite with coverage
- ✅ Server validation and integration tests
- ✅ Uploads coverage to Codecov

**Triggers**: Push to main/develop/feature branches, PRs to main/develop

### 2. Main CI (`main-ci.yml`)
**Comprehensive CI pipeline** - Enhanced version with additional checks
- ✅ All features from Essential CI
- ✅ Security auditing (bandit, safety)
- ✅ Performance benchmarks (main branch only)
- ✅ Artifact uploads for security reports
- ✅ Enhanced validation and error handling

**Triggers**: Push to main/develop/feature branches, PRs to main/develop

### 3. Tool Validation (`tool-validation-streamlined.yml`)
**Tool-specific validation** - Validates MCP server tools
- ✅ Tool registration validation
- ✅ Essential tool functionality testing
- ✅ Tool schema validation
- ✅ Tool categorization testing
- ✅ Daily scheduled runs for monitoring
- ✅ Tool reporting and artifacts

**Triggers**: Push/PR + daily at 2 AM UTC

## Optimization Changes Made

### Removed Redundant Workflows
- ❌ `quality-assurance.yml` - Merged into main CI
- ❌ `test-modular.yml` - Redundant matrix testing
- ❌ `tool-validation.yml` - Replaced with streamlined version

### Key Improvements
1. **Eliminated Redundancy**: Removed duplicate test execution across workflows
2. **Consolidated Quality Checks**: All code quality checks in one place
3. **Updated Dependencies**: Using actions/setup-python@v5 and codecov/codecov-action@v4
4. **Removed Legacy Python**: No longer testing Python 3.8/3.9 (near EOL)
5. **Fixed Tool Expectations**: Updated tool validation to match actual implementation
6. **Better Performance**: Conditional performance tests only on main branch
7. **Enhanced Security**: Dedicated security auditing with artifact storage
8. **Improved Caching**: Better cache keys for pip dependencies

### Resource Optimization
- **Before**: 4 workflows with overlapping test matrices = ~16 parallel jobs
- **After**: 3 focused workflows with clear separation = ~8 parallel jobs
- **Savings**: ~50% reduction in CI resource usage

### Branch Support
All workflows now properly support the current feature branch: `feature/critical-mcp-compliance`

## Usage

- **For quick feedback**: Monitor "Essential CI" for basic validation
- **For comprehensive checks**: Monitor "Main CI" for full pipeline
- **For tool health**: Monitor "Tool Validation" for MCP server functionality

## Maintenance

- Review tool expectations in `tool-validation-streamlined.yml` when adding new tools
- Update Python version matrix when dropping/adding Python version support
- Adjust performance thresholds in `main-ci.yml` based on project growth
