# AI Engine Tests

This folder contains all tests for the AI Engine modules.

## Test Structure

```
tests/
├── __init__.py              # Python package marker
├── conftest.py              # Pytest configuration
├── test_reward_calculator.py # RewardCalculator tests
├── test_multilingual_nlp.py  # NLPProcessor tests
└── README.md                # This file
```

## Running Tests

### Option 1: Run all tests
```bash
cd ai-engine
python run_tests.py
```

### Option 2: Run individual test files
```bash
cd ai-engine

# Run simple reward calculator test
python test_reward_simple.py

# Run multilingual NLP test
python tests/test_multilingual_nlp.py

# Run pytest tests
python -m pytest tests/ -v
```

### Option 3: Run specific pytest test
```bash
cd ai-engine
python -m pytest tests/test_reward_calculator.py::TestRewardCalculator::test_calculate_commission -v
```

## Test Files

### 1. `test_reward_simple.py`
- Simple test script for RewardCalculator
- Tests basic calculation, different roles, edge cases
- Can be run directly

### 2. `tests/test_multilingual_nlp.py`
- Comprehensive test for NLPProcessor
- Tests language detection, sentiment analysis, dispute analysis
- Tests both English and Vietnamese text processing

### 3. `tests/test_reward_calculator.py`
- Full pytest test suite for RewardCalculator
- Tests all methods and edge cases
- Uses pytest fixtures and async testing

## Test Configuration

### `conftest.py`
- Configures Python path for imports
- Sets up pytest environment

### `__init__.py`
- Makes tests folder a Python package
- Required for relative imports

## Expected Results

### RewardCalculator Tests
- ✅ Basic calculation works
- ✅ All 6 roles supported (developer, marketing_specialist, direct_mentor, indirect_mentor, hr_recruiter, business_development)
- ✅ New bonus formula: `Revenue * Role % * Performance Rate`
- ✅ AI confidence calculation
- ✅ Edge cases handled

### NLPProcessor Tests
- ✅ Language detection (EN/VI) with ~83% accuracy
- ✅ Multilingual sentiment analysis
- ✅ Vietnamese keyword extraction
- ✅ Dispute analysis in both languages
- ✅ spaCy models loaded correctly

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. You're running from the `ai-engine` directory
2. All dependencies are installed
3. Python path is configured correctly

### Model Loading Errors
If spaCy models fail to load:
```bash
pip install spacy==3.8.7
python -m spacy download en_core_web_sm
pip install vi-core-news-lg
pip install pyvi
```

### Pytest Issues
If pytest tests fail:
1. Check that `conftest.py` is in the tests folder
2. Verify Python path configuration
3. Run with verbose output: `pytest -v`
