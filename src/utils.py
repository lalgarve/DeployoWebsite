import re

def camel_to_kebab(name):
    """
    Converts a camelCase name to kebab-case.
    Example: 'MeuArquivoTeste' -> 'meu-arquivo-teste'
    """
    # Adds a hyphen before uppercase letters followed by lowercase letters or numbers
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
    # Adds a hyphen before uppercase letters followed by other uppercase and lowercase letters
    name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1-\2', name)
    # Converts everything to lowercase
    return name.lower()
