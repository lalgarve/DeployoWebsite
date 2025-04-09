import re
from pathlib import Path


def calculate_token_cost(log_file_path):
    """
    Calculate the total tokens and estimated cost from a log file, including model version.
    Rule: First 1 million tokens are free, then $0.10 per million tokens.
    """
    log_path = Path(log_file_path)
    if not log_path.exists():
        print(f"Log file '{log_file_path}' not found.")
        return None, None, None

    total_tokens = 0
    model_versions = set()  # Conjunto para rastrear modelos usados
    token_pattern = re.compile(r"Total tokens: (\d+)")
    model_pattern = re.compile(r"with model '([^']+)'")  # Extrai o modelVersion

    with open(log_path, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            token_match = token_pattern.search(line)
            model_match = model_pattern.search(line)
            if token_match:
                tokens = int(token_match.group(1))
                total_tokens += tokens
            if model_match:
                model_versions.add(model_match.group(1))

    free_tokens = 1_000_000
    cost_per_million = 0.10

    if total_tokens <= free_tokens:
        total_cost = 0.0
    else:
        billable_tokens = total_tokens - free_tokens
        total_cost = (billable_tokens / 1_000_000) * cost_per_million

    return total_tokens, total_cost, model_versions


def process_log_files(log_dir_or_file):
    """
    Process a single log file or all log files in a directory and calculate total tokens, cost, and models used.
    """
    log_path = Path(log_dir_or_file)
    total_tokens_all = 0
    total_cost_all = 0.0
    all_model_versions = set()

    if log_path.is_file():
        total_tokens, total_cost, model_versions = calculate_token_cost(log_dir_or_file)
        if total_tokens is not None:
            total_tokens_all += total_tokens
            total_cost_all += total_cost
            all_model_versions.update(model_versions)
            print(f"File: {log_dir_or_file}")
            print(f"Total tokens: {total_tokens:,}")
            print(f"Estimated cost: US$ {total_cost:.4f}")
            print(f"Model versions used: {', '.join(model_versions)}")
    elif log_path.is_dir():
        for log_file in log_path.glob("*.log"):
            total_tokens, total_cost, model_versions = calculate_token_cost(log_file)
            if total_tokens is not None:
                total_tokens_all += total_tokens
                total_cost_all += total_cost
                all_model_versions.update(model_versions)
                print(f"File: {log_file}")
                print(f"Total tokens: {total_tokens:,}")
                print(f"Estimated cost: US$ {total_cost:.4f}")
                print(f"Model versions used: {', '.join(model_versions)}")
        print("\nSummary for all files:")
    else:
        print(f"'{log_dir_or_file}' is neither a file nor a directory.")
        return

    print(f"Total tokens across all files: {total_tokens_all:,}")
    print(f"Total estimated cost: US$ {total_cost_all:.4f}")
    print(f"All model versions used: {', '.join(all_model_versions)}")


if __name__ == "__main__":
    print("Processing a single log file:")
    process_log_files("logs/summary_generator.log")

    print("\nProcessing all log files in a directory:")
    process_log_files("logs")