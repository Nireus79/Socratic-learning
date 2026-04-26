"""
Example 1: Basic Learning Session Tracking

Demonstrates creating a learning session, tracking agent interactions,
and retrieving learning metrics.
"""

from socratic_learning import (
    LearningEngine,
    UserBehaviorPattern,
    QuestionEffectiveness,
    KnowledgeBaseDocument
)


def basic_session_tracking():
    """
    Track a basic learning session with agent interactions.
    """
    print("=" * 70)
    print("BASIC LEARNING SESSION TRACKING")
    print("=" * 70)
    print()

    # Step 1: Create learning engine
    print("Step 1: Initialize Learning Engine")
    print("-" * 70)

    engine = LearningEngine()
    session_id = engine.create_session(
        agent_id="Agent-ArchitectureDesigner",
        project_id="project-123",
        session_type="discovery"
    )

    print(f"Created session: {session_id}")
    print(f"Agent: Agent-ArchitectureDesigner")
    print(f"Project: project-123")
    print(f"Phase: discovery")
    print()

    # Step 2: Record interactions
    print("Step 2: Record Agent Interactions")
    print("-" * 70)

    interactions = [
        {
            "type": "question_asked",
            "question": "What are the key scalability requirements?",
            "response_quality": 0.8,
            "tokens_used": 150
        },
        {
            "type": "analysis",
            "description": "Analyzed system architecture",
            "result_quality": 0.7,
            "tokens_used": 300
        },
        {
            "type": "decision",
            "decision": "Use microservices architecture",
            "confidence": 0.85,
            "tokens_used": 200
        }
    ]

    for i, interaction in enumerate(interactions, 1):
        interaction_id = engine.record_interaction(
            session_id=session_id,
            interaction_type=interaction["type"],
            details=interaction
        )
        print(f"  {i}. {interaction['type']}: {interaction_id}")

    print()

    # Step 3: Get session metrics
    print("Step 3: Retrieve Learning Metrics")
    print("-" * 70)

    metrics = engine.get_session_metrics(session_id)

    print(f"Session Metrics:")
    print(f"  Total interactions: {metrics.get('interaction_count', 0)}")
    print(f"  Average quality: {metrics.get('avg_quality', 0):.2f}")
    print(f"  Total tokens: {metrics.get('total_tokens', 0)}")
    print(f"  Session duration: {metrics.get('duration_seconds', 0)}s")
    print()

    # Step 4: Get user behavior pattern
    print("Step 4: User Behavior Pattern")
    print("-" * 70)

    pattern = engine.get_behavior_pattern(session_id)

    if pattern:
        print(f"Behavior Pattern:")
        print(f"  Learning style: {pattern.learning_style}")
        print(f"  Preferred interaction type: {pattern.preferred_interaction_type}")
        print(f"  Average confidence: {pattern.avg_confidence:.2f}")
        print(f"  Error recovery time: {pattern.error_recovery_time}ms")
    else:
        print("Pattern still developing (collect more data)")
    print()


def session_comparison():
    """
    Compare learning metrics across multiple sessions.
    """
    print("=" * 70)
    print("SESSION COMPARISON")
    print("=" * 70)
    print()

    engine = LearningEngine()

    # Simulate multiple sessions
    sessions_data = [
        ("Agent-ArchitectureDesigner", 850),
        ("Agent-DataEngineer", 920),
        ("Agent-SecuritySpecialist", 780),
    ]

    print("Agent Learning Performance:")
    print()

    for agent_id, tokens_used in sessions_data:
        session = engine.create_session(agent_id, "project-123", "analysis")
        metrics = {
            "tokens_used": tokens_used,
            "quality_score": tokens_used / 1000,  # Simplified
            "interactions": tokens_used // 100,
        }
        print(f"{agent_id:>30}")
        print(f"  Tokens used: {metrics['tokens_used']}")
        print(f"  Quality score: {metrics['quality_score']:.2f}")
        print(f"  Interactions: {metrics['interactions']}")
        print()


if __name__ == "__main__":
    basic_session_tracking()
    print()
    session_comparison()
    print("=" * 70)
