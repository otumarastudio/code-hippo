import os
import argparse
from pathlib import Path
import questionary
from questionary import Style
import emoji

custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

# 기본적으로 제외할 폴더와 파일
DEFAULT_IGNORE = [
    '.git/', '.env', 'env/', 'venv/', 'node_modules/', 
    '__pycache__/', '*.pyc', '*.pyo', '*.pyd',
    '.vscode/', '.idea/', '*.suo', '*.ntvs*', '*.njsproj', '*.sln', '*.sw?',
    '*.log', '*.sqlite', '*.db', '*.bak'
]

def parse_gitignore(gitignore_path):
    ignore_patterns = DEFAULT_IGNORE.copy()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            ignore_patterns.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
    return ignore_patterns

def should_ignore(path, ignore_patterns):
    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            if path_str.startswith(pattern) or path_str.startswith('./' + pattern) or pattern[:-1] in path_str.split(os.sep):
                return True
        elif '*' in pattern:
            if Path(path_str).match(pattern):
                return True
        elif pattern in path_str or ('/' + pattern) in path_str:
            return True
    return False

def generate_folder_structure(root_dir, ignore_patterns, prefix=''):
    folder_structure = ''
    try:
        items = sorted(os.listdir(root_dir))
        for i, item in enumerate(items):
            path = os.path.join(root_dir, item)
            if should_ignore(path, ignore_patterns):
                continue
            if os.path.isdir(path):
                folder_structure += f'{prefix}├── {item}/\n'
                folder_structure += generate_folder_structure(path, ignore_patterns, prefix + '│   ')
            else:
                folder_structure += f'{prefix}├── {item}\n'
    except PermissionError:
        folder_structure += f'{prefix}├── [Permission Denied]\n'
    return folder_structure

def count_files(input_path, ignore_patterns, allowed_extensions):
    count = 0
    for root, dirs, files in os.walk(input_path):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]
        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore(file_path, ignore_patterns):
                continue
            if Path(file).suffix in allowed_extensions:
                count += 1
    return count

def summarize_project(input_path, output_path, ignore_patterns):
    allowed_extensions = {'.py', '.ts', '.js', '.css', '.html'}
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write('# Project Summary\n\n')
        outfile.write('## Folder Structure\n')
        outfile.write('```\n')
        outfile.write(generate_folder_structure(input_path, ignore_patterns))
        outfile.write('```\n\n')
        
        for root, dirs, files in os.walk(input_path):
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]
            for file in sorted(files):
                file_path = os.path.join(root, file)
                if should_ignore(file_path, ignore_patterns):
                    continue
                if Path(file).suffix not in allowed_extensions:
                    continue
                
                rel_path = os.path.relpath(file_path, input_path)
                outfile.write(f'## File: {rel_path}\n')
                outfile.write(f'**Absolute Path:** {file_path}\n\n')
                outfile.write('**Content:**\n')
                outfile.write('```\n')
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f'Error reading file: {str(e)}')
                outfile.write('\n```\n\n')

def main():
    print(emoji.emojize("Welcome to Code Hippo! :hippopotamus: Let's summarize your project."))
    
    while True:
        input_path = questionary.path(
            "Enter the path to your project directory (absolute path preferred):",
            style=custom_style
        ).ask()
        
        input_path = os.path.abspath(input_path)
        
        if not os.path.exists(input_path):
            print(emoji.emojize(":warning: Oops! That path doesn't exist. Let's try again!"))
            continue
        
        if not os.path.isdir(input_path):
            print(emoji.emojize(":confused_face: That's not a directory. We need a folder, not a file!"))
            continue
        
        break
    
    output_path = questionary.path(
        "Enter the path for the output summary file (press Enter to use the input path):",
        default=os.path.join(input_path, "project_summary.md"),
        style=custom_style
    ).ask()
    
    gitignore_path = os.path.join(input_path, '.gitignore')
    ignore_patterns = parse_gitignore(gitignore_path)
    
    allowed_extensions = {'.py', '.ts', '.js', '.css', '.html'}
    
    try:
        file_count = count_files(input_path, ignore_patterns, allowed_extensions)
    except PermissionError:
        print(emoji.emojize(":locked: Uh-oh! We don't have permission to access some folders. We'll skip those."))
        file_count = 0  # 여기서는 0으로 설정하고 계속 진행합니다.
    
    proceed = questionary.confirm(
        f"Found {file_count} files to summarize. Ready to chomp through them? :grinning_face_with_big_eyes:",
        style=custom_style
    ).ask()
    
    if proceed:
        try:
            summarize_project(input_path, output_path, ignore_patterns)
            print(emoji.emojize(f":party_popper: Woohoo! Summary has been saved to {output_path}"))
        except Exception as e:
            print(emoji.emojize(f":disappointed_face: Oh no! Something went wrong: {str(e)}"))
    else:
        print(emoji.emojize("No problem! The hippo's going back to sleep. :sleeping_face: Goodbye!"))

if __name__ == "__main__":
    main()