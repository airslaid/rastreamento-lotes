@echo off
echo Configurando Git para projeto...

REM CONFIGURE SEUS DADOS AQUI
set "GIT_USER=airslaid"
set "GIT_EMAIL=ti@grupoairslaid.com.br"
set "REPO_URL=https://github.com/airslaid/rastreamento-lotes.git"

REM Entrar na pasta atual do script
cd /d %~dp0

REM Verifica se já é um repositório Git
IF NOT EXIST .git (
    git init
    git remote add origin %REPO_URL%
    echo Inicializado repositório Git.
) ELSE (
    echo Já é um repositório Git.
)

REM Configura nome e email
git config user.name "%GIT_USER%"
git config user.email "%GIT_EMAIL%"

REM Cria .gitignore
echo Criando .gitignore...
echo *.pyc> .gitignore
echo __pycache__/>> .gitignore
echo .env>> .gitignore
echo lotes_html_qr.xlsx>> .gitignore

REM Adiciona e envia os arquivos
git add .
git commit -m "Envio automático dos arquivos de rastreamento"
git branch -M main
git push -u origin main

pause