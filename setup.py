from setuptools import setup, find_packages

setup(
    name="github-markdown",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "tiktoken>=0.5.1",
        "gitpython>=3.1.40",
        "jinja2>=3.1.2",
        "radon>=6.0.1",
        "ruff>=0.1.9",
        "requirements-parser>=0.5.0",
        "packaging>=23.2"
    ],
    package_data={
        "github_markdown": ["templates/*.html"],
    },
    entry_points={
        "console_scripts": [
            "github-analyze=github_markdown.github_analyzer:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for analyzing GitHub repositories and generating insightful markdown and HTML reports",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/github-markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
