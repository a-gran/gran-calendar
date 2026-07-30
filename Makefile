UV_CACHE_DIR ?= /tmp/uv-cache
QT_QPA_PLATFORM ?= offscreen
APP_NAME ?= CalendarPlanner
APP_ID ?= calendar-planner
INSTALL_DIR ?= $(HOME)/.local/opt/$(APP_ID)
DESKTOP_DIR ?= $(HOME)/.local/share/applications
DESKTOP_FILE ?= $(DESKTOP_DIR)/$(APP_ID).desktop
ICON_DIR ?= $(HOME)/.local/share/icons/hicolor/scalable/apps
ICON_FILE ?= $(ICON_DIR)/$(APP_ID).svg

.PHONY: check lint format-check test py-compile build-app install-local uninstall-local clean-build

check: lint format-check test

build-app:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --with pyinstaller pyinstaller --noconfirm --clean packaging/CalendarPlanner.spec

install-local: build-app
	install -d "$(INSTALL_DIR)" "$(DESKTOP_DIR)" "$(ICON_DIR)"
	rm -rf "$(INSTALL_DIR)"
	install -d "$(INSTALL_DIR)"
	cp -a "dist/$(APP_NAME)/." "$(INSTALL_DIR)/"
	install -m 0644 "packaging/$(APP_ID).svg" "$(ICON_FILE)"
	{ \
		printf '%s\n' '[Desktop Entry]'; \
		printf '%s\n' 'Type=Application'; \
		printf '%s\n' 'Name=Calendar Planner'; \
		printf '%s\n' 'Comment=Личный календарный планировщик'; \
		printf '%s\n' 'Exec=$(INSTALL_DIR)/$(APP_NAME)'; \
		printf '%s\n' 'Icon=$(ICON_FILE)'; \
		printf '%s\n' 'Terminal=false'; \
		printf '%s\n' 'Categories=Office;Calendar;'; \
		printf '%s\n' 'StartupNotify=true'; \
	} > "$(DESKTOP_FILE)"
	chmod 644 "$(DESKTOP_FILE)"
	@if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(DESKTOP_DIR)"; fi

uninstall-local:
	rm -rf "$(INSTALL_DIR)"
	rm -f "$(DESKTOP_FILE)"
	rm -f "$(ICON_FILE)"
	@if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$(DESKTOP_DIR)"; fi

clean-build:
	rm -rf build dist

lint:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff check .

format-check:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff format --check .

test:
	QT_QPA_PLATFORM=$(QT_QPA_PLATFORM) UV_CACHE_DIR=$(UV_CACHE_DIR) uv run pytest

py-compile:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
