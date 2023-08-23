import os
import re
import subprocess
import sys

def get_imports_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    imports = re.findall(r'import (\w+(?:\.\w+)*?)|from (\w+(?:\.\w+)*) import', content)

    # Additional check for specific pattern usage related to model_name
    model_names = re.findall(r'model_name="([\w\-]+?)[/"]', content)
    imports.extend([(model_name,) for model_name in model_names])

    return [imp[0] or imp[1] for imp in imports]

def is_std_lib(package):
    try:
        __import__(package)
        if package in sys.builtin_module_names:
            return True
        else:
            file_location = __import__(package).__file__
            if 'dist-packages' in file_location or 'site-packages' in file_location:
                return False
            return True
    except:
        pass
    return False

def is_custom_script(package, root_dir):
    parts = package.split('.')
    script_name = parts[0]
    potential_paths = [
        os.path.join(root_dir, script_name, '__init__.py'),
        os.path.join(root_dir, script_name + '.py')
    ]
    return any(os.path.exists(path) for path in potential_paths)

def get_package_version(package):
    try:
        result = subprocess.run(['pip', 'show', package], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('Version:'):
                return line.split(' ')[-1]
    except:
        return None

MAPPING = {
    'load_dotenv': 'python-dotenv',
    'deeplake': 'deeplake',
    'langchain': 'langchain',
    'dotenv': 'python-dotenv'
}

def resolve_to_base_package(imp):
    if imp in MAPPING:
        return MAPPING[imp]
    parts = imp.split('.')
    return parts[0]

def main():
    root_dir = '.'
    packages = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                imports = get_imports_from_file(file_path)
                if imports:
                    print(f"\nFile: {file_path}")
                    print(f"Imports: {', '.join(imports)}")

                    for imp in imports:
                        base_package = resolve_to_base_package(imp)
                        if is_custom_script(base_package, root_dir):
                            print(f"  {imp} -> Custom script/package")
                        elif is_std_lib(base_package):
                            print(f"  {imp} -> Standard Library")
                        elif base_package in MAPPING:
                            print(f"  {imp} -> Mapped to '{MAPPING[base_package]}'")
                        else:
                            print(f"  {imp} -> Resolves to base package '{base_package}'")

                packages.update(imports)

    packages = {resolve_to_base_package(package) for package in packages}

    for package in packages:
        if not is_std_lib(package) and not is_custom_script(package, root_dir):
            version = get_package_version(package)
            if version:
                result = subprocess.run(['poetry', 'add', f"{package}@{version}"], capture_output=True, text=True)
                print(result.stdout)
                print(result.stderr)

if __name__ == "__main__":
    main()
