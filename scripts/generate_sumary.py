import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from google import genai
from google.genai import types


def setup_logging(log_file_base_path):
    """Configura o logging com rotação mensal no caminho especificado."""
    log_dir = os.path.dirname(log_file_base_path)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    log_handler = TimedRotatingFileHandler(
        filename=log_file_base_path,
        when='M',
        interval=1,
        backupCount=12,
        utc=True
    )
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    log_handler.suffix = "%Y-%m"

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            log_handler,
            logging.StreamHandler()
        ]
    )


def extract_markdown_title(markdown_text):
    """Extracts the first level-1 title from the Markdown text."""
    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            return line.lstrip('# ').strip()
    return "Untitled"


def generate_summary(markdown_text, model_version="gemini-2.0-flash", log_file_base_path=None):
    """Generate summaries for the given Markdown text in pt-br and en, returning a dict with summaries and token count."""
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
            types.Part.from_text(text="""For each provided Markdown text, generate a summary in Portuguese (pt-br) and English (en), each 40-60 words, without titles like 'Sumário' or 'Summary'. Return the result as plain text with 'pt-br:' followed by the Portuguese summary, then 'en:' followed by the English summary, separated by a newline."""),
        ],
    )

    full_response = ""
    total_tokens = 0

    for chunk in client.models.generate_content_stream(
        model=model_version,
        contents=contents,
        config=generate_content_config,
    ):
        full_response += chunk.text
        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
            total_tokens += chunk.usage_metadata.total_token_count or 0

    result_dict = {"summaries": {}, "total_tokens": total_tokens}
    lines = full_response.strip().split('\n')
    for line in lines:
        if line.startswith("pt-br:"):
            result_dict["summaries"]["pt-br"] = line[len("pt-br:"):].strip()
        elif line.startswith("en:"):
            result_dict["summaries"]["en"] = line[len("en:"):].strip()

    if total_tokens == 0 and hasattr(chunk, 'usage_metadata'):
        total_tokens = chunk.usage_metadata.total_token_count or 0
    result_dict["total_tokens"] = total_tokens

    logger.info(f"Completed {method_name} for '{markdown_title}' with model '{model_version}' - Total tokens: {total_tokens}")

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
... (resto do Markdown omitido para brevidade)"""

    result = generate_summary(markdown_input, model_version="gemini-2.0-flash", log_file_base_path='logs/summary_generator.log')
    print("Summaries:")
    for lang, summary in result["summaries"].items():
        print(f"{lang}: {summary}")
    print(f"Total tokens: {result['total_tokens']}")