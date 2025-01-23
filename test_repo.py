from github_markdown.github_analyzer import GitHubAnalyzer
from github_markdown.config import AnalysisConfig

def main():
    # Create configuration with increased file size limit (3MB)
    config = AnalysisConfig(
        extensions={'.py', '.ipynb', '.md', '.txt', '.yml', '.yaml', '.json'},
        exclude_dirs={'.git', 'node_modules', '__pycache__', '.venv'},
        max_file_size=3 * 1024 * 1024,  # 3MB
        token_encoding='cl100k_base',
        max_workers=4,
        output_format='markdown'
    )

    # Initialize analyzer
    analyzer = GitHubAnalyzer(config)

    # Analyze repository
    repo_url = "https://github.com/DSamuelHodge/ai-data-science-team.git"
    print(f"\nAnalyzing repository: {repo_url}")
    success = analyzer.analyze_repository(repo_url)
    
    if success:
        print("Analysis completed successfully!")
    else:
        print("Analysis failed.")

if __name__ == "__main__":
    main()
