import re
from pathlib import Path


def calculate_token_cost(log_file_path):
    """
    Calculate the total tokens and estimated cost from a log file, including model version.
    There are NO free tokens allocated for any model. Costs are calculated per million tokens.
    Supported models and costs per million tokens:
    - gemini-2.0-flash: $0.10 (input), $0.40 (output)
    - gemini-2.0-flash-lite: $0.075 (input), $0.30 (output)
    - gemini-1.5-flash: $0.075 (input), $0.30 (output)
    - gemini-1.5-flash-8b: $0.0375 (input), $0.15 (output)
    """
    log_path = Path(log_file_path)
    if not log_path.exists():
        print(f"Log file '{log_file_path}' not found.")
        return None, None, None

    # ## Preços por um milhão de tokens
    token_costs = {
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40, "input_tokens":0, "output_tokens":0, "cost":0.0},
        "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30, "input_tokens":0, "output_tokens":0, "cost":0.0},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30, "input_tokens":0, "output_tokens":0, "cost":0.0},
        "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15, "input_tokens":0, "output_tokens":0, "cost":0.0}
    }
    #
    # 2025-04-11 00:15:53,510 - INFO - Completed generate_summary for 'Resume Builder System - Documentação da Arquitetura' with model 'gemini-2.0-flash' - Input tokens: 9830 Output tokens: 228 Total tokens: 10058

    token_pattern = re.compile(r"Input tokens: (\d+) Output tokens: (\d+)")
    model_pattern = re.compile(r"with model '([^']+)'")  # Extrai o modelVersion

    with open(log_path, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            token_match = token_pattern.search(line)
            model_match = model_pattern.search(line)
            if token_match and model_match:
                input_tokens = int(token_match.group(1))
                output_tokens = int(token_match.group(2))
                model = model_match.group(1)

                if model in token_costs:
                    token_costs[model]["input_tokens"] += input_tokens
                    token_costs[model]["output_tokens"] += output_tokens
                    cost_input = (input_tokens / 1_000_000) * token_costs[model]["input"]
                    cost_output = (output_tokens / 1_000_000) * token_costs[model]["output"]
                    token_costs[model]["cost"] += cost_input + cost_output


    return token_costs


def process_log_files(log_dir_or_file):
    """
    Process a single log file or all log files in a directory and calculate total tokens, cost, and models used.
    """
    log_path = Path(log_dir_or_file)
    total_tokens_all = 0
    total_cost_all = 0
    all_model_versions = set()

    if log_path.is_file():
        process_log_file(log_dir_or_file)
    elif log_path.is_dir():
        for log_file in log_path.glob("*.log*"):
            total_tokens, total_cost, model_versions = process_log_file(log_file)
            if total_tokens is not None:
                total_tokens_all += total_tokens
                total_cost_all += total_cost
                all_model_versions.update(model_versions)
        print("\nSummary for all files:")
    else:
        print(f"'{log_dir_or_file}' is neither a file nor a directory.")
        return

    print(f"Total tokens across all files: {total_tokens_all:,}")
    print(f"Total estimated cost: US$ {total_cost_all:.4f}")
    print(f"All model versions used: {', '.join(all_model_versions)}")


def process_log_file(file):
    token_costs = calculate_token_cost(file)
    total_tokens = 0
    total_cost = 0.0
    model_versions = set()
    if token_costs is not None:
        print(f"File: {file}")
        for model in token_costs:
            if token_costs[model]["cost"] > 0:
                model_versions.add(model)
                total_tokens += token_costs[model]["input_tokens"]
                total_tokens += token_costs[model]["output_tokens"]
                token_costs[model]["cost"] += token_costs[model]["cost"]
                total_cost += token_costs[model]["cost"]
        print(f"Total tokens: {total_tokens:,}")
        print(f"Estimated cost: US$ {total_cost:.4f}")
        print(f"Model versions used: {', '.join(model_versions)}\n")

    return total_tokens, total_cost, model_versions


if __name__ == "__main__":
    # print("Processing a single log file:")
    # process_log_files("logs/summary_generator.log")

    print("\nProcessing all log files in a directory:")
    process_log_files("logs")