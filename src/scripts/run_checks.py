"""
Wrapper CLI around pytest call to allow users to use checks in this repo
without knowing much about pytest-repo-health
"""
import sys
from pathlib import Path

import pytest


def main():
    """
    Initiates pytest in repo-health mode
    """
    # get location of where edx-repo-health is located so that pytest knows where the checks are located
    checks_dir = Path(__file__).parent.parent.absolute()

    # Allow user to add further flags after run_check command and
    # pass those flags to pytest.
    flags = ["--noconftest", "--repo-health", "--repo-health-path", str(checks_dir)]
    flags.extend(sys.argv[1:])

    pytest.main(flags)



if __name__ == "__main__":
    main()
