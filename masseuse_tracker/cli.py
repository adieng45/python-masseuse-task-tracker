"""Command-line interface for the masseuse task tracker."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .tracker import Task, TaskTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track massage appointments and follow-ups")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("masseuse_tasks.json"),
        help="JSON database path (default: masseuse_tasks.json)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Add a task")
    add.add_argument("client")
    add.add_argument("service")
    add.add_argument("due_date", metavar="YYYY-MM-DD")
    add.add_argument("priority", type=int, choices=range(1, 6), metavar="1-5")
    add.add_argument("notes", nargs="?", default="")

    listing = commands.add_parser("list", help="List pending tasks")
    listing.add_argument("scope", nargs="?", choices=("all",))

    complete = commands.add_parser("complete", help="Complete a task")
    complete.add_argument("id", type=int)

    remove = commands.add_parser("remove", help="Remove a task")
    remove.add_argument("id", type=int)
    return parser


def format_tasks(tasks: Sequence[Task]) -> str:
    if not tasks:
        return "No tasks found."
    rows = ["ID | Priority | Status    | Due        | Client | Service | Notes"]
    rows.append("---+----------+-----------+------------+--------+---------+------")
    rows.extend(
        f"{task.id}  | {task.priority}        | {task.status.value:<9} | "
        f"{task.due_date:>10} | {task.client} | {task.service} | {task.notes}"
        for task in tasks
    )
    return "\n".join(rows)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracker = TaskTracker(args.database)
    try:
        tracker.load()
    except (OSError, ValueError) as error:
        print(f"Could not read the task database: {error}")
        return 1

    if args.command == "add":
        task = tracker.add(args.client, args.service, args.due_date, args.priority, args.notes)
        tracker.save()
        print(f"Added task #{task.id}.")
    elif args.command == "list":
        print(format_tasks(tracker.tasks if args.scope == "all" else tracker.pending_by_priority()))
    elif args.command in {"complete", "remove"}:
        changed = tracker.complete(args.id) if args.command == "complete" else tracker.remove(args.id)
        if not changed:
            print(f"Task #{args.id} was not found.")
            return 3
        tracker.save()
        print(f"{'Completed' if args.command == 'complete' else 'Removed'} task #{args.id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
