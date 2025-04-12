import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from google import genai
from google.genai import types

_log_configured = False;

def setup_logging(log_file_base_path):
    global _log_configured

    if _log_configured:
        return
    """Configura o logging com rotação mensal no caminho especificado."""
    # Criação do diretório, caso não exista
    log_dir = os.path.dirname(log_file_base_path)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    print (f"Log file base path: {log_file_base_path}")
    # Configuração do handler de rotação
    log_handler = TimedRotatingFileHandler(
        filename=log_file_base_path,
        when='M',  # Rotação mensal
        interval=1,
        backupCount=12,  # Manter os últimos 12 meses de logs
        utc=True  # Garantir que o UTC seja usado
    )
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    log_handler.suffix = "%Y-%m"  # Extensão do arquivo de rotação

    # Configurar logger root manualmente
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Evitar duplicação de handlers
    if not logger.hasHandlers():
        print("Setting up logging...")
        logger.addHandler(log_handler)



def extract_markdown_title(markdown_text):
    """Extracts the first level-1 title from the Markdown text."""
    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            return line.lstrip('# ').strip()
    return "Untitled"


def generate_ai_content(markdown_text, model_version="gemini-2.0-flash", log_file_base_path=None):
    """
    Generates summarized content and page descriptions in both Portuguese (pt-br) and English (en) based on the provided Markdown text.
    
    Parameters:
        markdown_text (str): The Markdown input text to process.
        model_version (str): The version of the AI model to use (default is "gemini-2.0-flash").
        log_file_base_path (str or None): The file path for logging. If not provided, defaults to the "LOG_FILE_PATH" environment variable 
                                          or "summary_generator.log".
    
    Returns:
        dict: A dictionary containing:
            - "summaries" (dict): Summaries in pt-br and en.
            - "descriptions" (dict): Page descriptions in pt-br and en.
            - "total_tokens" (int): The total number of tokens consumed during processing.
    """
    log_file_base_path = log_file_base_path or os.environ.get("LOG_FILE_PATH", "summary_generator.log")
    setup_logging(log_file_base_path)
    logger = logging.getLogger(__name__)

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    method_name = "generate_summary"
    markdown_title = extract_markdown_title(markdown_text)
    logger.info(f"Starting {method_name} for Markdown titled '{markdown_title}' with model '{model_version}'")

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=markdown_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""For each provided Markdown text:
    - write "summaries" and skip a line
    - generate a summary in Portuguese (pt-br) and English (en), each 40-60 words, without titles like 'Sumário' or 'Summary'. Return the result as plain text with 'pt-br:' followed by the Portuguese summary, then 'en:' followed by the English summary, separated by a newline.
    - write "descriptions" and skip a line
    - generate a page description in Portuguese (pt-br) and English (en), each about 20 words, without titles like 'Descrição' or 'Description'. Return the result as plain text with 'pt-br:' followed by the Portuguese page description, then 'en:' followed by the English page description, separated by a newline."""),
        ],
    )

    full_response = ""
    total_tokens = 0
    input_tokens = 0
    output_tokens = 0

    for chunk in client.models.generate_content_stream(
        model=model_version,
        contents=contents,
        config=generate_content_config,
    ):
        full_response += chunk.text
        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
            input_tokens += chunk.usage_metadata.prompt_token_count or 0
            output_tokens += chunk.usage_metadata.candidates_token_count or 0
            total_tokens += chunk.usage_metadata.total_token_count or 0
    print (full_response)
    result_dict = {"summaries": {}, "tokens": {}}
    lines = full_response.strip().split('\n')
    step = 1
    for line in lines:
        if line.startswith("pt-br:") and step==1:
            result_dict["summaries"]["pt-br"] = line[len("pt-br:"):].strip()
            step = 2
        elif line.startswith("en:") and step==2:
            result_dict["summaries"]["en"] = line[len("en:"):].strip()
            step = 3
        elif line.startswith("pt-br:") and step==3:
            result_dict.setdefault("descriptions", {})["pt-br"] = line[len("pt-br:"):].strip()
        elif line.startswith("en:"):
            result_dict.setdefault("descriptions", {})["en"] = line[len("en:"):].strip()

    if total_tokens == 0 and hasattr(chunk, 'usage_metadata'):
        total_tokens = chunk.usage_metadata.total_token_count or 0
        input_tokens = chunk.usage_metadata.prompt_token_count or 0
        output_tokens = chunk.usage_metadata.candidates_token_count or 0
    result_dict["tokens"]["input_tokens"] = input_tokens
    result_dict["tokens"]["output_tokens"] = output_tokens
    result_dict["tokens"]["total_tokens"] = total_tokens

    logger.info(f"Completed {method_name} for '{markdown_title}' with model '{model_version}' - Input tokens: {input_tokens} Output tokens: {output_tokens} Total tokens: {total_tokens}")

    return result_dict


if __name__ == "__main__":
    markdown_input = """<!----------------------------------------------------------------------- 
	This is part of the documentation of Deployo.io Resume Builder System.
	Copyright (C) 2025
	Leila Otto Algarve
	Licensed under the GNU Free Documentation License v1.3 or later.
    See LICENSE-DOCUMENTATION for details. 
