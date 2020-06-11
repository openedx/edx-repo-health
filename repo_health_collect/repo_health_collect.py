import os
import subprocess
import sys
import tempfile

import codecs
import yaml


def main():
    components_file_path = sys.argv[1]
    output_dir_path = sys.argv[2]

    with codecs.open(sys.argv[1], "r", "utf-8") as f:
        file_data = f.read()
        parsed_file_data = yaml.safe_load(file_data)

    for component in parsed_file_data['components']:
        if component['component_type'] != 'repository':
            continue

        output_path = os.path.join(output_dir_path, f'{component["name"]}_repo_health.yaml')
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            repo_clone_url = component['url'].replace('https://github.com/', 'git@github.com:')
            subprocess.call(['git', 'clone', '--depth', '1', repo_clone_url, tmp_dir_path])
            run_repo_health(component, tmp_dir_path, output_path)
            for child_component in component.get('children', []):
                cleaned_name = child_component['name'].replace(':', '_').replace('/', '_')
                child_output_path = os.path.join(output_dir_path, f'{cleaned_name}_repo_health.yaml')
                path = os.path.abspath(os.path.join(tmp_dir_path, child_component['path']))
                run_repo_health(child_component, path, child_output_path)


def run_repo_health(component, target_path, output_path):
    print(f'Analyzing {component["component_type"]} {component["name"]}')
    if not os.path.exists(target_path):
        print('Target path does not exist. Skipping.')
        return
    with open(os.path.join(target_path, '.ownership.yaml'), 'wb') as f:
        f.write(yaml.dump(component).encode('utf8'))
    subprocess.call(['pytest', '--repo-health', '--repo-health-path', 'edx-repo-health', '--repo-path', target_path, '--output-path', output_path, '--noconftest', '-v', '-c', '/dev/null'])


if __name__ == "__main__":
    main()
