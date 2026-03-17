import os
from pathlib import Path

def tree(directory, prefix='', ignore=['.venv', '__pycache__', '.git']):
    contents = sorted(Path(directory).iterdir(), key=lambda p: (not p.is_dir(), p.name))
    contents = [c for c in contents if c.name not in ignore]

    for i, path in enumerate(contents):
        is_last = i == len(contents) - 1
        current_prefix = '└── ' if is_last else '├── '
        print(prefix + current_prefix + path.name + ('/' if path.is_dir() else ''))

        if path.is_dir():
            next_prefix = prefix + ('    ' if is_last else '│   ')
            tree(path, next_prefix, ignore)

if __name__ == '__main__':
    print('financial-advisor-agent/')
    tree('.', '', ['.venv', '__pycache__', '.git', '.python-version'])