------------------------------------------------------------------------>
# Resume Builder System - Documentação da Arquitetura

O **Resume Builder System** é um sistema projetado para criar e gerenciar currículos de forma eficiente, utilizando uma arquitetura baseada em Spring Boot e AWS Lambda para otimizar custos em cenários de baixa demanda inicial. A estrutura é organizada em pacotes que separam responsabilidades claras, promovendo modularidade e escalabilidade.

## Explicação da Arquitetura

### Models
No topo da arquitetura, os modelos definem as entidades principais:
- **User**: Representa os usuários, que podem ser anônimos (com `trialCode` no formato `dddd-dddd-dddd-dddd` e validade de 7 dias) ou autenticados via OAuth (LinkedIn ou Google, sem login/senha tradicional).
- **Resume**: Armazena informações do currículo, incluindo dados brutos (`rawData`), dados parseados (`parsedData`), modelo escolhido (`templateId`), estilos personalizados (`styles`), URL do PDF gerado (`pdfUrl`) e metadados como data de criação.
- **Template**: Define modelos LaTeX pré-configurados, com campos personalizáveis (ex.: paleta de cores, fontes).

### Services
A camada de serviços contém a lógica de negócio:
- **AnonymousAuthService**: Gera e valida códigos de teste para contas anônimas, garantindo acesso temporário de 7 dias.
- **OAuthService**: Integra autenticação com LinkedIn e Google, eliminando a necessidade de credenciais tradicionais.
- **ResumeService**: Gerencia o fluxo completo do currículo: upload (PDF, Word ou texto), parsing, edição manual, geração de preview e download em PDF com armazenamento temporário de 3 dias.
- **TemplateService**: Administra os modelos LaTeX, permitindo listar opções, aplicar templates e customizar estilos.

### Controllers
Os controladores fornecem os pontos de entrada da API:
- **AuthController**: Lida com autenticação anônima e OAuth, delegando a lógica aos serviços correspondentes.
- **ResumeController**: Expõe endpoints para operações de currículo, como upload, edição e geração de PDFs.

### Repositories
Interfaces de persistência para `User`, `Resume` e `Template`, provavelmente implementadas com um banco serverless como DynamoDB para alinhar com a arquitetura AWS Lambda.

### Utils
Ferramentas de suporte:
- **DocumentParser**: Extrai dados de arquivos enviados (PDF, Word ou texto).
- **LatexRenderer**: Converte dados em PDFs usando templates LaTeX.
- **FileStorage**: Abstrai o armazenamento de arquivos, com upload, geração de URLs e exclusão automática após 3 dias.

### Configuration
Configurações do sistema:
- **SpringBootApplication**: Ponto de entrada do Spring Boot.
- **AWSLambdaConfig**: Configurações específicas para execução no AWS Lambda.

### AWS Integration
Integração com serviços AWS:
- **S3Storage**: Armazena PDFs temporariamente (3 dias) e fornece URLs pré-assinadas, conectado ao `FileStorage`.
- **LambdaHandler**: Adaptador para integrar o Spring Boot com o AWS Lambda.

### Relacionamentos
- Um `User` possui um `Resume` principal, usado para gerar os outros(1:1).
- Um `User` pode ter vários `SpecificResume` (1:N), um para cada vaga de emprego específica.
- Cada `SpecificResume`Resume` está associado a um único `Template` (1:1).
- Os serviços interagem com os repositórios e os utilitários conforme necessário, enquanto o `ResumeService` coordena o fluxo principal do sistema.

Essa estrutura foi projetada para ser leve e econômica, aproveitando a escalabilidade automática do AWS Lambda e o armazenamento temporário no S3, com foco em simplicidade e funcionalidade.ddd 

## Diagrama da Arquitetura

![Diagrama da Arquitetura](images/Architecture.png)
"""

    result = generate_ai_content(markdown_input, model_version="gemini-2.0-flash", log_file_base_path='logs/ai_token_accounting.log')
    print("Summaries:")
    for lang, summary in result["summaries"].items():
        print(f"{lang}: {summary}")
    print("Descriptions:")
    for lang, description in result["descriptions"].items():
        print(f"{lang}: {description}")
    print(f"Input tokens: {result['tokens']['input_tokens']}")
    print(f"Output tokens: {result['tokens']['output_tokens']}")
    print(f"Total tokens: {result['tokens']['total_tokens']}")