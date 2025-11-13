import json
import os
import re

import yaml

from src.media_title import MediaTitle

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
        # Write JSON file
        with open (self.path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(), f, ensure_ascii=False, indent=4)
            return True

    def to_yaml(self) -> bool:
        # Write YAML file
        with open (self.path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._to_dict(), f, allow_unicode=True, sort_keys=False)
            return True

    def _to_dict(self):
        # Convert MediaTitle to dict
        media_title_dict = vars(self.media_title)
        media_title_dict["imdb_rating"] = str(media_title_dict["imdb_rating"])
        return media_title_dict