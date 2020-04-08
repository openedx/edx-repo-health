"""
This package contains checks for edx repo standards
"""
import codecs
import os
from configparser import ConfigParser
from pathlib import Path
import glob


__version__ = "0.1.0"


def parse_config_file(path):
    """
    Get the parsed content of an INI-style config file (using ConfigParser).
    Used for pytest fixtures.
    """
    config = ConfigParser()
    if os.path.exists(path):
        config.read(path)
    return config


def get_file_content(path):
    """
    Get the content of the UTF-8 text file at the specified path.
    Used for pytest fixtures.
    """
    if not os.path.exists(path):
        return ''
    with codecs.open(path, 'r', 'utf-8') as f:
        return f.read()


def get_file_lines(path):
    """
    Get a list of the lines in the UTF-8 text file at the specified path.
    Strips leading and trailing whitespace from each line.
    Used for pytest fixtures.
    """
    if not os.path.exists(path):
        return []
    with codecs.open(path, 'r', 'utf-8') as f:
        return [line.strip() for line in f.readlines()]

def get_file_names(path, file_type):
    """
    Get a list of files with given file_type in path's directory and its subdirectories
    If the directory is large, this might take forever, so use with care
    """
    path_pattern = path + "**/*." + file_type
    files = glob.glob(path_pattern, recursive=True)
    return files
