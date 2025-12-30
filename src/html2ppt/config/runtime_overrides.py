"""In-memory runtime settings overrides.

This module provides a minimal, process-local override store for settings that
need to be changed at runtime (e.g., via a settings API) without touching `.env`.
"""

from __future__ import annotations

from threading import RLock
from typing import Any


_lock = RLock()
_overrides: dict[str, dict[str, Any]] = {}


def get_override(namespace: str) -> dict[str, Any] | None:
    """Return a shallow copy of the override dict for a namespace."""
    with _lock:
        override = _overrides.get(namespace)
        return dict(override) if override else None


def set_override(namespace: str, override: dict[str, Any]) -> None:
    """Replace the override dict for a namespace."""
    with _lock:
        _overrides[namespace] = dict(override)


def update_override(namespace: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Update a namespace override dict with a patch and return the new override."""
    with _lock:
        current = dict(_overrides.get(namespace) or {})
        current.update(patch)
        _overrides[namespace] = current
        return dict(current)


def clear_override(namespace: str) -> None:
    """Remove a namespace override dict."""
    with _lock:
        _overrides.pop(namespace, None)
