# GitHub Markdown Analyzer

A Python package for analyzing GitHub repositories and generating both detailed markdown documentation and interactive HTML reports. This tool helps you understand repository structure, code quality, and technical debt while providing actionable insights.

## Features

- **Dual Output Formats**:
  - Markdown reports optimized for LLM processing and documentation
  - Interactive HTML reports with visualizations and metrics
  
- **Code Quality Analysis**:
  - Identify code hot spots and complexity issues
  - Track performance, style, and security issues
  - Measure and visualize technical debt
  - Dependencies analysis and vulnerability checks

- **Repository Insights**:
  - Comprehensive code statistics
  - Change frequency analysis
  - Dependency tracking
  - Automated recommendations

- **Developer Experience**:
  - Parallel processing for fast analysis
  - Configurable analysis settings
  - Integration with common development tools
  - Support for multiple programming languages

## Installation

Install the package via pip:

```bash
pip install github-markdown
```

## Usage

Basic usage example:

```python
from github_markdown.github_analyzer import GitHubAnalyzer
from github_markdown.config import AnalysisConfig

# Create configuration
config = AnalysisConfig(
    extensions=['.py', '.js', '.java'],  # File types to analyze
    exclude_dirs=['.git', 'node_modules'],  # Directories to skip
    token_encoding='cl100k_base'  # Token encoding for analysis
)

# Initialize analyzer
analyzer = GitHubAnalyzer(config)

# Analyze repository and generate reports
analyzer.analyze_repository(
    github_url="https://github.com/username/repo",
    output_dir="./analysis"
)
```

This will generate two files:
- `repository_analysis.md`: Markdown report optimized for LLM processing
- `repository_analysis.html`: Interactive HTML report with visualizations

## Report Features

### Markdown Report
The markdown report includes:
- Repository statistics and metrics
- Code quality analysis
- Hot spots identification
- Technical debt assessment
- Dependency analysis
- Actionable recommendations

### HTML Report
The interactive HTML report provides:
- Visual metrics dashboard
- Code complexity charts
- Issue distribution graphs
- Technical debt visualization
- Dependency status
- Interactive code hot spots

## Configuration Options

```python
AnalysisConfig(
    # File extensions to analyze
    extensions=['.py', '.js', '.java'],
    
    # Directories to exclude
    exclude_dirs=['.git', 'node_modules'],
    
    # Token encoding for analysis
    token_encoding='cl100k_base',
    
    # Maximum parallel workers
    max_workers=4
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
