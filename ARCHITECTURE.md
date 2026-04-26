# socratic-learning Architecture

Continuous learning system for agent behavior tracking and improvement.

## System Overview

socratic-learning tracks agent interactions, analyzes behavior patterns, identifies improvement opportunities, and exports data for model fine-tuning.

## Core Components

### 1. LearningEngine

Main orchestrator for the learning system:
- `create_session()` - Start tracking a learning session
- `record_interaction()` - Log agent interaction
- `get_session_metrics()` - Retrieve learning metrics
- `get_behavior_pattern()` - Analyze behavior patterns
- `detect_patterns()` - Find behavioral patterns
- `detect_anomalies()` - Identify unusual behavior
- `get_recommendations()` - Get improvement suggestions
- `export_for_finetuning()` - Export training data
- `save_finetuning_data()` - Save to file

### 2. Data Models

#### UserBehaviorPattern
Represents learned agent behavior:
- `learning_style` - How agent prefers to work
- `preferred_interaction_type` - Favored interaction modes
- `avg_confidence` - Average decision confidence
- `error_recovery_time` - Speed to recover from errors
- `effectiveness_score` - Overall effectiveness metric

#### QuestionEffectiveness
Tracks question quality and impact:
- `question_id` - Unique identifier
- `question_text` - The question itself
- `effectiveness_score` - How effective was question
- `usage_count` - Times question was used
- `positive_outcomes` - Successful outcomes
- `improved_areas` - What areas improved

#### KnowledgeBaseDocument
Represents learned information:
- `doc_id` - Document identifier
- `content` - Learning content
- `relevance_score` - How relevant to current task
- `effectiveness` - How much did it help
- `created_date` - When learned
- `last_used_date` - Most recent use

### 3. Learning Data Flow

```
Agent Interactions
    |
    v
Record in Session
    |
    v
Analyze Patterns
    |
    +---> Behavior patterns
    +---> Effectiveness metrics
    +---> Anomalies
    |
    v
Generate Recommendations
    |
    v
Export for Fine-tuning
```

## Component Architecture

```
LearningEngine (Main)
    |
    ├-- Session Management
    │   ├-- create_session()
    │   └-- session_storage
    |
    ├-- Interaction Tracking
    │   ├-- record_interaction()
    │   └-- interaction_store
    |
    ├-- Pattern Detection
    │   ├-- detect_patterns()
    │   ├-- detect_anomalies()
    │   └-- behavior_analyzer
    |
    ├-- Recommendations
    │   ├-- get_recommendations()
    │   └-- recommender
    |
    └-- Export
        ├-- export_for_finetuning()
        └-- data_exporter
```

## Session-Based Learning

Each learning session tracks:
1. **Session metadata**
   - Session ID
   - Agent ID
   - Project ID
   - Phase/type
   - Start time

2. **Interactions** (recorded during session)
   - Interaction type (question, analysis, decision, etc.)
   - Quality metrics
   - Token usage
   - Results/outputs
   - Timestamp

3. **Derived metrics**
   - Session quality score
   - Total tokens used
   - Interaction count
   - Duration
   - Categories covered

## Pattern Detection

### Behavioral Patterns
- Repeated interaction types
- Preferred question styles
- Decision-making patterns
- Error recovery patterns
- Knowledge application patterns

### Learning Styles
- Data-driven: Prefers metrics and numbers
- Visual: Prefers diagrams and visualizations
- Strategic: Focuses on goals and planning
- Tactical: Focuses on immediate actions
- Collaborative: Seeks feedback and discussion

### Anomalies
- Unusual token usage
- Quality deviations
- Unexpected error rates
- Behavioral changes
- Performance degradation

## Recommendations Generation

Based on learning data:

### Quality Improvements
- Identify weak areas (quality < threshold)
- Suggest training/retraining
- Recommend skill development
- Propose workflow improvements

### Optimization Suggestions
- Reduce token usage
- Improve quality scores
- Accelerate learning
- Better error handling

### Fine-tuning Opportunities
- Collect high-quality examples
- Identify training categories
- Suggest model improvements
- Recommend specialized variants

## Fine-tuning Data Export

### Export Process

1. **Collect Sessions**
   - Select sessions for export
   - Filter by quality threshold
   - Group by category

2. **Format Data**
   - Convert to training format
   - Include metadata
   - Validate completeness

3. **Export to File**
   - JSONL format (one example per line)
   - Include quality scores
   - Include category tags
   - Include source information

### Export Format

```jsonl
{"input": "question", "output": "response", "quality": 0.95, "category": "architecture"}
{"input": "question", "output": "response", "quality": 0.92, "category": "performance"}
```

### Use Cases

- **OpenAI Fine-tuning API**
  - Upload exported data
  - Train specialized model variant
  - Evaluate on test set

- **Custom Training**
  - Use exported data for in-house model training
  - Track improvement metrics
  - Iterate with new examples

## Integration Points

### With socratic-nexus (LLM Client)
- Track LLM API calls
- Log token usage per interaction
- Monitor quality of LLM outputs
- Collect examples for fine-tuning

### With socratic-agents (Agent Framework)
- Track agent task completion
- Learn from agent behaviors
- Improve agent skill selection
- Recommend agent specializations

### With socratic-workflow (Task Management)
- Track workflow execution quality
- Learn from workflow patterns
- Recommend workflow improvements
- Predict task duration

### With socratic-maturity (Maturity Tracking)
- Track maturity improvement speed
- Identify effective strategies
- Recommend phase progression
- Learn optimal workflows per phase

## Performance Characteristics

- **Session Creation**: O(1)
- **Interaction Recording**: O(1)
- **Pattern Detection**: O(n) where n = interactions
- **Recommendation Generation**: O(n) or O(n log n)
- **Export**: O(n) for n sessions

## Memory Management

- Sessions are immutable once completed
- Streaming pattern detection
- Lazy recommendation generation
- Batched export operations

## Data Retention

- Active sessions: In memory
- Completed sessions: Persistent storage
- Historical data: Queryable archive
- Export data: Separated for fine-tuning

---

Part of the Socratic Ecosystem | Learning-Driven Improvement | Fine-tuning Ready
