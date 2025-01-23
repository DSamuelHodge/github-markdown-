import unittest
from pathlib import Path
import tempfile
import shutil
from github_markdown.github_analyzer import GitHubAnalyzer
from github_markdown.config import AnalysisConfig

class TestGitHubAnalyzer(unittest.TestCase):
    def setUp(self):
        self.config = AnalysisConfig(
            extensions={'.py', '.md'},
            exclude_dirs={'.git', 'node_modules'},
            max_file_size=1024 * 1024,
            token_encoding='cl100k_base',
            max_workers=4,
            output_format='markdown'
        )
        self.analyzer = GitHubAnalyzer(self.config)

    def test_parse_github_url(self):
        # Test regular repository URL
        url = "https://github.com/username/repo"
        repo_url, subdirectory = self.analyzer.parse_github_url(url)
        self.assertEqual(repo_url, url)
        self.assertEqual(subdirectory, '')

        # Test repository URL with subdirectory
        url = "https://github.com/username/repo/tree/main/src"
        repo_url, subdirectory = self.analyzer.parse_github_url(url)
        self.assertEqual(repo_url, "https://github.com/username/repo")
        self.assertEqual(subdirectory, "src")

    def test_format_size(self):
        self.assertEqual(self.analyzer.format_size(500), "500.0B")
        self.assertEqual(self.analyzer.format_size(1024), "1.0KB")
        self.assertEqual(self.analyzer.format_size(1024 * 1024), "1.0MB")
        self.assertEqual(self.analyzer.format_size(1024 * 1024 * 1024), "1.0GB")

    def test_count_lines(self):
        content = "line1\n\nline2\n  \nline3"
        self.assertEqual(self.analyzer.count_lines(content), 3)

    def test_process_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            test_file = temp_dir_path / "test.py"
            
            # Create a test file
            with open(test_file, 'w') as f:
                f.write("print('Hello, World!')\n")

            result = self.analyzer.process_file(test_file, temp_dir_path)
            
            self.assertFalse(result["skip"])
            self.assertEqual(result["extension"], ".py")
            self.assertEqual(result["relative_path"], "test.py")
            self.assertTrue(result["tokens"] > 0)

if __name__ == '__main__':
    unittest.main()
