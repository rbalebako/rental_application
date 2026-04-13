"""Caching utilities for field mappings."""

import json
from pathlib import Path
from typing import Dict, Optional

from rental_application.config import config


class FieldMappingCache:
    """Manages caching of field mappings to avoid repeated LLM calls."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to config.cache_dir
        """
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, source_schema: str, target_schema: str) -> str:
        """Generate a cache key for a source-target schema pair.

        Args:
            source_schema: Name/identifier of source form
            target_schema: Name/identifier of target form

        Returns:
            Cache key string
        """
        # Create a deterministic key
        return f"{source_schema}__to__{target_schema}".lower().replace(" ", "_")

    def _get_cache_path(self, source_schema: str, target_schema: str) -> Path:
        """Get the file path for a cached mapping.

        Args:
            source_schema: Name/identifier of source form
            target_schema: Name/identifier of target form

        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(source_schema, target_schema)
        return self.cache_dir / f"{cache_key}.json"

    def save_mapping(
        self,
        source_schema: str,
        target_schema: str,
        mapping: Dict[str, str],
    ) -> None:
        """Save a field mapping to cache.

        Args:
            source_schema: Name/identifier of source form
            target_schema: Name/identifier of target form
            mapping: Dictionary mapping target fields to source fields
        """
        cache_path = self._get_cache_path(source_schema, target_schema)
        try:
            with open(cache_path, "w") as f:
                json.dump({"mapping": mapping, "schemas": {
                    "source": source_schema,
                    "target": target_schema
                }}, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save mapping cache: {e}")

    def load_mapping(
        self,
        source_schema: str,
        target_schema: str,
    ) -> Optional[Dict[str, str]]:
        """Load a field mapping from cache.

        Args:
            source_schema: Name/identifier of source form
            target_schema: Name/identifier of target form

        Returns:
            Cached mapping dictionary, or None if not found
        """
        cache_path = self._get_cache_path(source_schema, target_schema)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
                return data.get("mapping")
        except Exception as e:
            print(f"Warning: Failed to load mapping cache: {e}")
            return None

    def clear_cache(self, source_schema: Optional[str] = None, target_schema: Optional[str] = None) -> None:
        """Clear cache entries.

        Args:
            source_schema: If provided, only clear caches for this source
            target_schema: If provided, only clear caches for this target
        """
        if source_schema is None and target_schema is None:
            # Clear entire cache
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Clear specific entries
            cache_path = self._get_cache_path(source_schema or "*", target_schema or "*")
            for path in self.cache_dir.glob(f"{cache_path.stem}*.json"):
                path.unlink()
