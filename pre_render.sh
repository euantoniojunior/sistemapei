#!/bin/bash
# Script para instalar wkhtmltopdf no Render

echo "Instalando wkhtmltopdf..."

# Baixa e instala o wkhtmltopdf
sudo apt-get update
sudo apt-get install -y wkhtmltopdf

# Confirma instalação
wkhtmltopdf --version
