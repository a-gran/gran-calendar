# Calendar Planner

Desktop-приложение для личного планирования в форме календаря.

Проект задуман как простой аналог календарного планировщика из Obsidian/Full Calendar,
но без привязки к Obsidian, Google Calendar и перегруженных внешних сервисов.

## Статус

Сейчас проект находится на этапе прототипа.

Точка запуска приложения находится в `main.py`.

## Технологии

- Python
- PySide6
- SQLite
- uv

## Быстрый запуск

```bash
uv venv
source .venv/bin/activate
uv sync
uv run python main.py
```

Без активации окружения:

```bash
uv run python main.py
```

## Проверки

```bash
make check
```

## Документация

- [Инструкция по работе с приложением](docs/usage.md)
- [Горячие клавиши](docs/hotkeys.md)
- [Архитектура](docs/architecture.md)
- [Синхронизация через GitLab](docs/gitlab-sync.md)
