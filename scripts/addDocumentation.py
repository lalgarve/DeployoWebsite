#!/usr/bin/env python3
         
#!/usr/bin/env python3

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
addDocumentation.py - A script to process documentation files from a source repository and 
populate them with metadata from Git.

This script performs the following tasks:
- Traverses a source repository directory recursively.
- Identifies `.png` and `.md` files to process.
- Copies `.png` files to the destination directory.
- Processes `.md` files by extracting Git metadata and adding it as YAML front matter.
- Ignores `uml` directories and unsupported file formats.

Usage:
    addDocumentation.py <source_repo_path> <destination_path>

Arguments:
    source_repo_path (str): Path to the source Git repository containing the documentation files.
    destination_path (str): Path to the destination directory where processed files will be saved.

Functions:
    - verify_usage: Ensures correct script usage with proper arguments.
    - process_files: Recursively processes a source directory to copy/process files.
    - copy_file: Copies `.png` files from source to destination.
    - process_file: Processes `.md` files by adding Git metadata as YAML front matter.
    - extract_title_from_markdown: Extracts the title from the first H1 header in an `.md` file.
    - get_git_file_info: Retrieves Git author, creation date, and last modified date for a file.

Examples:
    python addDocumentation.py /path/to/source/repo /path/to/destination

Dependencies:
    - Python 3.x is required.
    - The script uses the `os`, `sys`, `subprocess`, and `datetime` modules.

"""
         import sys
         import os
         import subprocess
         from datetime import datetime

         def verify_usage():
             if len(sys.argv) != 3:
                 print("Usage: addDocumentation.py <source_repo_path> <destination_path>", file=sys.stderr)
                 sys.exit(1)

         def process_files(source, destination, source_repo_path):
             if not os.path.exists(destination):
                 try:
                     os.makedirs(destination)
                 except OSError as e:
                     print(f"Error creating directory '{destination}': {e}", file=sys.stderr)
                     sys.exit(1)

             if os.path.isdir(source):
                 for item in os.listdir(source):
                     source_item = os.path.join(source, item)
                     destination_item = os.path.join(destination, item)
                     if os.path.isdir(source_item) and item != 'uml':
                         process_files(source_item, destination_item, source_repo_path)
                     else:
                         filename, extension = os.path.splitext(item)
                         if extension == '.png':
                             copy_file(source_item, destination_item)
                         elif extension == '.md':
                             process_file(source_item, destination_item, source_repo_path)
                         else:
                             print(f"Ignoring unsupported file: {source_item}", file=sys.stderr)

         def copy_file(source_item, destination_item):
             try:
                 with open(source_item, 'rb') as src_file:
                     with open(destination_item, 'wb') as dest_file:
                         dest_file.write(src_file.read())
             except FileNotFoundError:
                 print(f"File not found: {source_item}", file=sys.stderr)
             except IOError as e:
                 print(f"Error copying file from '{source_item}' to '{destination_item}': {e}", file=sys.stderr)

         def process_file(source_item, destination_item, source_repo_path):
             translations = {
                 "pt-br": {
                     "unknown_author": "Desconhecido",
                     "no_title": "Sem título"
                 },
                 "en": {
                     "unknown_author": "Unknown",
                     "no_title": "No title"
                 }
             }

             language = "en"
             if "pt-br" in source_item.lower():
                 language = "pt-br"
             elif "en" in source_item.lower():
                 language = "en"

             title = extract_title_from_markdown(source_item) or translations[language]["no_title"]

             front_matter = {
                 "title": title,
                 "date_created": None,
                 "last_modified": None,
                 "author": None
             }

             git_info = get_git_file_info(source_item, source_repo_path)
             if git_info:
                 front_matter["date_created"] = git_info["creation_date"].isoformat() if git_info["creation_date"] else None
                 front_matter["last_modified"] = git_info["last_modification_date"].isoformat() if git_info["last_modification_date"] else None
                 front_matter["author"] = git_info["author"] or translations[language]["unknown_author"]

             try:
                 with open(source_item, 'r', encoding='utf-8') as src:
                     content = src.read()
                 with open(destination_item, 'w', encoding='utf-8') as dest:
                     dest.write("---\n")
                     for key, value in front_matter.items():
                         dest.write(f"{key}: {value if value is not None else ''}\n")
                     dest.write("---\n\n")
                     dest.write(content)
             except FileNotFoundError:
                 print(f"File not found: {destination_item}", file=sys.stderr)
             except IOError as e:
                 print(f"Error processing file '{destination_item}': {e}", file=sys.stderr)

         def extract_title_from_markdown(source_item):
             try:
                 with open(source_item, 'r', encoding='utf-8') as source_file:
                     for line in source_file:
                         if line.startswith("# "):
                             return line[2:].strip()
             except FileNotFoundError:
                 print(f"File not found: {source_item}", file=sys.stderr)
             except IOError as e:
                 print(f"Error processing file '{source_item}': {e}", file=sys.stderr)
             return None

         def get_git_file_info(file_path, source_repo_path):
             """
             Extracts the Git metadata (author, creation date, last modification date) for a given file.

             :param file_path: Path to the file for which metadata is to be extracted.
             :param source_repo_path: Path to the source Git repository.
             :return: A dictionary with author, creation_date, and last_modification_date.
             """
             repo_path = source_repo_path

             def run_git_command(command, repo_path):
                 try:
                     output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True, cwd=repo_path)
                     return output.strip()
                 except subprocess.CalledProcessError as e:
                     print(f"Git command failed: {e}", file=sys.stderr)
                     return None

             author = run_git_command(["git", "log", "-n", "1", "--format=%an", file_path], repo_path)
             creation_date_str = run_git_command(["git", "log", "--reverse", "--format=%ad", "--date=iso8601", file_path, "--", file_path], repo_path)
             last_modification_date_str = run_git_command(["git", "log", "-n", "1", "--format=%ad", "--date=iso8601", file_path], repo_path)

             creation_date = datetime.fromisoformat(creation_date_str) if creation_date_str else None
             last_modification_date = datetime.fromisoformat(last_modification_date_str) if last_modification_date_str else None

             return {
                 "author": author,
                 "creation_date": creation_date,
                 "last_modification_date": last_modification_date
             }

         if __name__ == "__main__":
             if len(sys.argv) != 3:
                 verify_usage()
             else:
                 source_repo_path = sys.argv[1]
                 destination_path = sys.argv[2]
                 source = os.path.join(source_repo_path, "docs")
                 process_files(source, destination_path, source_repo_path)