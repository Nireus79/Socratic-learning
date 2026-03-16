# Socratic Learning

[![PyPI version](https://badge.fury.io/py/socratic-learning.svg)](https://badge.fury.io/py/socratic-learning)
[![Tests](https://github.com/Nireus79/Socratic-learning/workflows/Tests/badge.svg)](https://github.com/Nireus79/Socratic-learning/actions)
[![Code Quality](https://github.com/Nireus79/Socratic-learning/workflows/Code%20Quality/badge.svg)](https://github.com/Nireus79/Socratic-learning/actions)

## Why Socratic Learning?

Most AI platforms treat learning as an afterthought. Socratic Learning makes continuous improvement built-in:

- **Interaction Tracking** - Capture and store all agent interactions with full context for analysis
- **Pattern Detection** - Automatically identify recurring patterns in agent behaviors and model outputs
- **Performance Monitoring** - Track success rates, response times, and costs across all interactions
- **Data-Driven Recommendations** - Get actionable improvement suggestions based on detected patterns
- **Fine-Tuning Ready** - Export interaction data in industry-standard formats for model fine-tuning

A continuous learning system for AI agents that tracks interactions, detects patterns, and provides data-driven improvement recommendations.

## Features

- **Interaction Tracking** - Capture and store all agent interactions with context
- **Pattern Detection** - Identify recurring patterns in agent behaviors and LLM outputs
- **Performance Metrics** - Monitor agent effectiveness with success rates, response times, costs
- **User Feedback Integration** - Collect and analyze user feedback on agent responses
- **Learning Recommendations** - Generate actionable improvement suggestions
- **Fine-Tuning Export** - Export interaction data for model fine-tuning
- **Analytics & Reporting** - JSON-based insights and metrics
- **Framework Integration** - Works with Openclaw and LangChain

## Installation

```bash
# Core package
pip install socratic-learning

# With Socratic Agents integration
pip install socratic-learning[agents]

# With all optional dependencies
pip install socratic-learning[all]

# For development
pip install socratic-learning[dev]
```

## Quick Start

```python
from socratic_learning import LearningManager
from socratic_agents import SocraticCounselor

# Initialize learning manager
learning = LearningManager(storage="sqlite", db_path="learning.db")

# Create a tracking session
session_id = learning.create_session(
    user_id="user123",
    context={"environment": "production"}
)

# Track agent interactions
counselor = SocraticCounselor()
result = counselor.guide("recursion", level="beginner")

learning.track_interaction(
    session_id=session_id,
    agent_name="SocraticCounselor",
    input_data={"topic": "recursion", "level": "beginner"},
    output_data=result,
    model_name="claude-opus-4",
    provider="anthropic",
    input_tokens=150,
    output_tokens=500,
    duration_ms=1200.0,
)

# Add user feedback
learning.add_feedback(
    interaction_id=interaction.interaction_id,
    rating=5,
    feedback="Very helpful explanation!"
)

# Get metrics
metrics = learning.get_metrics(agent_name="SocraticCounselor")
print(f"Success rate: {metrics.success_rate}%")
print(f"Avg rating: {metrics.avg_rating}/5")

# Detect patterns
patterns = learning.detect_patterns(agent_name="SocraticCounselor")
for pattern in patterns:
    print(f"Pattern: {pattern.name} (confidence: {pattern.confidence})")

# Get recommendations
recommendations = learning.get_recommendations(agent_name="SocraticCounselor")
for rec in recommendations:
    print(f"Recommendation: {rec.title}")

# Export for fine-tuning
learning.export_for_finetuning(
    output_path="finetuning_data.jsonl",
    agent_name="SocraticCounselor",
    min_rating=4,
    format="openai"
)
```

## Core Concepts

### Interaction
Represents a single agent interaction with input, output, performance metrics, and optional user feedback.

### Pattern
A detected recurring pattern in agent behaviors (e.g., error patterns, topic-specific behaviors).

### Metric
Aggregated performance metrics (success rate, average response time, user satisfaction, costs).

### Recommendation
An actionable improvement suggestion based on detected patterns and metrics.

## Architecture

- **Core Models** - Dataclass-based models with serialization
- **Storage Layer** - Abstract interface with SQLite backend
- **Tracking** - Interaction logger with session management
- **Analytics** - Pattern detection and metrics collection
- **Integrations** - Openclaw skills and LangChain tools

## Documentation

See [examples/](examples/) for complete working examples.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/socratic_learning --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v
```

## Code Quality

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with MyPy
mypy src/
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Status

**Phase 1** - Core foundation complete (v0.1.0 development)
- ✅ Core data models
- ✅ SQLite storage
- ✅ Unit tests
- 🚀 Phase 2-6 planned
