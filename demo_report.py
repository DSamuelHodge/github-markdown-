from jinja2 import Template
from pathlib import Path
import json
from datetime import datetime

# Sample data for demonstration
demo_data = {
    "repo_name": "BAML",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_files": 100,
    "total_lines": 50000,
    "total_size": "10MB",
    "total_tokens": 1000000,
    
    # Issue metrics
    "performance_issues": 10,
    "performance_trend": 0,  # 0% increase
    "style_issues": 50,
    "security_issues": 0,
    "documentation_issues": 20,
    "coverage_issues": 10,
    "type_check_issues": 0,
    "bug_risks": 50,
    "total_issues": 140,
    
    "hot_spots": [
        {
            "file": "baml/integ-tests/python/baml_client/types.py",
            "severity": "high",
            "complexity": 25,
            "changes_count": 154,
            "issues_count": 12,
            "recommendation": "Consider breaking down the large types.py file into smaller modules by category. Current file has over 150 class definitions."
        },
        {
            "file": "baml/engine/language_client_python/python_src/baml_py/stream.py",
            "severity": "medium",
            "complexity": 15,
            "changes_count": 8,
            "issues_count": 4,
            "recommendation": "Add more comprehensive error handling and documentation to stream processing classes."
        }
    ],
    
    "tech_debt": [
        {
            "name": "Code Organization",
            "hours": 32,
            "percentage": 45,
            "issues": [
                "Large types.py file with 150+ class definitions",
                "Complex inheritance hierarchies in client types",
                "Scattered enum definitions"
            ]
        },
        {
            "name": "Documentation",
            "hours": 24,
            "percentage": 35,
            "issues": [
                "Missing docstrings in key classes",
                "Incomplete API documentation",
                "Limited usage examples"
            ]
        },
        {
            "name": "Testing",
            "hours": 16,
            "percentage": 20,
            "issues": [
                "Integration tests could use more coverage",
                "Missing unit tests for stream handling",
                "Limited error case testing"
            ]
        }
    ],
    
    "dependencies": [
        {
            "name": "pydantic",
            "current_version": "2.7.1",
            "latest_version": "2.7.1",
            "outdated": False,
            "vulnerable": False
        },
        {
            "name": "pytest",
            "current_version": "8.2.1",
            "latest_version": "8.2.1",
            "outdated": False,
            "vulnerable": False
        },
        {
            "name": "ruff",
            "current_version": "0.3.3",
            "latest_version": "0.3.3",
            "outdated": False,
            "vulnerable": False
        }
    ],
    
    "performance_insights": [
        {
            "type": "Code Organization",
            "impact": "high",
            "impact_description": "Maintenance Impact",
            "description": "Large type definition file affects development velocity",
            "code_example": """
# Current structure (types.py with 150+ classes)
class Category(str, Enum): ...
class Color(str, Enum): ...
class DataType(str, Enum): ...
# ... 147+ more classes

# Recommended structure
# category_types.py
class Category(str, Enum): ...

# color_types.py
class Color(str, Enum): ...

# data_types.py
class DataType(str, Enum): ...""",
            "suggestion": "Split types.py into domain-specific modules"
        },
        {
            "type": "Stream Processing",
            "impact": "medium",
            "impact_description": "Error Handling",
            "description": "Stream processing could benefit from better error handling",
            "code_example": """
# Current implementation
class BamlStream(Generic[PartialOutputType, FinalOutputType]):
    def __init__(self):
        self._stream = ...

# Recommended implementation
class BamlStream(Generic[PartialOutputType, FinalOutputType]):
    def __init__(self):
        self._stream = ...
        self._error_handlers = []
    
    def on_error(self, handler: Callable[[Exception], None]):
        self._error_handlers.append(handler)
        return self""",
            "suggestion": "Add error handling hooks to stream processing"
        }
    ],
    
    "debt_hours": 72,
    "outdated_deps": 0,
    "vulnerable_deps": 0
}

def generate_demo_report():
    # Read the template
    template_path = Path(__file__).parent / "github_markdown" / "templates" / "report.html"
    with open(template_path, 'r') as f:
        template = Template(f.read())
    
    # Generate the report
    html_content = template.render(**demo_data)
    
    # Save the report
    output_path = Path(__file__).parent / "demo_report.html"
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Demo report generated at: {output_path}")

if __name__ == "__main__":
    generate_demo_report()
