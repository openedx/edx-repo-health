import argparse
import pytest
import pathlib



def main():
    checks_dir = pathlib.Path(__file__).parent.parent.absolute()
    pytest.main(["-c", "<()", "--noconftest", "--repo-health", "--repo-health-path", str(checks_dir)])


if __name__ == "__main__":
    main()
