import ast
from typing import Dict, List, Any
from pathlib import Path
import radon.complexity as radon_complexity
from radon.visitors import ComplexityVisitor
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
import astroid

class CodeAnalyzer:
    def __init__(self):
        self.complexity_cache = {}
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for various metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if file_path.suffix == '.py':
                return self._analyze_python_file(content, file_path)
            else:
                return self._analyze_generic_file(content, file_path)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}
            
    def _analyze_python_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file for complexity and patterns."""
        results = {
            'file_path': str(file_path),
            'complexity_score': 0,
            'functions': [],
            'classes': [],
            'issues': [],
            'highlighted_code': self._highlight_code(content, file_path)
        }
        
        # Calculate cyclomatic complexity
        try:
            visitor = ComplexityVisitor.from_code(content)
            results['complexity_score'] = visitor.total_complexity
            
            # Analyze functions and classes
            for func in visitor.functions:
                results['functions'].append({
                    'name': func.name,
                    'complexity': func.complexity,
                    'lineno': func.lineno,
                    'length': func.endline - func.lineno
                })
        except:
            pass
            
        # Use astroid for more detailed analysis
        try:
            module = astroid.parse(content)
            results['classes'] = self._analyze_classes(module)
            results['issues'].extend(self._find_code_issues(module))
        except:
            pass
            
        return results
        
    def _analyze_generic_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze non-Python file."""
        return {
            'file_path': str(file_path),
            'highlighted_code': self._highlight_code(content, file_path)
        }
        
    def _analyze_classes(self, module: astroid.Module) -> List[Dict[str, Any]]:
        """Analyze classes in a Python module."""
        classes = []
        for node in module.body:
            if isinstance(node, astroid.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, astroid.FunctionDef):
                        methods.append({
                            'name': child.name,
                            'lineno': child.lineno,
                            'length': child.tolineno - child.lineno
                        })
                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'lineno': node.lineno
                })
        return classes
        
    def _find_code_issues(self, module: astroid.Module) -> List[str]:
        """Find potential code issues."""
        issues = []
        
        for node in module.nodes_of_class(astroid.FunctionDef):
            # Check for long functions
            if node.tolineno - node.lineno > 50:
                issues.append(f"Long function '{node.name}' ({node.tolineno - node.lineno} lines)")
                
            # Check for too many arguments
            if len(node.args.args) > 5:
                issues.append(f"Function '{node.name}' has too many arguments ({len(node.args.args)})")
                
        return issues
        
    def _highlight_code(self, content: str, file_path: Path) -> str:
        """Highlight code using Pygments."""
        try:
            lexer = get_lexer_for_filename(file_path.name)
            formatter = HtmlFormatter(linenos=True, cssclass="source")
            return highlight(content, lexer, formatter)
