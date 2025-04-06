import os
import sys
from src.utils import camel_to_kebab

class FileHandler:
    def __init__(self, source_repo_path, destination_repo_path, update_all_fields=False):
        self.source_repo_path = source_repo_path
        self.destination_repo_path = destination_repo_path
        self.update_all_fields = update_all_fields

def should_traverse_directory(directory_name):
    """
    Determines if a directory should be traversed.
    Excludes directories named 'uml' and 'backlog'.

    :param directory_name: Name of the directory to check.
    :return: True if the directory should be traversed, False otherwise.
    """
    return directory_name not in {'uml', 'backlog'}


def determine_file_actions(file_path):
    """
    Determines which actions to perform based on file type and location.

    :param file_path: Full path of the file to process.
    :return: List of actions to perform.
    """
    actions = []
    if file_path.endswith('.png'):
        actions.append('handle_png')
    if file_path.endswith('.md'):
        actions.append('handle_markdown')
        if '/blog/' in file_path or file_path.startswith('blog/'):
            actions.append('handle_markdown_in_blog')
    return actions


def handle_png(source_file_path, destination_file_path):
    """
    Copies a PNG file from the source path to the destination path.
    
    :param source_file_path: Path to the source PNG file.
    :param destination_file_path: Path to the destination PNG file.
    """
    try:
        with open(source_file_path, 'rb') as src_file:
            with open(destination_file_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
    except FileNotFoundError:
        print(f"File not found: {source_file_path}", file=sys.stderr)
    except IOError as e:
        print(f"Error copying PNG file from '{source_file_path}' to '{destination_file_path}': {e}", file=sys.stderr)


def build_destination_path(self, source_path):
    """
    Build the destination path based on the source path and the defined rules.

    :param self: Instance of the class.
    :param source_path: Source file or directory path.
    :return: Destination path based on the rules.
    """
    source_repo_name = os.path.basename(self.source_repo_path.rstrip('/'))
    kebab_source_repo_name = camel_to_kebab(source_repo_name)
    relative_source_path = os.path.relpath(source_path, self.source_repo_path)

    # Base of the destination path
    destination_base = os.path.join(self.destination_repo_path, "content")

    # Determine if there is a language in the path
    path_parts = relative_source_path.split(os.sep)
    if len(path_parts) > 1 and path_parts[0] == 'docs' and path_parts[1] in ['en', 'pt-br']:  # Supported languages
        language = path_parts[1]
        relative_language_path = os.sep.join(path_parts[2:])
        language_destination = os.path.join(destination_base, language)

        if relative_language_path.startswith('articles'):
            blog_path = relative_language_path.replace('articles', 'blog', 1)
            if os.path.isfile(source_path):
                pathname, filename = os.path.split(blog_path)
                name, ext = os.path.splitext(filename)
                new_filename = f"{kebab_source_repo_name}-{camel_to_kebab(name)}{ext}"
                return os.path.join(language_destination, pathname, new_filename)
            else:
                return os.path.join(language_destination, blog_path)

        elif os.path.isfile(source_path):
            pathname, filename = os.path.split(relative_language_path)
            name, ext = os.path.splitext(filename)
            new_filename = f"{camel_to_kebab(name)}{ext}"
            return os.path.join(language_destination, 'docs', kebab_source_repo_name, pathname, new_filename)
        else:
            return os.path.join(language_destination, 'docs', kebab_source_repo_name, relative_language_path)

    return destination_base
    