import tempfile
import unittest
from pathlib import Path

from masseuse_tracker import TaskStatus, TaskTracker
from masseuse_tracker.cli import format_tasks, main


class TaskTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "tasks.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_sort_complete_remove_and_reload(self) -> None:
        tracker = TaskTracker(self.database)
        first = tracker.add("Jordan", "Deep tissue", "2026-09-13", 2, "Shoulders")
        second = tracker.add("Taylor", "Sports massage", "2026-09-12", 1, "Legs")
        self.assertEqual([task.id for task in tracker.pending_by_priority()], [second.id, first.id])
        self.assertTrue(tracker.complete(first.id))
        self.assertFalse(tracker.complete(999))
        tracker.save()

        loaded = TaskTracker(self.database)
        loaded.load()
        self.assertEqual(len(loaded.tasks), 2)
        self.assertEqual(loaded.tasks[0].status, TaskStatus.COMPLETED)
        self.assertTrue(loaded.remove(second.id))
        self.assertEqual(len(loaded.tasks), 1)

    def test_cli_workflow(self) -> None:
        common = ["--database", str(self.database)]
        self.assertEqual(main([*common, "add", "Ari", "Swedish", "2026-09-20", "3"]), 0)
        self.assertEqual(main([*common, "complete", "1"]), 0)
        tracker = TaskTracker(self.database)
        tracker.load()
        self.assertEqual(tracker.tasks[0].status, TaskStatus.COMPLETED)

    def test_empty_format(self) -> None:
        self.assertEqual(format_tasks([]), "No tasks found.")


if __name__ == "__main__":
    unittest.main()
