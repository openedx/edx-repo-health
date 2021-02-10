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

    # Allow user to add further flags after run_check command and
    # pass those flags to pytest.
    parser = argparse.ArgumentParser()
    args, unknown_args = parser.parse_known_args()

    checks_dir = pathlib.Path(__file__).parent.parent.absolute()
    flags = ["--noconftest", "--repo-health", "--repo-health-path", str(checks_dir)]
    flags.extend(unknown_args)
    pytest.main(flags)


if __name__ == "__main__":
    main()
