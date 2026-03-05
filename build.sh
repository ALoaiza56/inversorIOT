#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Inicializar la base de datos si es necesario
python init_sqlite.py
