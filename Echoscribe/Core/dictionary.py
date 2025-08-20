import csv
import sys
from pathlib import Path
from typing import Dict, Optional


class Dictionary:
    """
    Simple local dictionary reader that reads from CSV: Assets/dict/ecdict.csv
    Caches necessary fields, indexed by lowercase word.
    """

    def __init__(self, csv_path: Optional[Path] = None):
        """Initialize dictionary with optional custom CSV path."""
        self._entries: Dict[str, Dict[str, str]] = {}
        self._load(csv_path)

    def _get_application_path(self) -> Path:
        """Get application root directory path."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent.parent.parent

    def _default_csv_path(self) -> Path:
        """Get default dictionary CSV file path."""
        return self._get_application_path() / "Assets" / "dict" / "ecdict.csv"

    def _load(self, csv_path: Optional[Path]):
        """Load dictionary entries from CSV file."""
        path = Path(csv_path) if csv_path else self._default_csv_path()
        if not path.exists():
            print(f"Warning: Dictionary file not found - {path}")
            return
        try:
            # Try UTF-8 encoding first
            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = (row.get("word") or "").strip()
                    if not word:
                        continue
                    key = word.lower()
                    entry = {
                        "word": word,
                        "phonetic": (row.get("phonetic") or "").strip(),
                        "pos": (row.get("pos") or "").strip(),
                        "translation": (row.get("translation") or "").strip(),
                        "definition": (row.get("definition") or "").strip(),
                        "exchange": (row.get("exchange") or "").strip(),
                        "collins": (row.get("collins") or "").strip(),
                        "oxford": (row.get("oxford") or "").strip(),
                        "tag": (row.get("tag") or "").strip(),
                        "bnc": (row.get("bnc") or "").strip(),
                        "frq": (row.get("frq") or "").strip(),
                        "audio": (row.get("audio") or "").strip(),
                        "detail": (row.get("detail") or "").strip(),
                    }
                    self._entries[key] = entry
        except UnicodeDecodeError:
            # Fallback to UTF-8-SIG for BOM files
            with path.open("r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = (row.get("word") or "").strip()
                    if not word:
                        continue
                    key = word.lower()
                    entry = {
                        "word": word,
                        "phonetic": (row.get("phonetic") or "").strip(),
                        "pos": (row.get("pos") or "").strip(),
                        "translation": (row.get("translation") or "").strip(),
                        "definition": (row.get("definition") or "").strip(),
                        "exchange": (row.get("exchange") or "").strip(),
                        "collins": (row.get("collins") or "").strip(),
                        "oxford": (row.get("oxford") or "").strip(),
                        "tag": (row.get("tag") or "").strip(),
                        "bnc": (row.get("bnc") or "").strip(),
                        "frq": (row.get("frq") or "").strip(),
                        "audio": (row.get("audio") or "").strip(),
                        "detail": (row.get("detail") or "").strip(),
                    }
                    self._entries[key] = entry

    def lookup(self, word: str) -> Optional[Dict[str, str]]:
        """Look up a word in the dictionary.
        
        Args:
            word: The word to look up (case-insensitive)
            
        Returns:
            Dictionary entry with word details, or None if not found
        """
        if not word:
            return None
        return self._entries.get(word.strip().lower())


