"""
Example 4: Fine-tuning Data Export

Demonstrates exporting learning data for model fine-tuning.
"""

from socratic_learning import LearningEngine


def export_finetuning_data():
    """
    Export learning session data for model fine-tuning.
    """
    print("=" * 70)
    print("EXPORT LEARNING DATA FOR FINE-TUNING")
    print("=" * 70)
    print()

    engine = LearningEngine()

    # Create session
    print("Step 1: Create Learning Session")
    print("-" * 70)

    session = engine.create_session(
        agent_id="Agent-Expert",
        project_id="finetuning-project",
        session_type="all_phases"
    )

    print(f"Session: {session}")
    print()

    # Record high-quality interactions for training
    print("Step 2: Record High-Quality Interactions")
    print("-" * 70)

    training_examples = [
        {
            "input": "Analyze this system architecture for scalability",
            "output": "Based on the current architecture, I recommend: 1) Implement sharding...",
            "quality": 0.95,
            "category": "architecture_analysis"
        },
        {
            "input": "What are the main performance bottlenecks?",
            "output": "The main bottlenecks are: 1) Database queries (40%), 2) API calls (35%)...",
            "quality": 0.92,
            "category": "performance_analysis"
        },
        {
            "input": "How should we handle error scenarios?",
            "output": "Error handling strategy: 1) Retry with exponential backoff...",
            "quality": 0.88,
            "category": "error_handling"
        },
    ]

    for example in training_examples:
        engine.record_interaction(
            session_id=session,
            interaction_type="training_example",
            details=example
        )

    print(f"Recorded {len(training_examples)} high-quality examples")
    print()

    # Export for fine-tuning
    print("Step 3: Export Data for Fine-Tuning")
    print("-" * 70)

    export_data = engine.export_for_finetuning(session)

    print(f"Export format: JSONL")
    print(f"Number of examples: {len(export_data)}")
    print(f"Categories: {set(ex['category'] for ex in export_data)}")
    print()

    print("Sample training examples:")
    for i, example in enumerate(export_data[:2], 1):
        print(f"\nExample {i}:")
        print(f"  Input: {example['input'][:50]}...")
        print(f"  Output: {example['output'][:50]}...")
        print(f"  Quality: {example['quality']}")
    print()

    # Show export path
    print("Step 4: Save Export")
    print("-" * 70)

    export_path = engine.save_finetuning_data(
        session_id=session,
        format="jsonl",
        output_path="./finetuning_data.jsonl"
    )

    print(f"Exported to: {export_path}")
    print("[OK] Data ready for model fine-tuning")
    print()


def selective_export():
    """
    Export specific categories of interactions for targeted fine-tuning.
    """
    print("=" * 70)
    print("SELECTIVE FINE-TUNING DATA EXPORT")
    print("=" * 70)
    print()

    engine = LearningEngine()

    session = engine.create_session(
        agent_id="Agent-Specialist",
        project_id="selective-export",
        session_type="mixed"
    )

    print("Step 1: Record Interactions in Multiple Categories")
    print("-" * 70)

    categories = ["code_review", "architecture", "testing", "documentation"]
    examples_per_category = 5

    for category in categories:
        for i in range(examples_per_category):
            engine.record_interaction(
                session_id=session,
                interaction_type="training_example",
                details={
                    "category": category,
                    "quality": 0.8 + (i * 0.02),  # Increasing quality
                }
            )

    print(f"Recorded {len(categories)} categories")
    print(f"Examples per category: {examples_per_category}")
    print()

    # Export by category
    print("Step 2: Export by Category")
    print("-" * 70)

    for category in categories:
        category_data = engine.export_for_finetuning(
            session_id=session,
            category_filter=category,
            min_quality=0.85
        )

        print(f"{category}:")
        print(f"  Examples: {len(category_data)}")
        if category_data:
            print(f"  Avg quality: {sum(e['quality'] for e in category_data) / len(category_data):.2f}")
        print()


def finetuning_pipeline():
    """
    Complete fine-tuning pipeline workflow.
    """
    print("=" * 70)
    print("COMPLETE FINE-TUNING PIPELINE")
    print("=" * 70)
    print()

    print("Step 1: Collect Data")
    print("-" * 70)
    print("  - Create learning sessions")
    print("  - Record agent interactions")
    print("  - Track quality metrics")
    print()

    print("Step 2: Filter High-Quality Examples")
    print("-" * 70)
    print("  - Minimum quality: 0.85")
    print("  - Minimum interactions per session: 10")
    print("  - No anomalies or errors")
    print()

    print("Step 3: Export and Format")
    print("-" * 70)
    print("  - Format: JSONL (one example per line)")
    print("  - Include metadata (quality, category, source)")
    print("  - Validate format before export")
    print()

    print("Step 4: Fine-tune Model")
    print("-" * 70)
    print("  - Use OpenAI API or custom training")
    print("  - Validate on held-out test set")
    print("  - Track improvement metrics")
    print()

    print("Step 5: Evaluate Results")
    print("-" * 70)
    print("  - Compare before/after performance")
    print("  - Measure improvement on target tasks")
    print("  - Iterate with new examples")
    print()


if __name__ == "__main__":
    export_finetuning_data()
    print()
    selective_export()
    print()
    finetuning_pipeline()
    print("=" * 70)
