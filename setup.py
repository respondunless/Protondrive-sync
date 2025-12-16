"""Setup script for ProtonDrive Sync."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "ProtonDrive Sync - A Python-based sync application for ProtonDrive"

setup(
    name="protondrive-sync",
    version="1.0.0",
    author="ProtonDrive Sync Contributors",
    description="Sync your ProtonDrive files with rclone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/protondrive-sync",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    entry_points={
        "console_scripts": [
            "protondrive-sync=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
