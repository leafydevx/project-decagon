from setuptools import setup, find_packages

setup(
    name="snapback",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "snapback=snapback.cli:main",
        ],
    },
    python_requires=">=3.8",
)
