import subprocess


class GitClient:

    def __init__(self, repository_path="."):
        """
        Initializes the GitClient with the repository path.
        :param repository_path: Path to the git repository (default: current directory).
        """
        self.repository_path = repository_path

    def commit(self, message):
        """
        Executes a git commit with the provided message.
        :param message: The commit message to use.
        """
        try:
            subprocess.run(["git", "commit", "-m", message], check=True, cwd=self.repository_path)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute commit: {e}")

    def add(self, path):
        """
        Executes a git add for the specified path.
        :param path: The file or directory path to add.
        """
        try:
            subprocess.run(["git", "add", path], check=True, cwd=self.repository_path)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute add for path '{path}': {e}")

    def status(self):
        """
        Executes git status and returns its output.
        :return: The output of the git status command as a string.
        """
        try:
            result = subprocess.run(["git", "status"], check=True, text=True, capture_output=True,
                                    cwd=self.repository_path)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute git status: {e}")
            return None

    def file_change_since(self, commit_id_begin, commit_id_end="HEAD"):
        """
        Executes git diff to show file changes between two commits.
        :param commit_id_begin: The starting commit ID.
        :param commit_id_end: The ending commit ID (default: HEAD).
        :return: The output of the git diff command as a string.
        """
        try:
            result = subprocess.run(
                ["git", "diff", f"{commit_id_begin}..{commit_id_end}"],
                check=True, text=True, capture_output=True, cwd=self.repository_path
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute git diff between '{commit_id_begin}' and '{commit_id_end}': {e}")

    def get_file_creation_info(self, file_path, commit_id="--reverse"):
        """
        Retrieves the creation date and author of a file.
        :param file_path: The file for which to retrieve data.
        :param commit_id: The starting commit ID (default: first commit of the file using --reverse).
        :return: A dictionary containing 'creation_date' and 'author'.
        """
        try:
            author_result = subprocess.run(
                ["git", "log", commit_id, "--format=%an", "--", file_path],
                check=True, text=True, capture_output=True, cwd=self.repository_path
            )
            date_result = subprocess.run(
                ["git", "log", commit_id, "--format=%ad", "--date=iso", "--", file_path],
                check=True, text=True, capture_output=True, cwd=self.repository_path
            )
            return {
                "author": author_result.stdout.strip(),
                "creation_date": date_result.stdout.strip()
            }
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve creation info for '{file_path}': {e}")
            return None
