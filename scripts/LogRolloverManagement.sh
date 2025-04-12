#!/bin/bash

# Carrega as variáveis de ambiente do arquivo .env
if [ -f ".env" ]; then
  source .env
  echo "Variáveis de ambiente carregadas do arquivo .env"
else
  echo "Arquivo .env não encontrado."
  exit 1
fi

# Define o nome do arquivo de log
LOG_FILE="$PROJECT_ROOT"/logs/ai_token_accounting.log

# Obtém a data atual no formato AAAA-MM
CURRENT_MONTH=$(date +%Y-%m)

# Cria o nome do arquivo de rollover esperado para o mês atual
ROLLOVER_FILE="$LOG_FILE".$CURRENT_MONTH

echo "$ROLLOVER_FILE"

# Verifica se o arquivo de rollover do mês atual existe
if [ -f "$ROLLOVER_FILE" ]; then
  echo "Rollover detectado para o mês atual ($CURRENT_MONTH)."

  # Cria um novo arquivo de log com o conteúdo do rollover + o conteúdo atual
  cat "$ROLLOVER_FILE" "$LOG_FILE" > "$LOG_FILE.new"

  # Substitui o arquivo de log antigo pelo novo
  mv "$LOG_FILE.new" "$LOG_FILE"

  echo "Novo arquivo de log criado com conteúdo do rollover e conteúdo atual."

  # Remove o arquivo de rollover
  rm "$ROLLOVER_FILE"

  echo "Arquivo de rollover removido."
else
  echo "Nenhum rollover detectado para o mês atual."
fi

# Executa o arquivo principal (substitua pelo comando real para executar generate_ai_content.py)
#python generate_ai_content.py # Substitua pelo comando correto com os argumentos necessários

# Exemplo: apenas para demonstração, cria ou atualiza o arquivo de log
echo "$(date) - Log atualizado" >> "$LOG_FILE"
echo "Arquivo de log ($LOG_FILE) atualizado."

python3 "$PROJECT_ROOT"/src/documentation/generate_ai_content.py

exit 0