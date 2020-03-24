"""
Checks to see if repo structure
"""

import glob
import os
import re
import pdb

module_dict_key = 'repo_structure'

def check_python_files(all_results, repo_path):
    """
    See if current repo has python files in it
    Only checks one level down(repo_path/*/*.py)
    """
    # first check if py exist in head file
    python_files = glob.glob(os.path.join(repo_path, "*.py"), recursive=True)
    all_results[module_dict_key]['has_python_files'] = False
    if len(python_files) > 0:
        all_results[module_dict_key]['has_python_files'] = True
    # if no py files in head dir, check below
    if not all_results[module_dict_key]['has_python_files']:
        subdirs = glob.glob('*')
        for name in subdirs:
            if os.path.isdir(os.path.join(repo_path, name)):
                python_files = glob.glob(os.path.join(repo_path,name,"*.py"), recursive=True)
                if len(python_files) > 0:
                    all_results[module_dict_key]['has_python_files'] = True



def check_necessary_files(all_results, repo_path):
    """ Test if each repo has required files """
    necessary_files = ['openedx.yaml', 'tox.ini', 'Makefile', '.travis.yml', 'README.rst', 'pylintrc']
    for filename in necessary_files:
        if os.path.isfile(os.path.join(repo_path, filename)):
            all_results[module_dict_key][filename] = True
        else:
            all_results[module_dict_key][filename] = False

def check_requirements(all_results, repo_path):
    """ Test if repo has req folders and necessary .in files """
    required_req_files = ['base.in', 'dev.in', 'doc.in', 'pip-tools.in', 'quality.in', 'test.in', 'travis.in']
    all_results[module_dict_key]['requirements'] = {}
    if os.path.isdir(os.path.join(repo_path,'requirements')):
        all_results[module_dict_key]['requirements_folder'] = True
        for filename in required_req_files:
            files = glob.glob(os.path.join(repo_path, "requirements/**/", filename), recursive=True)
            # check if any files names filename were found
            if files:
                all_results[module_dict_key]['requirements'][filename] = True
    else:
        all_results[module_dict_key]['requirements_folder'] = False
        for filename in required_req_files:
            all_results[module_dict_key]['requirements'][filename] = False
