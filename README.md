# Python Masseuse Task Tracker

A dependency-free Python command-line tracker for massage appointments and follow-up work. Each task stores a client, service, due date, priority, status, and notes in a local JSON file.

## Requirements

- Python 3.11 or newer

## Run without installing

```bash
python -m masseuse_tracker.cli add "Jordan Lee" "Deep tissue" 2026-09-13 1 "Focus on shoulders"
python -m masseuse_tracker.cli list
python -m masseuse_tracker.cli complete 1
python -m masseuse_tracker.cli list all
python -m masseuse_tracker.cli remove 1
```

Priority `1` is highest and `5` is lowest. `list` shows pending tasks in priority/due-date order; `list all` includes completed tasks. Data is stored in `masseuse_tasks.json` unless `--database PATH` is supplied before the command.

## Install as a command

```bash
python -m pip install .
masseuse-tracker list
```

## Test

```bash
python -m unittest discover -s tests -v
```

## License

MIT
