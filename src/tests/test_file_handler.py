import unittest

from src.documentation import file_handler
from ..documentation.file_handler import FileHandler, should_traverse_directory, determine_file_actions, build_destination_path


class TestFileHandlerFunctions(unittest.TestCase):
    # Tests for the function should_traverse_directory
    def test_should_traverse_directory_valid(self):
        """Tests if the directories should be traversed."""
        self.assertTrue(should_traverse_directory('my-directory'))
        self.assertTrue(should_traverse_directory('documents'))
        self.assertTrue(should_traverse_directory('project'))

    def test_should_traverse_directory_excluded(self):
        """Tests if the directories 'uml' and 'backlog' should not be traversed."""
        self.assertFalse(should_traverse_directory('uml'))
        self.assertFalse(should_traverse_directory('backlog'))

    # Tests for the function determine_file_actions
    def test_determine_file_actions_png(self):
        """Tests if the correct action is returned for .png files."""
        self.assertEqual(determine_file_actions('images/photo.png'), ['handle_png'])

    def test_determine_file_actions_markdown(self):
        """Tests if the correct action is returned for .md files."""
        self.assertEqual(determine_file_actions('docs/file.md'), ['handle_markdown'])

    def test_determine_file_actions_markdown_in_blog(self):
        """Tests if the correct actions are returned for .md files in the /blog directory."""
        self.assertEqual(determine_file_actions('/blog/file.md'), ['handle_markdown', 'handle_markdown_in_blog'])
        self.assertEqual(determine_file_actions('blog/file.md'), ['handle_markdown', 'handle_markdown_in_blog'])

    def test_determine_file_actions_no_match(self):
        """Tests if no actions are returned for files with unsupported file patterns."""
        self.assertEqual(determine_file_actions('notes.txt'), [])


if __name__ == '__main__':
    unittest.main()
