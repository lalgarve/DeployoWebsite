import re
from pathlib import Path
import pytest
from src.documentation.markdown import Markdown


@pytest.fixture
def markdown_files():
    base_dir = Path(__file__).parent / 'resources' / 'markdown'
    return {
        'source_file_correct': base_dir / 'source-correct.md',
        'target_file_not_existing': base_dir / 'target-correct-not-existing.md'
    }

def test_merge_files_source_only_git(markdown_files, mocker):
    """
    Test when the source file exists and the target file does not exist.
    """
    # Arrange
    mock_get_file_creation_info = mocker.patch(
        'src.git_client.GitClient.get_file_creation_info',
        return_value={'created_at': '2023-11-02T10:00:00', 'author': 'user1'}
    )

    mock_generate_summary = mocker.patch(
        'scr.documentation.generate_ai_content.generate_ai_content',
        return_value="""Summaries:
    pt-br: O Resume Builder System utiliza Spring Boot e AWS Lambda para criar e gerenciar currículos eficientemente, otimizando custos. A arquitetura inclui camadas de modelos, serviços, controladores, repositórios e utilitários, com integração AWS via S3 e Lambda, promovendo modularidade e escalabilidade.
    en: The Resume Builder System uses Spring Boot and AWS Lambda for efficient resume creation and management, optimizing costs. It features layered models, services, controllers, repositories, and utilities, with AWS integration via S3 and Lambda, ensuring modularity and scalability."""
    )

    markdown = Markdown(markdown_files['source_file_correct'], markdown_files['target_file_not_existing'], '.')

    # Act
    markdown.merge_files()
    merged_content = markdown.get_content()

    # Assert
    front_matter_match = re.match(r'^---\n(.*?)\n---\n', merged_content, re.DOTALL)
    assert front_matter_match is not None, "Front matter is missing in the merged content"
    front_matter = front_matter_match.group(1)
    content_body = re.sub(r'^---\n.*?\n---\n', '', merged_content, flags=re.DOTALL)

    assert "date: 2023-11-02T10:00:00" in front_matter, "Date in front matter is incorrect"
    assert "author: user1" in front_matter, "Author in front matter is incorrect"
    assert "title: Title 1" in front_matter, "Title in front matter is incorrect"
    assert not re.search(r'^# Title 1', content_body), "Title should not be present in the content section"
    assert "<!-- One liner -->" not in content_body, "One-line comment should not be present in the content section"

    mock_get_file_creation_info.assert_called_once_with(markdown_files['source_file_correct'])