# Socratic Learning - FAQ by Scenario

## Tracking Interactions

How do I track agent interactions?

```python
from socratic_learning import LearningManager

learning = LearningManager(storage="sqlite")
session_id = learning.create_session(user_id="user123")

learning.track_interaction(
    session_id=session_id,
    agent_name="CodeGenerator",
    input_data={"prompt": "..."},
    output_data={"code": "..."},
    model_name="claude-opus",
    provider="anthropic",
    input_tokens=150,
    output_tokens=500
)
```

## Getting Metrics

How do I analyze performance?

```python
metrics = learning.get_metrics(agent_name="CodeGenerator")
print(f"Success rate: {metrics.success_rate}%")
```

## Detecting Patterns

How do I find patterns?

```python
patterns = learning.detect_patterns(agent_name="CodeGenerator")
```

## Getting Recommendations

How do I get suggestions?

```python
recommendations = learning.get_recommendations(agent_name="CodeGenerator")
```

## Exporting for Fine-Tuning

How do I export data?

```python
learning.export_for_finetuning(
    output_path="training_data.jsonl",
    agent_name="CodeGenerator",
    min_rating=4,
    format="openai"
)
```
