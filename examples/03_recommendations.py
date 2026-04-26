"""
Example 3: Improvement Recommendations

Demonstrates getting improvement recommendations based on learning data.
"""

from socratic_learning import LearningEngine


def get_recommendations():
    """
    Get improvement recommendations from learning data.
    """
    print("=" * 70)
    print("IMPROVEMENT RECOMMENDATIONS")
    print("=" * 70)
    print()

    engine = LearningEngine()

    # Create session with learning data
    print("Step 1: Create Learning Session with Data")
    print("-" * 70)

    session = engine.create_session(
        agent_id="Agent-CodeGenerator",
        project_id="project-789",
        session_type="implementation"
    )

    print(f"Session: {session}")
    print()

    # Record interactions showing weaknesses
    print("Step 2: Record Interactions Showing Patterns")
    print("-" * 70)

    interactions = [
        {
            "type": "code_generation",
            "quality": 0.6,
            "issue": "low_code_quality",
            "tokens": 500
        },
        {
            "type": "code_generation",
            "quality": 0.65,
            "issue": "low_code_quality",
            "tokens": 520
        },
        {
            "type": "testing",
            "quality": 0.8,
            "tokens": 300
        },
        {
            "type": "documentation",
            "quality": 0.5,
            "issue": "poor_documentation",
            "tokens": 200
        },
    ]

    weak_areas = []
    for interaction in interactions:
        engine.record_interaction(
            session_id=session,
            interaction_type=interaction["type"],
            details=interaction
        )
        if interaction.get("quality", 1.0) < 0.7:
            weak_areas.append(interaction["type"])

    print(f"Recorded {len(interactions)} interactions")
    print(f"Weak areas identified: {set(weak_areas)}")
    print()

    # Get recommendations
    print("Step 3: Get Improvement Recommendations")
    print("-" * 70)

    recommendations = engine.get_recommendations(session)

    print(f"Recommendations for Agent-CodeGenerator:")
    print()

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Description: {rec['description']}")
        print(f"   Expected improvement: {rec['expected_improvement']}")
        print()


def priority_recommendations():
    """
    Get prioritized recommendations.
    """
    print("=" * 70)
    print("PRIORITIZED RECOMMENDATIONS")
    print("=" * 70)
    print()

    engine = LearningEngine()

    session = engine.create_session(
        agent_id="Agent-Optimizer",
        project_id="optimization-project",
        session_type="analysis"
    )

    print(f"Session: {session}")
    print()

    # Record metrics showing multiple issues
    issues = [
        {
            "area": "performance",
            "severity": 0.9,
            "impact": "query_slowness",
        },
        {
            "area": "error_handling",
            "severity": 0.7,
            "impact": "unhandled_exceptions",
        },
        {
            "area": "testing",
            "severity": 0.6,
            "impact": "low_coverage",
        },
        {
            "area": "documentation",
            "severity": 0.4,
            "impact": "missing_docs",
        },
    ]

    for issue in issues:
        engine.record_interaction(
            session_id=session,
            interaction_type="assessment",
            details=issue
        )

    print("Recorded issues:")
    for issue in issues:
        print(f"  - {issue['area']}: severity {issue['severity']:.1f}")
    print()

    # Get prioritized recommendations
    print("Prioritized Action Plan:")
    print()

    # Sort by severity
    sorted_issues = sorted(issues, key=lambda x: x["severity"], reverse=True)

    for i, issue in enumerate(sorted_issues, 1):
        print(f"{i}. [PRIORITY] Fix {issue['area']}")
        print(f"   Impact: {issue['impact']}")
        print(f"   Severity: {issue['severity']:.1f}/1.0")
        print()


if __name__ == "__main__":
    get_recommendations()
    print()
    priority_recommendations()
    print("=" * 70)
