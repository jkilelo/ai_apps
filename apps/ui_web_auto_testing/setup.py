"""
Setup script for Web Automation Testing Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web-automation-framework",
    version="1.0.0",
    author="Web Automation Team",
    author_email="team@webautomation.com",
    description="A powerful 4-step framework for automated web testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/web-automation-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "pydantic>=2.0.0",
        "playwright>=1.40.0",
        "pytest>=7.0.0",
        "pytest-playwright>=0.4.0",
        "python-dotenv>=0.19.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-click>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "web-automation=apps.ui_web_auto_testing.cli:main",
            "wa=apps.ui_web_auto_testing.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
)