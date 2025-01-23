import tiktoken
from typing import Dict, Optional, List
from pathlib import Path
import tempfile
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import git
from git.exc import GitCommandError
from .config import AnalysisConfig

class GitHubAnalyzer:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.token_counter = tiktoken.get_encoding(config.token_encoding)
        self.analysis_data = {}

    def parse_github_url(self, github_url: str) -> tuple:
        """Parse GitHub URL to extract repository URL and subdirectory path."""
        github_url = github_url.rstrip('/')
        url_parts = github_url.split('/')
        tree_pos = -1
        for i, part in enumerate(url_parts):
            if part in ['tree', 'blob']:
                tree_pos = i
                break
        if tree_pos != -1:
            repo_url = '/'.join(url_parts[:tree_pos])
            subdirectory = '/'.join(url_parts[tree_pos + 2:]) if len(url_parts) > tree_pos + 2 else ''
        else:
            repo_url = github_url
            subdirectory = ''
        return repo_url, subdirectory

    def clone_repository(self, github_url: str, target_dir: str) -> Optional[git.Repo]:
        """Clone a GitHub repository."""
        try:
            print(f"Cloning {github_url}...")
            return git.Repo.clone_from(github_url, target_dir)
        except GitCommandError as e:
            print(f"Failed to clone repository: {e}")
            return None

    def process_file(self, file_path: Path, repo_root: Path) -> Dict:
        """Process a single file and return its analysis results."""
        try:
            if file_path.stat().st_size > self.config.max_file_size:
                print(f"Skipping large file: {file_path}")
                return {"skip": True}

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return {
                    "content": content,
                    "tokens": len(self.token_counter.encode(content)),
                    "relative_path": str(file_path.relative_to(repo_root)),
                    "extension": file_path.suffix,
                    "skip": False
                }
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {"skip": True}

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}GB"

    def count_lines(self, content: str) -> int:
        """Count non-empty lines in content."""
        return len([line for line in content.splitlines() if line.strip()])

    def analyze_repository(self, github_url: str, output_dir: Optional[str] = None) -> Dict:
        """Analyze repository and generate both markdown and HTML reports."""
        repo_url, subdirectory = self.parse_github_url(github_url)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                repo = git.Repo.clone_from(repo_url, temp_dir)
                self.analysis_data = self._gather_repository_data(repo, subdirectory)
                
                # Generate both report formats
                if output_dir:
                    output_path = Path(output_dir)
                else:
                    output_path = Path.cwd()
                
                markdown_path = output_path / "repository_analysis.md"
                html_path = output_path / "repository_analysis.html"
                
                self._generate_markdown_report(markdown_path)
                self._generate_html_report(html_path)
                
                return self.analysis_data
            except GitCommandError as e:
                raise ValueError(f"Failed to clone repository: {e}")

    def _gather_repository_data(self, repo: git.Repo, subdirectory: str) -> Dict:
        """Gather comprehensive repository data for analysis."""
        data = {
            "repo_name": repo.remotes.origin.url.split('/')[-1].replace('.git', ''),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": {}
        }

        # Basic stats
        stats = self._gather_basic_stats(repo, subdirectory)
        data["analysis"]["basic_stats"] = stats

        # Code quality metrics
        quality = self._analyze_code_quality(repo, subdirectory)
        data["analysis"]["code_quality"] = quality

        # Dependency analysis
        deps = self._analyze_dependencies(repo, subdirectory)
        data["analysis"]["dependencies"] = deps

        # Hot spots analysis
        hotspots = self._find_hot_spots(repo, subdirectory)
        data["analysis"]["hot_spots"] = hotspots

        # Technical debt estimation
        debt = self._estimate_technical_debt(quality, hotspots)
        data["analysis"]["tech_debt"] = debt

        return data

    def _generate_markdown_report(self, output_path: Path):
        """Generate a markdown report optimized for LLM consumption."""
        data = self.analysis_data
        
        with open(output_path, 'w') as f:
            f.write(f"# Repository Analysis Report: {data['repo_name']}\n\n")
            f.write(f"Generated on: {data['timestamp']}\n\n")
            
            # Basic Statistics
            f.write("## Repository Statistics\n")
            stats = data["analysis"]["basic_stats"]
            f.write(f"- Total Files: {stats['total_files']}\n")
            f.write(f"- Lines of Code: {stats['total_lines']}\n")
            f.write(f"- Repository Size: {stats['total_size']}\n\n")
            
            # Code Quality Section
            f.write("## Code Quality Analysis\n")
            quality = data["analysis"]["code_quality"]
            f.write("\n### Issues Summary\n")
            f.write(f"- Performance Issues: {quality['performance_issues']}\n")
            f.write(f"- Style Issues: {quality['style_issues']}\n")
            f.write(f"- Security Issues: {quality['security_issues']}\n")
            f.write(f"- Documentation Issues: {quality['documentation_issues']}\n\n")
            
            # Hot Spots
            f.write("## Code Hot Spots\n")
            for spot in data["analysis"]["hot_spots"]:
                f.write(f"\n### {spot['file']}\n")
                f.write(f"- Complexity Score: {spot['complexity']}\n")
                f.write(f"- Recent Changes: {spot['changes_count']}\n")
                f.write(f"- Issues Count: {spot['issues_count']}\n")
                f.write(f"- Recommendation: {spot['recommendation']}\n")
            
            # Technical Debt
            f.write("\n## Technical Debt Analysis\n")
            debt = data["analysis"]["tech_debt"]
            f.write(f"\nEstimated Resolution Time: {debt['total_hours']} hours\n\n")
            for category in debt["categories"]:
                f.write(f"### {category['name']}\n")
                f.write(f"- Estimated Hours: {category['hours']}\n")
                f.write("- Key Issues:\n")
                for issue in category["issues"]:
                    f.write(f"  - {issue}\n")
            
            # Dependencies
            f.write("\n## Dependencies\n")
            deps = data["analysis"]["dependencies"]
            f.write(f"\nTotal Dependencies: {len(deps)}\n")
            f.write(f"Outdated: {sum(1 for d in deps if d['outdated'])}\n")
            f.write(f"Security Vulnerabilities: {sum(1 for d in deps if d['vulnerable'])}\n\n")
            
            for dep in deps:
                if dep['outdated'] or dep['vulnerable']:
                    f.write(f"### {dep['name']}\n")
                    f.write(f"- Current Version: {dep['current_version']}\n")
                    f.write(f"- Latest Version: {dep['latest_version']}\n")
                    if dep['vulnerable']:
                        f.write(f"- Security Issue: {dep['vulnerability_details']}\n")

    def _generate_html_report(self, output_path: Path):
        """Generate an interactive HTML report with visualizations."""
        from jinja2 import Template
        template_path = Path(__file__).parent / "templates" / "report.html"
        
        with open(template_path) as f:
            template = Template(f.read())
        
        html_content = template.render(**self.analysis_data)
        
        with open(output_path, 'w') as f:
            f.write(html_content)

    def _analyze_code_quality(self, repo: git.Repo, subdirectory: str) -> Dict:
        """Analyze code quality metrics."""
        # Implementation details here
        pass

    def _analyze_dependencies(self, repo: git.Repo, subdirectory: str) -> List[Dict]:
        """Analyze project dependencies."""
        # Implementation details here
        pass

    def _find_hot_spots(self, repo: git.Repo, subdirectory: str) -> List[Dict]:
        """Identify code hot spots."""
        # Implementation details here
        pass

    def _estimate_technical_debt(self, quality: Dict, hotspots: List[Dict]) -> Dict:
        """Estimate technical debt based on analysis."""
        # Implementation details here
        pass

    def _gather_basic_stats(self, repo: git.Repo, subdirectory: str) -> Dict:
        """Gather basic repository statistics."""
        # Implementation details here
        pass

    def generate_output(self, analysis_results: Dict) -> str:
        """Generate analysis output in the specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = f"{analysis_results['repository']}_analysis_{timestamp}"

        if self.config.output_format == "markdown":
            output_path += ".md"
            self.generate_markdown(analysis_results, output_path)
        elif self.config.output_format == "json":
            output_path += ".json"
            self.generate_json(analysis_results, output_path)
        else:
            print(f"Unsupported output format: {self.config.output_format}")
            return ""

        return output_path

    def generate_markdown(self, analysis_results: Dict, output_path: str):
        """Generate Markdown documentation with enhanced source tree."""
        with open(output_path, 'w', encoding='utf-8') as f:
            # Repository header
            repo_name = analysis_results['repository']
            f.write(f"# {repo_name} Analysis\n\n")

            # Summary section
            total_files = len(analysis_results['files'])
            total_lines = sum(self.count_lines(file['content']) for file in analysis_results['files'])
            total_size = sum(len(file['content'].encode('utf-8')) for file in analysis_results['files'])

            f.write("## Repository Summary\n\n")
            f.write(f"- **Generated:** {analysis_results['timestamp']}\n")
            f.write(f"- **Total Files:** {total_files:,}\n")
            f.write(f"- **Total Lines:** {total_lines:,}\n")
            f.write(f"- **Total Size:** {self.format_size(total_size)}\n")
            f.write(f"- **Total Tokens:** {analysis_results['total_tokens']:,}\n\n")

            # File type statistics
            extension_stats = {}
            for file in analysis_results['files']:
                ext = file['extension']
                content = file['content']
                size = len(content.encode('utf-8'))
                lines = self.count_lines(content)

                if ext not in extension_stats:
                    extension_stats[ext] = {'count': 0, 'lines': 0, 'size': 0}
                
                stats = extension_stats[ext]
                stats['count'] += 1
                stats['lines'] += lines
                stats['size'] += size

            f.write("## File Type Statistics\n\n")
            f.write("| Extension | Files | Lines | Size |\n")
            f.write("|-----------|-------|-------|------|\n")
            for ext, stats in sorted(extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
                f.write(f"| {ext or 'no ext'} | {stats['count']:,} | {stats['lines']:,} | {self.format_size(stats['size'])} |\n")

    def generate_json(self, analysis_results: Dict, output_path: str):
        """Generate JSON output."""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2)

    def analyze_repo(self, repo_url):
        # Logic for analyzing a GitHub repository
        print(f"Analyzing repository: {repo_url}")
        # Simulate analysis logic
        analysis_result = {
            'repository': repo_url,
            'files_analyzed': 42,
            'total_lines': 1234,
            'total_size': '2.3MB'
        }
        return analysis_result

    def generate_report(self, analysis_result):
        # Logic for generating a report
        print("Generating report...")
        report = f"Repository: {analysis_result['repository']}\nFiles Analyzed: {analysis_result['files_analyzed']}\nTotal Lines: {analysis_result['total_lines']}\nTotal Size: {analysis_result['total_size']}\n"
        print(report)
        return report

# Other classes and functions can be added here as needed.
