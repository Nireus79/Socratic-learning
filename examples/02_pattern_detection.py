"""
Example 2: Pattern Detection in Agent Behavior

Demonstrates detecting patterns in agent interactions and learning styles.
"""

from socratic_learning import LearningEngine


def detect_learning_patterns():
    """
    Detect patterns in agent behavior over multiple interactions.
    """
    print("=" * 70)
    print("PATTERN DETECTION IN AGENT BEHAVIOR")
    print("=" * 70)
    print()

    engine = LearningEngine()

    # Create session
    print("Step 1: Create Learning Session")
    print("-" * 70)

    session_id = engine.create_session(
        agent_id="Agent-CodeReviewer",
        project_id="project-456",
        session_type="implementation"
    )

    print(f"Session ID: {session_id}")
    print()

    # Simulate repeated interactions
    print("Step 2: Record Repeated Interactions")
    print("-" * 70)

    # Agent asks similar questions in different contexts
    questions = [
        "What is the current error rate?",
        "What is the failure rate for this component?",
        "What percentage of requests fail?",
        "How many errors are we seeing?",
    ]

    print(f"Recording {len(questions)} related interactions...")

    for question in questions:
        engine.record_interaction(
            session_id=session_id,
            interaction_type="question_asked",
            details={"question": question, "intent": "monitoring"}
        )

    print()

    # Detect patterns
    print("Step 3: Detect Behavior Patterns")
    print("-" * 70)

    patterns = engine.detect_patterns(session_id)

    print(f"Detected Patterns:")
    print()

    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['name']}")
        print(f"   Description: {pattern['description']}")
        print(f"   Confidence: {pattern['confidence']:.2f}")
        print(f"   Frequency: {pattern['frequency']} times")
        print()


def learning_style_detection():
    """
    Detect learning style preferences of agents.
    """
    print("=" * 70)
    print("LEARNING STYLE DETECTION")
    print("=" * 70)
    print()

    engine = LearningEngine()

    print("Step 1: Analyze Agent Interaction Styles")
    print("-" * 70)

    agents = [
        {
            "id": "Agent-DataAnalyst",
            "interactions": ["numeric_analysis", "statistical_testing", "data_visualization"],
            "style": "data-driven"
        },
        {
            "id": "Agent-Designer",
            "interactions": ["visual_design", "user_research", "prototyping"],
            "style": "visual"
        },
        {
            "id": "Agent-Strategist",
            "interactions": ["roadmap_planning", "goal_setting", "risk_assessment"],
            "style": "strategic"
        },
    ]

    print()
    for agent in agents:
        session = engine.create_session(
            agent_id=agent["id"],
            project_id="learning-project",
            session_type="analysis"
        )

        # Record interactions matching style
        for interaction_type in agent["interactions"]:
            engine.record_interaction(
                session_id=session,
                interaction_type=interaction_type,
                details={"agent_style": agent["style"]}
            )

        print(f"{agent['id']}")
        print(f"  Preferred style: {agent['style']}")
        print(f"  Interaction types: {len(agent['interactions'])}")
        print()

    print("[OK] Learning styles detected for all agents")
    print()


def anomaly_detection():
    """
    Detect anomalies in agent behavior patterns.
    """
    print("=" * 70)
    print("ANOMALY DETECTION IN PATTERNS")
    print("=" * 70)
    print()

    engine = LearningEngine()

    print("Step 1: Establish Normal Behavior Baseline")
    print("-" * 70)

    session = engine.create_session(
        agent_id="Agent-Monitor",
        project_id="anomaly-project",
        session_type="monitoring"
    )

    # Normal interactions
    normal_interactions = [
        {"type": "metric_check", "tokens": 100},
        {"type": "metric_check", "tokens": 95},
        {"type": "metric_check", "tokens": 105},
        {"type": "metric_check", "tokens": 98},
        {"type": "metric_check", "tokens": 102},
    ]

    for interaction in normal_interactions:
        engine.record_interaction(
            session_id=session,
            interaction_type=interaction["type"],
            details={"tokens_used": interaction["tokens"]}
        )

    print(f"Recorded {len(normal_interactions)} normal interactions")
    print("Average tokens: ~100")
    print()

    # Anomalous interaction
    print("Step 2: Anomalous Interaction Detected")
    print("-" * 70)

    anomaly = engine.record_interaction(
        session_id=session,
        interaction_type="metric_check",
        details={"tokens_used": 5000}  # 50x normal
    )

    print(f"Detected anomaly in interaction: {anomaly}")
    print(f"Tokens used: 5000 (expected: ~100)")
    print(f"Deviation: 50x normal")
    print()

    anomalies = engine.detect_anomalies(session)
    print(f"Total anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"  - {anomaly}")
    print()


if __name__ == "__main__":
    detect_learning_patterns()
    print()
    learning_style_detection()
    print()
    anomaly_detection()
    print("=" * 70)
