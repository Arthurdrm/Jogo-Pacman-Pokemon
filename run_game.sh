#!/usr/bin/env bash
# Script de execução rápida para o PokePacman (Ash Ketchum Edition)
set -e
cd "$(dirname "$0")"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 main.py "$@"
