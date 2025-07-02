import os

def count_lines_in_directory(directory, extension='.py'):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"{file_path}: {len(lines)} lines")
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")

if __name__ == "__main__":
    project_dir = "d:/drzqr/Documents/GitHub/MarkerGUI"
    count_lines_in_directory(project_dir)
