#!/usr/bin/env python3
"""
Setup script for DS-pyVDC-API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README_IMPLEMENTATION.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ds-vdc-api",
    version="1.0.0",
    author="DS-pyVDC-API Contributors",
    description="Python implementation of the digitalSTROM vDC API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KarlKiel/DS-pyVDC-API",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "protobuf>=3.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
        "discovery": [
            "zeroconf>=0.38.0",
        ],
    },
    package_data={
        "ds_vdc_api": ["*.proto"],
    },
)
