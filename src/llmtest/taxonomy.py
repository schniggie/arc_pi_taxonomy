import os
from pathlib import Path
from typing import Dict, List

class Taxonomy:
    def __init__(self, taxonomy_path: str = "."):
        self.base_path = Path(taxonomy_path)
        self.intents = self._load_category("attack_intents")
        self.techniques = self._load_category("attack_techniques")
        self.evasions = self._load_category("attack_evasions")

    def _load_category(self, category_dir: str) -> Dict[str, str]:
        """
        Loads a category of the taxonomy from a directory, including content.
        Handles nested directories.
        """
        category_path = self.base_path / category_dir
        items = {}
        if not category_path.is_dir():
            return items

        for file_path in category_path.rglob("*.md"):
            # Create a relative path string from the category base
            relative_path = file_path.relative_to(category_path)
            # Create a unique name by joining the parts, and remove the .md suffix
            name = str(relative_path.with_suffix(""))

            # Skip README.md files
            if name.lower() == "readme":
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                items[name] = content
            except Exception:
                # In case of reading errors, we can skip the file
                # or log the error. For now, we'll just skip.
                continue

        return items

def load_taxonomy(taxonomy_path: str = ".") -> Taxonomy:
    """
    Loads the full taxonomy from the given path.
    """
    return Taxonomy(taxonomy_path)

if __name__ == '__main__':
    # Example usage:
    taxonomy = load_taxonomy()
    print("Loaded Intents:", list(taxonomy.intents.keys()))
    print("\nLoaded Techniques:", list(taxonomy.techniques.keys()))
    print("\nLoaded Evasions:", list(taxonomy.evasions.keys()))

    # Example of accessing content
    if "jailbreak" in taxonomy.intents:
        print("\nContent of 'jailbreak' intent:")
        print(taxonomy.intents["jailbreak"][:200] + "...")
