"""
OneExtraction - B2B Lead Intelligence Platform
Setup configuration for package installation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="oneextraction",
    version="1.0.0",
    author="Your Team",
    author_email="team@oneextraction.io",
    description="B2B Lead Intelligence Platform - Aggregate & enrich business data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/OneExtraction",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Business/Corporate",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "sentry-sdk>=1.38.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "oneextraction=src.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
