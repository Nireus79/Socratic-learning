# Socratic Learning - API Reference

## LearningManager

### Methods
- `create_session(user_id, context)` - Start session
- `track_interaction(...)` - Log interaction
- `add_feedback(interaction_id, rating, feedback)` - Add feedback
- `get_metrics(agent_name)` - Get metrics
- `detect_patterns(agent_name)` - Find patterns
- `get_recommendations(agent_name)` - Get suggestions
- `export_for_finetuning(output_path, agent_name, ...)` - Export data
