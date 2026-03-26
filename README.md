# AI System Repository

This repository is designed as a professional and scalable AI development environment. It includes a structured layout, integrated logging, and a robust testing suite. 

## Project Structure

The codebase is organized into modular components to ensure separation of concerns:

- **`data/`**: Stores raw data, cleaned datasets, models, and system logs.
- **`parsers/`**: Contains scripts to parse varying input formats (e.g., resumes, documents, API responses).
- **`ats_engine/`**: Core engine for parsing and handling resumes and applications.
- **`screening_ai/`**: Implementation of AI algorithms to process and screen candidate profiles.
- **`interview_ai/`**: AI modules for generating and evaluating candidate interview questions.
- **`scoring/`**: Machine Learning tools and metrics used for calculating and assigning standard scores.
- **`utils/`**: Shared utilities, database handlers, and logging configurations.
- **`tests/`**: Unit and integration test suite.

## Setup Instructions

1. **Setup Python Environment**
   Ensure Python 3.8+ is installed. Create and activate a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate on Windows:
   .\venv\Scripts\activate
   
   # Activate on Unix/MacOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**
   Install the necessary libraries via `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

### Testing
To run the full test suite and verify the environment:
```bash
python -m unittest discover tests/
```

### Logging
The AI modules uniformly use the configured logger to track activities and errors. 
Logs are stored in `data/logs/ai_activities.log` and are limited to 5MB, maintaining up to 3 backups (rolling window).

## Code Standards & Documentation

1. **Formatting**: Follow PEP 8 style guidelines for all Python code. Black or Ruff is recommended for automated formatting.
2. **Docstrings**: Provide clear Google-style or Numpy-style docstrings for all modules, classes, and substantive functions. 
3. **Type Hinting**: Use Python type hints (PEP 484) to improve code clarity and support static analysis.
4. **Testing**: Every major logic component must have a corresponding unit test residing in the `tests/` directory. Target a test coverage of at least 80%.
