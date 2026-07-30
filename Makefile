UV_CACHE_DIR ?= /tmp/uv-cache
QT_QPA_PLATFORM ?= offscreen

.PHONY: check lint format-check test py-compile

check: lint format-check test

lint:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff check .

format-check:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff format --check .

test:
	QT_QPA_PLATFORM=$(QT_QPA_PLATFORM) UV_CACHE_DIR=$(UV_CACHE_DIR) uv run pytest

py-compile:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
