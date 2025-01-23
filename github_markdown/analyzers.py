"""Code analysis implementations for GitHub repository analyzer."""

import os
from typing import Dict, List
import git
from pathlib import Path
import re
from radon.complexity import cc_visit
from radon.metrics import h_visit
import pkg_resources
import requirements
import json
import subprocess

def analyze_code_quality(repo_path: str, subdirectory: str = "") -> Dict:
    """Analyze code quality metrics."""
    quality_data = {
        "performance_issues": 0,
        "style_issues": 0,
        "security_issues": 0,
        "documentation_issues": 0,
        "type_check_issues": 0,
        "bug_risks": 0
    }
    
    # Use ruff for linting
    try:
        result = subprocess.run(
            ["ruff", "check", repo_path, "--format", "json"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            issues = json.loads(result.stdout)
            for issue in issues:
                if "performance" in issue["code"].lower():
                    quality_data["performance_issues"] += 1
                elif "style" in issue["code"].lower():
                    quality_data["style_issues"] += 1
                elif "security" in issue["code"].lower():
                    quality_data["security_issues"] += 1
                elif "doc" in issue["code"].lower():
                    quality_data["documentation_issues"] += 1
                elif "type" in issue["code"].lower():
                    quality_data["type_check_issues"] += 1
                else:
                    quality_data["bug_risks"] += 1
    except subprocess.CalledProcessError:
        pass  # Ruff not installed or failed
    
    return quality_data

def analyze_dependencies(repo_path: str) -> List[Dict]:
    """Analyze project dependencies."""
    deps = []
    req_files = []
    
    # Find requirements files
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file in ["requirements.txt", "pyproject.toml", "setup.py"]:
                req_files.append(os.path.join(root, file))
    
    for req_file in req_files:
        if req_file.endswith(".txt"):
            with open(req_file) as f:
                for req in requirements.parse(f):
                    if req.name:
                        try:
                            latest = pkg_resources.working_set.by_key[req.name].version
                            deps.append({
                                "name": req.name,
                                "current_version": req.specs[0][1] if req.specs else "Unknown",
                                "latest_version": latest,
                                "outdated": req.specs[0][1] != latest if req.specs else False,
                                "vulnerable": False  # Would need safety-db integration
                            })
                        except KeyError:
                            continue
    
    return deps

def find_hot_spots(repo: git.Repo, repo_path: str) -> List[Dict]:
    """Identify code hot spots based on complexity and change frequency."""
    hot_spots = []
    
    # Get commit history for files
    file_changes = {}
    for commit in repo.iter_commits():
        for file in commit.stats.files:
            if file.endswith('.py'):
                file_changes[file] = file_changes.get(file, 0) + 1
    
    # Analyze complexity
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path) as f:
                        content = f.read()
                    
                    # Calculate complexity
                    complexity = max(
                        (block.complexity for block in cc_visit(content)),
                        default=0
                    )
                    
                    if complexity > 10 or file_changes.get(rel_path, 0) > 10:
                        hot_spots.append({
                            "file": rel_path,
                            "severity": "high" if complexity > 20 else "medium",
                            "complexity": complexity,
                            "changes_count": file_changes.get(rel_path, 0),
                            "issues_count": len(list(cc_visit(content))),
                            "recommendation": _generate_recommendation(complexity, content)
                        })
                except Exception:
                    continue
    
    return sorted(hot_spots, key=lambda x: (x["complexity"], x["changes_count"]), reverse=True)

def estimate_technical_debt(quality: Dict, hotspots: List[Dict]) -> Dict:
    """Estimate technical debt based on analysis results."""
    categories = []
    total_hours = 0
    
    # Code organization debt
    if hotspots:
        org_hours = sum(spot["complexity"] * 2 for spot in hotspots)
        categories.append({
            "name": "Code Organization",
            "hours": org_hours,
            "percentage": 0,  # Will calculate after total
            "issues": [
                f"Complex code in {spot['file']} (complexity: {spot['complexity']})"
                for spot in hotspots[:3]
            ]
        })
        total_hours += org_hours
    
    # Documentation debt
    if quality["documentation_issues"] > 0:
        doc_hours = quality["documentation_issues"] * 1.5
        categories.append({
            "name": "Documentation",
            "hours": doc_hours,
            "percentage": 0,
            "issues": ["Missing or incomplete documentation"]
        })
        total_hours += doc_hours
    
    # Testing debt based on complexity
    test_hours = sum(spot["complexity"] for spot in hotspots) * 1.5
    categories.append({
        "name": "Testing",
        "hours": test_hours,
        "percentage": 0,
        "issues": ["Insufficient test coverage for complex code"]
    })
    total_hours += test_hours
    
    # Calculate percentages
    for category in categories:
        category["percentage"] = round((category["hours"] / total_hours) * 100)
    
    return {
        "categories": categories,
        "total_hours": total_hours
    }

def _generate_recommendation(complexity: int, content: str) -> str:
    """Generate specific recommendations based on code analysis."""
    if complexity > 20:
        return "Consider breaking down this file into smaller, more focused modules"
    elif complexity > 15:
        return "Reduce method complexity by extracting helper functions"
    elif len(content.splitlines()) > 300:
        return "File is too long, consider splitting it into multiple files"
    else:
        return "Add more comprehensive documentation and tests"
