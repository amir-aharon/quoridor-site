import os
from setuptools import setup, find_packages


def get_requirements():
    # Get the absolute path to the directory containing setup.py
    this_directory = os.path.abspath(os.path.dirname(__file__))

    # Construct the path to requirements.txt relative to setup.py
    requirements_path = os.path.join(this_directory, "requirements.txt")

    # Read requirements from requirements.txt
    with open(requirements_path) as f:
        requirements = f.read().splitlines()

    return requirements


setup(
    name="quoridor_game",
    version="0.1.0",
    description="Quoridor game logic module",
    install_requires=get_requirements(),
    python_requires=">=3.13",
    entry_points={
        "console_scripts": [
            "quoridor = quoridor.main:main",
        ],
    },
)
