from dataclasses import dataclass
from typing import Set, Dict, Optional
import json

@dataclass
class AnalysisConfig:
    """Configuration for the analysis process."""
    extensions: Set[str]
    exclude_dirs: Set[str]
    max_file_size: int
    token_encoding: str
    max_workers: int
    output_format: str

    @classmethod
    def get_default_config(cls) -> Dict:
        return {
            "extensions": [".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".java", ".c", ".cpp", ".h", ".cs", ".rb", ".php", ".go", ".rs", ".swift", ".kt", ".scala", ".pl", ".lua", ".r", ".sql", ".sh", ".bat", ".m", ".vb", ".erl", ".ex", ".clj", ".hs", ".s", ".asm", ".ps1", ".groovy", ".f", ".f90", ".lisp", ".lsp", ".fs", ".ml", ".jl"],
            "exclude_dirs": [".git", "node_modules", "__pycache__", ".venv"],
            "max_file_size": 1024 * 1024,  # 1MB
            "token_encoding": "cl100k_base",
            "max_workers": 4,
            "output_format": "markdown"
        }

    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> 'AnalysisConfig':
        """Load configuration from a JSON file or use defaults."""
        default_config = cls.get_default_config()

        if config_path:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    config = {**default_config, **config}
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load config file ({str(e)}). Using defaults.")
                config = default_config
        else:
            config = default_config

        return cls(
            extensions=set(config["extensions"]),
            exclude_dirs=set(config["exclude_dirs"]),
            max_file_size=config["max_file_size"],
            token_encoding=config["token_encoding"],
            max_workers=config["max_workers"],
            output_format=config["output_format"]
        )
