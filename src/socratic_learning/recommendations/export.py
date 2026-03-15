"""Fine-tuning data export functionality."""

import json
from pathlib import Path
from typing import Any, Optional

from socratic_learning.storage.base import BaseLearningStore


class FinetuningExporter:
    """Exports interaction data for model fine-tuning."""

    def __init__(self, store: BaseLearningStore):
        """Initialize exporter with storage backend."""
        self.store = store

    def export_jsonl(
        self,
        output_path: str,
        agent_name: Optional[str] = None,
        min_rating: Optional[int] = None,
        include_failed: bool = False,
        format_type: str = "openai",
    ) -> int:
        """Export interactions in JSONL format for fine-tuning.

        Args:
            output_path: Path to write JSONL file
            agent_name: Optional agent name to filter
            min_rating: Optional minimum user rating to include
            include_failed: Whether to include failed interactions
            format_type: Format type ("openai", "anthropic", "raw")

        Returns:
            Number of interactions exported
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        # Filter interactions
        if not include_failed:
            interactions = [i for i in interactions if i.success]

        if min_rating is not None:
            interactions = [
                i for i in interactions if i.user_rating is not None and i.user_rating >= min_rating
            ]

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        with open(output_file, "w") as f:
            for interaction in interactions:
                record = self._format_interaction(interaction, format_type)
                f.write(json.dumps(record) + "\n")
                exported_count += 1

        return exported_count

    def export_csv(
        self,
        output_path: str,
        agent_name: Optional[str] = None,
        min_rating: Optional[int] = None,
        include_failed: bool = False,
    ) -> int:
        """Export interactions in CSV format.

        Args:
            output_path: Path to write CSV file
            agent_name: Optional agent name to filter
            min_rating: Optional minimum user rating to include
            include_failed: Whether to include failed interactions

        Returns:
            Number of interactions exported
        """
        import csv

        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        # Filter interactions
        if not include_failed:
            interactions = [i for i in interactions if i.success]

        if min_rating is not None:
            interactions = [
                i for i in interactions if i.user_rating is not None and i.user_rating >= min_rating
            ]

        if not interactions:
            return 0

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "interaction_id",
                    "agent_name",
                    "input",
                    "output",
                    "rating",
                    "timestamp",
                    "duration_ms",
                    "cost_usd",
                ],
            )
            writer.writeheader()

            for interaction in interactions:
                writer.writerow(
                    {
                        "interaction_id": interaction.interaction_id,
                        "agent_name": interaction.agent_name,
                        "input": json.dumps(interaction.input_data),
                        "output": json.dumps(interaction.output_data),
                        "rating": interaction.user_rating,
                        "timestamp": interaction.timestamp.isoformat(),
                        "duration_ms": interaction.duration_ms,
                        "cost_usd": interaction.cost_usd,
                    }
                )

        return len(interactions)

    def export_jsonl_by_quality(
        self,
        output_path: str,
        agent_name: Optional[str] = None,
    ) -> dict[str, int]:
        """Export interactions grouped by quality level.

        Args:
            output_path: Base path (will create quality_high.jsonl, quality_medium.jsonl, etc.)
            agent_name: Optional agent name to filter

        Returns:
            Dict with counts for each quality level
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        # Categorize by rating
        high_quality = []
        medium_quality = []
        low_quality = []
        no_rating = []

        for i in interactions:
            if i.user_rating is None:
                no_rating.append(i)
            elif i.user_rating >= 4:
                high_quality.append(i)
            elif i.user_rating >= 3:
                medium_quality.append(i)
            else:
                low_quality.append(i)

        # Write files
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        counts = {}

        # High quality (best for fine-tuning)
        high_path = output_path_obj.parent / f"{output_path_obj.stem}_high.jsonl"
        with open(high_path, "w") as f:
            for interaction in high_quality:
                record = self._format_interaction(interaction, "openai")
                f.write(json.dumps(record) + "\n")
        counts["high_quality"] = len(high_quality)

        # Medium quality
        medium_path = output_path_obj.parent / f"{output_path_obj.stem}_medium.jsonl"
        with open(medium_path, "w") as f:
            for interaction in medium_quality:
                record = self._format_interaction(interaction, "openai")
                f.write(json.dumps(record) + "\n")
        counts["medium_quality"] = len(medium_quality)

        # Low quality (for analysis, not recommended for fine-tuning)
        low_path = output_path_obj.parent / f"{output_path_obj.stem}_low.jsonl"
        with open(low_path, "w") as f:
            for interaction in low_quality:
                record = self._format_interaction(interaction, "openai")
                f.write(json.dumps(record) + "\n")
        counts["low_quality"] = len(low_quality)

        # No rating
        no_rating_path = output_path_obj.parent / f"{output_path_obj.stem}_unrated.jsonl"
        with open(no_rating_path, "w") as f:
            for interaction in no_rating:
                record = self._format_interaction(interaction, "openai")
                f.write(json.dumps(record) + "\n")
        counts["unrated"] = len(no_rating)

        return counts

    def _format_interaction(
        self,
        interaction: Any,
        format_type: str,
    ) -> dict[str, Any]:
        """Format interaction for export based on format type.

        Args:
            interaction: Interaction object
            format_type: Format type ("openai", "anthropic", "raw")

        Returns:
            Formatted dict
        """
        if format_type == "openai":
            # OpenAI fine-tuning format: {"messages": [...]}
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": json.dumps(interaction.input_data),
                    },
                    {
                        "role": "assistant",
                        "content": json.dumps(interaction.output_data),
                    },
                ]
            }

        elif format_type == "anthropic":
            # Anthropic format: {"prompt": ..., "completion": ...}
            return {
                "prompt": json.dumps(interaction.input_data),
                "completion": json.dumps(interaction.output_data),
            }

        else:  # "raw"
            # Raw format with all metadata
            return {
                "interaction_id": interaction.interaction_id,
                "agent_name": interaction.agent_name,
                "input_data": interaction.input_data,
                "output_data": interaction.output_data,
                "rating": interaction.user_rating,
                "feedback": interaction.user_feedback,
                "duration_ms": interaction.duration_ms,
                "cost_usd": interaction.cost_usd,
                "timestamp": interaction.timestamp.isoformat(),
                "success": interaction.success,
            }

    def get_export_summary(
        self,
        agent_name: Optional[str] = None,
        min_rating: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get summary of what would be exported.

        Args:
            agent_name: Optional agent name to filter
            min_rating: Optional minimum user rating

        Returns:
            Summary dict
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        # Apply filters
        if min_rating is not None:
            rated = [
                i for i in interactions if i.user_rating is not None and i.user_rating >= min_rating
            ]
        else:
            rated = [i for i in interactions if i.user_rating is not None]

        successful = [i for i in interactions if i.success]
        rated_successful = [i for i in rated if i.success]

        return {
            "total_interactions": len(interactions),
            "successful_interactions": len(successful),
            "rated_interactions": len(rated),
            "rated_and_successful": len(rated_successful),
            "rating_coverage": (len(rated) / len(interactions) * 100 if interactions else 0.0),
            "success_rate": (len(successful) / len(interactions) * 100 if interactions else 0.0),
            "recommended_export_count": len(rated_successful),
            "recommended_for_finetuning": rated_successful,
        }
