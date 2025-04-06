
import pytest
import os

from ..documentation.file_handler import FileHandler, build_destination_path
from ..utils import camel_to_kebab


@pytest.fixture(params=[
    {'language': 'en', 'name-style': 'kebab-case'},
    {'language': 'en', 'name-style': 'camelCase'},
    {'language': 'pt-br', 'name-style': 'kebab-case'},
    {'language': 'pt-br', 'name-style': 'camelCase'}
])
def temp_repos(tmp_path, request):
    language = request.param['language']
    name_style = request.param['name-style']

    file_name = {
        'en': {
            'kebab-case': {
            'doc': 'my-file.md',
            'article': 'my-article.md',
            'image': 'my-image.png'
            },
            'camelCase': {
                'doc': 'MyFile.md',
                'article': 'MyArticle.md',
                'image': 'MyImage.png'
            }
        },
        'pt-br': {
            'kebab-case': {
                'doc': 'my-file.md',
                'article': 'my-article.md',
                'image': 'my-image.png'
            },
            'camelCase': {
                'doc': 'MyFile.md',
                'article': 'MyArticle.md',
                'image': 'MyImage.png'
            }
        }
    }[language][name_style]

    """Creates temporary source and destination repositories."""
    source_repo = tmp_path / 'MySourceRepository'
    dest_repo = tmp_path / 'MyDestinationRepository'

    # Create source structure
    source_docs = source_repo / 'docs' / language
    source_articles = source_docs / 'articles'
    source_images = source_docs / 'images'

    source_docs.mkdir(parents=True)
    source_articles.mkdir()
    source_images.mkdir()

    # Create files in the source
    (source_docs / file_name['doc']).touch()
    (source_articles / file_name['article']).touch()
    (source_images / file_name['image']).touch()

    # Create minimal destination structure
    dest_repo.mkdir()

    return source_repo, dest_repo, language, file_name['doc'], file_name['article'], file_name['image']

@pytest.fixture
def file_handler(temp_repos):
    """Creates an instance of FileHandler with the temporary repositories."""
    source_repo, dest_repo, _ , _, _, _= temp_repos
    return FileHandler(str(source_repo), str(dest_repo))

def test_build_destination_path_documentation(file_handler, temp_repos):
    """Tests if the correct destination path is built for a documentation directory."""
    source_repo, dest_repo, language, _, _, _ = temp_repos
    source_path = source_repo / 'docs' / language
    expectation = dest_repo / 'content' / language / 'docs' / 'my-source-repository'
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

def test_build_destination_path_article(file_handler, temp_repos):
    """Tests if the correct destination path is built for  articles directory."""
    source_repo, dest_repo, language, _, _, _  = temp_repos
    source_path = source_repo / 'docs' / language / 'articles'
    expectation = dest_repo / 'content' / language / 'blog'
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

def test_build_destination_path_documentation_file(file_handler, temp_repos):
    """Tests if the correct destination path is built for a documentation file."""
    source_repo, dest_repo, language, doc_file, _, _ = temp_repos
    source_path = source_repo / 'docs' / language / doc_file
    doc_filename = camel_to_kebab(doc_file)
    expectation = dest_repo / 'content' / language / 'docs' / 'my-source-repository' / doc_filename
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

def test_build_destination_path_article_file(file_handler, temp_repos):
    """Tests if the correct destination path is built for an article file."""
    source_repo, dest_repo, language, _, article_file, _ = temp_repos
    source_path = source_repo / 'docs' / language / 'articles' / article_file
    article_filename = 'my-source-repository-'+camel_to_kebab(article_file)
    expectation = dest_repo / 'content' / language / 'blog' / article_filename
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

def test_build_destination_path_images(file_handler, temp_repos):
    """Tests if the correct destination path is built for images directory."""
    source_repo, dest_repo, language, _, _, image_file = temp_repos
    source_path = source_repo / 'docs' / language / 'images'
    expectation = dest_repo / 'content' / language / 'docs' / 'my-source-repository' /  'images'
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

def test_build_destination_path_images_file(file_handler, temp_repos):
    """Tests if the correct destination path is built for an image file."""
    source_repo, dest_repo, language, _, _, image_file = temp_repos
    source_path = source_repo / 'docs' / language / 'images' / image_file
    image_filename = camel_to_kebab(image_file)
    expectation = dest_repo / 'content' / language / 'docs' / 'my-source-repository' / 'images' / image_filename
    result = build_destination_path(file_handler, str(source_path))
    assert os.path.normpath(result) == os.path.normpath(expectation)

