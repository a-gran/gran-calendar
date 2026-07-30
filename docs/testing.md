# Автотесты

Этот документ описывает, как запускать тесты проекта.

## Запуск

```bash
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

Полная локальная проверка:

```bash
make check
```

## Линтеры

```bash
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
```

Для автоисправления:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check . --fix
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format .
```

## Что проверяется

- модель сохранения событий в SQLite;
- получение текущего времени через доменный helper;
- фабрика создания событий;
- индексация событий по `id`, датам и пересечениям диапазонов;
- применение снимка события к существующему событию;
- загрузка, обновление и удаление событий;
- календарная сетка и преобразование координат во время;
- адаптивная высота строк календаря;
- одиночное и множественное выделение ячеек;
- выбор события кликом;
- подготовка создания события через одинарный клик и протягивание по пустым ячейкам;
- запрет наложения событий;
- копирование, вставка, вырезание и удаление событий;
- `Ctrl+Z` и `Ctrl+Y` на уровне логики окна;
- ограничение истории отмены десятью действиями.

## Структура тестов

- `test_calendar_grid*.py` - поведение сетки, выделение, drag-selection, resize и move.
- `test_calendar_window*.py` - поведение главного окна, деталей, overview, shortcuts и истории.
- `test_clock.py` - получение текущего времени.
- `test_event_factory.py` - создание и копирование событий.
- `test_event_index.py` - чистая логика поиска, сортировки и индексации событий.
- `test_event_service.py` - операции добавления и удаления событий через storage.
- `test_event_update.py` - применение снимков событий.
- `test_event_storage.py` - SQLite-хранилище событий.
