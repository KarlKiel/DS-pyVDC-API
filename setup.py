"""Setup script for DS-pyVDC-API."""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ds-pyvdc-api",
    version="0.1.0",
    description="A Python API for VDC (Virtual Data Center) operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KarlKiel/DS-pyVDC-API",
    author="KarlKiel",
    license="GPL-3.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/KarlKiel/DS-pyVDC-API/issues",
        "Source": "https://github.com/KarlKiel/DS-pyVDC-API",
    },
)
