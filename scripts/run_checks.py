"""
Wrapper CLI around pytest call to allow users to use checks in this repo
without knowing much about pytest-repo-health
"""
import argparse
import pytest
import pathlib


def main():
    """
    Initiates pytest in repo-health mode
    """
    checks_dir = pathlib.Path(__file__).parent.parent.absolute()
    pytest.main(["-c", "<()", "--noconftest", "--repo-health", "--repo-health-path", str(checks_dir)])


if __name__ == "__main__":
    main()
