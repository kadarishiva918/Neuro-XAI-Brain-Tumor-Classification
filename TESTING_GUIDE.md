# Testing & Quality Assurance Guide

## Overview

This document provides comprehensive guidance for testing the Brain Tumor Classification system to ensure code quality, reliability, and production readiness.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Test Categories](#test-categories)
4. [Writing Tests](#writing-tests)
5. [Code Coverage](#code-coverage)
6. [Continuous Integration](#continuous-integration)
7. [Best Practices](#best-practices)

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_model.py            # Model architecture tests
├── test_inference.py        # Inference pipeline tests
├── test_api.py              # API endpoint tests
├── test_data.py             # Data loading tests
├── test_explanations.py     # XAI explanation tests
└── fixtures/
    ├── sample_images/       # Test images
    └── sample_models/       # Test models
```

### Test File Organization

Each test file should:
- Use descriptive names: `test_<component>_<functionality>.py`
- Group related tests into classes: `Test<Component><Functionality>`
- Include docstrings explaining what's being tested
- Use appropriate pytest markers for categorization

---

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_model.py
```

### Run Specific Test Class
```bash
pytest tests/test_model.py::TestModelArchitecture
```

### Run Specific Test
```bash
pytest tests/test_model.py::TestModelArchitecture::test_model_creation
```

### Run with Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all tests except slow tests
pytest -m "not slow"

# Run GPU tests (if GPU available)
pytest -m gpu
```

### Run with Coverage
```bash
# Basic coverage report
pytest --cov=src

# Detailed coverage report with missing lines
pytest --cov=src --cov-report=term-missing

# HTML coverage report
pytest --cov=src --cov-report=html
# View report: open htmlcov/index.html
```

### Run with Specific Options
```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last N failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff

# Parallel execution (requires pytest-xdist)
pytest -n auto
```

---

## Test Categories

### 1. Unit Tests (test_model.py)

**Purpose**: Test individual components in isolation

**Examples**:
- Model initialization
- Forward pass with dummy input
- Attention module functionality
- Configuration loading
- Utility functions

**Running Unit Tests**:
```bash
pytest tests/test_model.py -m unit
```

### 2. Integration Tests (test_inference.py)

**Purpose**: Test complete workflows end-to-end

**Examples**:
- Load model → preprocess image → inference
- End-to-end prediction pipeline
- Multiple component interactions
- Data loading + model inference

**Running Integration Tests**:
```bash
pytest tests/test_inference.py -m integration
```

### 3. API Tests (test_api.py)

**Purpose**: Test all API endpoints

**Examples**:
- POST /predict with image file
- GET /health
- Error handling (400, 500 responses)
- Request validation
- Response formats

**Running API Tests**:
```bash
pytest tests/test_api.py -m api
```

### 4. Performance Tests

**Purpose**: Verify performance requirements are met

**Examples**:
- Inference latency < 1s (CPU)
- Memory usage < 2GB
- Throughput > 10 predictions/second
- Model size < 500MB

**Running Performance Tests**:
```bash
pytest -m performance
```

### 5. Data Tests (test_data.py)

**Purpose**: Validate data loading and preprocessing

**Examples**:
- Dataset loading
- Image preprocessing
- Augmentation correctness
- Data split validation

**Running Data Tests**:
```bash
pytest tests/test_data.py -m data
```

### 6. XAI Tests (test_explanations.py)

**Purpose**: Verify explanation generation

**Examples**:
- Grad-CAM output shape and values
- LIME explanation generation
- SHAP explanation generation
- Output visualization

**Running XAI Tests**:
```bash
pytest tests/test_explanations.py -m xai
```

---

## Writing Tests

### Basic Test Template

```python
import pytest
import torch
from pathlib import Path

class TestMyFeature:
    """Test suite for my feature."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        # More setup...
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        input_data = torch.randn(1, 3, 224, 224)
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result.shape == (1, 4)
        assert torch.all(result >= 0)
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test slow operation."""
        # This test might take > 5 seconds
        pass
    
    @pytest.mark.parametrize("input_size", [224, 256, 512])
    def test_with_parameters(self, input_size):
        """Test with different parameters."""
        assert input_size > 0
```

### Using Fixtures

```python
@pytest.fixture
def sample_image():
    """Provide sample image for tests."""
    from PIL import Image
    import numpy as np
    
    # Create dummy image
    img = Image.fromarray(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    return img

@pytest.fixture
def model():
    """Provide model for tests."""
    from src.models.model import BrainTumorClassifier
    
    model = BrainTumorClassifier(
        backbone='efficientnet_b0',
        num_classes=4,
        pretrained=False
    )
    return model.eval()

class TestWithFixtures:
    def test_with_sample_image(self, sample_image):
        """Use fixture in test."""
        assert sample_image.size == (224, 224)
    
    def test_with_model(self, model):
        """Use model fixture."""
        assert model is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("class_name,expected_idx", [
    ("glioma", 0),
    ("meningioma", 1),
    ("no_tumor", 2),
    ("pituitary", 3),
])
def test_class_mapping(class_name, expected_idx):
    """Test class name to index mapping."""
    # Implementation
    pass
```

---

## Code Coverage

### Understanding Coverage Reports

- **Line Coverage**: % of lines executed
- **Branch Coverage**: % of conditional branches executed
- **Function Coverage**: % of functions called

### Targets

| Metric | Target | Current |
|--------|--------|---------|
| Overall | > 80% | TBD |
| src/models/ | > 85% | TBD |
| src/training/ | > 75% | TBD |
| src/data/ | > 80% | TBD |
| src/xai/ | > 70% | TBD |

### Improving Coverage

1. **Identify uncovered code**: `pytest --cov=src --cov-report=term-missing`
2. **Write tests for missing coverage**
3. **Focus on critical paths first**
4. **Test error conditions and edge cases**

---

## Continuous Integration

### GitHub Actions Workflow

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main/develop
- Scheduled daily at 2 AM UTC

### Workflow Stages

1. **Lint**: Flake8 code quality checks
2. **Test**: Run pytest suite
3. **Coverage**: Generate and upload coverage reports
4. **Build**: Build Docker image
5. **Security**: Security scanning with Bandit
6. **Performance**: Performance benchmarking

### Local CI Simulation

Run the same checks locally:
```bash
# Lint
flake8 src/ --max-line-length=127

# Test with coverage
pytest tests/ --cov=src --cov-report=html

# Security check
bandit -r src/

# Type check (if mypy installed)
mypy src/ --ignore-missing-imports
```

---

## Best Practices

### 1. Test Naming

✅ **Good**:
- `test_model_inference_produces_4_outputs`
- `test_invalid_image_raises_error`
- `test_api_predict_endpoint_returns_200`

❌ **Bad**:
- `test_1`
- `test_something`
- `test_works`

### 2. Test Organization

✅ **Good**: One assertion (or related assertions) per test
```python
def test_model_output_shape():
    """Test model produces correct output shape."""
    model = get_model()
    x = torch.randn(1, 3, 224, 224)
    
    output = model(x)
    
    assert output.shape == (1, 4)
```

❌ **Bad**: Multiple unrelated assertions
```python
def test_model():
    model = get_model()
    x = torch.randn(1, 3, 224, 224)
    output = model(x)
    assert output.shape == (1, 4)
    assert output.sum() > 0
    assert isinstance(output, torch.Tensor)
    # ... many more assertions
```

### 3. Use Markers

```python
@pytest.mark.slow
@pytest.mark.gpu
def test_gpu_intensive_operation():
    """Test that requires GPU and takes time."""
    pass
```

### 4. Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

def test_with_mock_api():
    """Test with mocked external service."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'status': 'ok'}
        # Test code
```

### 5. Test Error Cases

```python
def test_invalid_input_raises_error():
    """Test error handling for invalid input."""
    with pytest.raises(ValueError):
        process_image(invalid_image_path)
```

### 6. Use Meaningful Assertions

✅ **Good**:
```python
assert latency_ms < 1000, f"Expected <1s, got {latency_ms}ms"
```

❌ **Bad**:
```python
assert result
```

---

## Troubleshooting

### Tests Pass Locally but Fail in CI

**Causes**:
- Different Python versions
- Different OS (Linux vs Windows vs macOS)
- Environment variables not set
- Missing dependencies

**Solutions**:
- Test with multiple Python versions locally
- Check CI logs for error details
- Ensure all dependencies in requirements.txt

### Tests are Too Slow

**Solutions**:
- Use `@pytest.mark.slow` for long tests
- Run only fast tests with `-m "not slow"`
- Parallelize with `pytest-xdist`: `pytest -n auto`
- Use fixtures to avoid repeated setup

### Memory Issues During Testing

**Solutions**:
- Clear GPU memory: `torch.cuda.empty_cache()`
- Use smaller batch sizes in tests
- Skip memory-intensive tests on CI

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [PyTorch Testing Guide](https://pytorch.org/docs/stable/testing.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

