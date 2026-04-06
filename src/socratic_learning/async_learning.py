"""Asynchronous learning analytics and processing."""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from .analytics.learning_engine import LearningEngine, UserProfile

logger = logging.getLogger(__name__)


class AsyncLearningEngine:
    """Asynchronous version of learning engine for concurrent processing."""

    def __init__(self, learning_engine: Optional[LearningEngine] = None, max_concurrent: int = 5):
        """
        Initialize async learning engine.

        Args:
            learning_engine: Base learning engine instance
            max_concurrent: Maximum concurrent operations
        """
        self.engine = learning_engine or LearningEngine()
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def build_user_profile_async(
        self,
        user_id: str,
        questions_asked: List[Dict[str, Any]],
        responses_quality: List[float],
        topic_interactions: List[str],
        projects_completed: int,
    ) -> UserProfile:
        """
        Asynchronously build user profile.

        Args:
            user_id: User ID
            questions_asked: List of questions with metadata
            responses_quality: Quality scores for responses
            topic_interactions: Topics the user has interacted with
            projects_completed: Number of projects completed

        Returns:
            UserProfile object
        """
        async with self.semaphore:
            # Run sync method in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.engine.build_user_profile,
                user_id,
                questions_asked,
                responses_quality,
                topic_interactions,
                projects_completed,
            )

    async def calculate_learning_metrics_async(self, profile: UserProfile) -> Dict[str, Any]:
        """
        Asynchronously calculate learning metrics.

        Args:
            profile: UserProfile object

        Returns:
            Dictionary of learning metrics
        """
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.engine.calculate_learning_metrics,
                profile,
            )

    async def batch_build_profiles_async(
        self,
        user_data: List[Dict[str, Any]],
    ) -> List[UserProfile]:
        """
        Build profiles for multiple users concurrently.

        Args:
            user_data: List of user data dictionaries

        Returns:
            List of UserProfile objects
        """
        tasks = [
            self.build_user_profile_async(
                user_id=data["user_id"],
                questions_asked=data.get("questions_asked", []),
                responses_quality=data.get("responses_quality", []),
                topic_interactions=data.get("topic_interactions", []),
                projects_completed=data.get("projects_completed", 0),
            )
            for data in user_data
        ]

        return await asyncio.gather(*tasks)

    async def batch_calculate_metrics_async(
        self,
        profiles: List[UserProfile],
    ) -> List[Dict[str, Any]]:
        """
        Calculate metrics for multiple profiles concurrently.

        Args:
            profiles: List of UserProfile objects

        Returns:
            List of metric dictionaries
        """
        tasks = [
            self.calculate_learning_metrics_async(profile)
            for profile in profiles
        ]

        return await asyncio.gather(*tasks)

    async def stream_profile_analysis(
        self,
        user_data: List[Dict[str, Any]],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream profile analysis results as they complete.

        Args:
            user_data: List of user data dictionaries

        Yields:
            Dictionary with user_id and metrics as each completes
        """
        tasks = {
            asyncio.create_task(
                self.build_user_profile_async(
                    user_id=data["user_id"],
                    questions_asked=data.get("questions_asked", []),
                    responses_quality=data.get("responses_quality", []),
                    topic_interactions=data.get("topic_interactions", []),
                    projects_completed=data.get("projects_completed", 0),
                )
            ): data["user_id"]
            for data in user_data
        }

        # Yield results as they complete
        for future in asyncio.as_completed(tasks):
            try:
                profile = await future
                metrics = await self.calculate_learning_metrics_async(profile)
                yield {
                    "user_id": profile.user_id,
                    "profile": profile,
                    "metrics": metrics,
                }
            except Exception as e:
                self.logger.error(f"Error processing user: {e}", exc_info=True)
                yield {
                    "user_id": tasks[future],
                    "error": str(e),
                }

    async def parallel_analyze_interactions(
        self,
        interactions: List[Dict[str, Any]],
        processor_func=None,
    ) -> List[Dict[str, Any]]:
        """
        Process interactions in parallel.

        Args:
            interactions: List of interaction data
            processor_func: Optional async function to process each interaction

        Returns:
            List of processed interaction results
        """
        if processor_func is None:
            # Default processor - just return the interaction
            async def processor_func(interaction):
                await asyncio.sleep(0)  # Yield control
                return interaction

        tasks = [processor_func(interaction) for interaction in interactions]
        return await asyncio.gather(*tasks)


class AsyncBatchProcessor:
    """Async batch processor for large-scale learning operations."""

    def __init__(self, batch_size: int = 100, max_workers: int = 5):
        """
        Initialize batch processor.

        Args:
            batch_size: Size of each batch
            max_workers: Maximum concurrent workers
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    async def process_batches(
        self,
        items: List[Any],
        processor_func,
    ) -> List[Any]:
        """
        Process items in batches with concurrency control.

        Args:
            items: List of items to process
            processor_func: Async function to process each item

        Returns:
            List of processed results
        """
        results = []
        semaphore = asyncio.Semaphore(self.max_workers)

        async def bounded_processor(item):
            async with semaphore:
                return await processor_func(item)

        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            self.logger.debug(f"Processing batch {i // self.batch_size + 1}")

            batch_results = await asyncio.gather(
                *[bounded_processor(item) for item in batch]
            )
            results.extend(batch_results)

        return results

    async def stream_batches(
        self,
        items: List[Any],
        processor_func,
    ) -> AsyncGenerator[List[Any], None]:
        """
        Stream batch results as they complete.

        Args:
            items: List of items to process
            processor_func: Async function to process each item

        Yields:
            Batch results as they complete
        """
        semaphore = asyncio.Semaphore(self.max_workers)

        async def bounded_processor(item):
            async with semaphore:
                return await processor_func(item)

        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            self.logger.debug(f"Processing batch {i // self.batch_size + 1}")

            batch_results = await asyncio.gather(
                *[bounded_processor(item) for item in batch]
            )
            yield batch_results


class AsyncLearningAnalyzer:
    """Async analyzer for learning data."""

    def __init__(self, engine: Optional[AsyncLearningEngine] = None):
        """
        Initialize analyzer.

        Args:
            engine: AsyncLearningEngine instance
        """
        self.engine = engine or AsyncLearningEngine()
        self.logger = logging.getLogger(__name__)

    async def analyze_cohort_async(
        self,
        cohort_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze a cohort of users asynchronously.

        Args:
            cohort_data: List of user data for cohort

        Returns:
            Cohort analysis results
        """
        profiles = await self.engine.batch_build_profiles_async(cohort_data)
        metrics_list = await self.engine.batch_calculate_metrics_async(profiles)

        # Aggregate cohort statistics
        cohort_stats = {
            "total_users": len(profiles),
            "avg_engagement": sum(m["engagement_score"] for m in metrics_list) / len(metrics_list),
            "avg_success_rate": sum(m["success_rate"] for m in metrics_list) / len(metrics_list),
            "avg_learning_velocity": sum(m["learning_velocity"] for m in metrics_list) / len(metrics_list),
            "experience_levels": self._count_levels(metrics_list),
            "total_topics_explored": sum(m["topics_explored"] for m in metrics_list),
            "total_projects": sum(m["projects_completed"] for m in metrics_list),
        }

        return cohort_stats

    async def compare_cohorts_async(
        self,
        cohorts: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple cohorts asynchronously.

        Args:
            cohorts: Dictionary mapping cohort names to user data

        Returns:
            Comparison results for all cohorts
        """
        tasks = {
            name: self.analyze_cohort_async(data)
            for name, data in cohorts.items()
        }

        results = {}
        for name, task in tasks.items():
            results[name] = await task

        return results

    @staticmethod
    def _count_levels(metrics_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count users by experience level."""
        counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for metrics in metrics_list:
            level = metrics.get("experience_level", "beginner")
            counts[level] = counts.get(level, 0) + 1
        return counts
