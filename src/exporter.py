import json
import os
import re

import yaml

from media_title import MediaTitle

class Exporter:
    """
    Handles exporting MediaTitle objects to various file formats.

    Responsibilities:
        - Convert MediaTitle instances into dictionaries suitable for serialization.
        - Save data to YAML or JSON files.
    """
    def __init__(self, media_title: MediaTitle, path: str):
        self.media_title = media_title
        self.path = path

    def to_json(self) -> bool:
        full_path = self._get_full_path('json')

        # Write JSON file
        with open (full_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(), f, ensure_ascii=False, indent=4)
            return True

    def to_yaml(self) -> bool:
        full_path = self._get_full_path('yaml')

        # Write YAML file
        with open (full_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._to_dict(), f, allow_unicode=True, sort_keys=False)
            return True

    def _get_full_path(self, ext: str) -> str:
        # File type validation
        if ext not in ('json', 'yaml'):
            raise ValueError(f"Unsupported file type: {ext}")

        # Set file type
        if ext == 'json':
            extension = '.json'
        else:
            extension = '.yaml'

        # Create full path with filename
        filename = re.sub(r'[\\/:"*?<>|]+', '_', self.media_title.title)
        full_path = os.path.join(self.path, filename + extension)
        return full_path

    def _to_dict(self):
        # Convert MediaTitle to dict
        media_title_dict = vars(self.media_title)
        return media_title_dict