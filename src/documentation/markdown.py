import os
import yaml

from src.git_client import GitClient
from datetime import datetime

class Markdown:
    def __init__(self, source_file, target_file, source_repo_path):
        """
        Initializes the Markdown object with given source and target files.
        If the target file exists, extracts the Hugo front matter.

        :param source_file: Path to the source file.
        :param target_file: Path to the target file.
        """
        self.source_file = source_file
        self.target_file = target_file
        self.source_repo_path = source_repo_path
        self.content = ''
        self.front_matter = {}

        if os.path.exists(self.target_file):
            self.extract_front_matter()

    def extract_front_matter(self):
        """
        Reads the Hugo front matter from the target file and stores it as a dictionary.
        """
        try:
            with open(self.target_file, 'r', encoding='utf-8') as file:
                content = file.read()

            if content.startswith("---"):
                parts = content.split('---', 2)
                if len(parts) > 1:
                    self.front_matter = yaml.safe_load(parts[1]) or {}

        except Exception as e:
            print(f"Error while extracting front matter: {e}")
            
    def get_content(self):
        return self.content

    def merge_files(self):
        creation_info = GitClient().get_file_creation_info(self.source_file)
        created_at = datetime.strptime(creation_info.get('created_at'), '%Y-%m-%dT%H:%M:%S')

        first_title = None
        comment_started = False
        lines_to_keep = []
        with open(self.source_file, 'r', encoding='utf-8') as file:
            for line in file:
                stripped_line = line.strip()
                if stripped_line.startswith("<!--") and stripped_line.endswith("-->"):
                    continue
                elif stripped_line.startswith("<!--") and not comment_started:
                    comment_started = True
                    continue
                elif stripped_line.endswith("-->") and comment_started:
                    comment_started = False
                    continue
                if comment_started:
                    continue
                if line.startswith("# ") and first_title is None:
                    first_title = line.lstrip("# ").strip()
                    continue
                lines_to_keep.append(line)

        self.content = "\n".join(lines_to_keep)
        data_frontmatter = {
            'date': created_at,
            'title': first_title,
            'params': {
                'author': creation_info.get('author')
            },
        }

        def datetime_representer(dumper, data):
            return dumper.represent_scalar('tag:yaml.org,2002:timestamp', data.isoformat())
        yaml.SafeDumper.add_representer(datetime, datetime_representer)

        front_matter_str = yaml.dump(data_frontmatter, Dumper=yaml.SafeDumper, default_flow_style=False)

        # Merge front matter and content
        self.content = f"---\n{front_matter_str}---\n{self.content}"

