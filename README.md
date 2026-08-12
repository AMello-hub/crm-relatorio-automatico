# CRM Relatório Automático

Gera e envia relatório do CRM Notion para WhatsApp automaticamente.

## Execução

- **Frequência:** Todos os dias de semana (segunda a sexta)
- **Horário:** 08:00 AM (Brasília)
- **Destino:** WhatsApp automático

## Setup

1. Criar Token Notion
2. Criar Repositório GitHub
3. Adicionar arquivos (este repositório)
4. Configurar Secrets
5. Testar execução

## Secrets Necessários

Configure estes 3 secrets no GitHub (Settings → Secrets and variables → Actions):

- `NOTION_API_KEY` - Token da API Notion
- `CALLMEBOT_PHONE` - Seu número WhatsApp (com código de país)
- `CALLMEBOT_API_KEY` - API Key do CallMeBot

## Como Usar

1. Abra seu repositório no GitHub
2. Vá em **Actions**
3. Clique no workflow "📋 Relatório CRM Automático"
4. Clique **"Run workflow"**
5. Aguarde 2-3 minutos
6. Verifique seu WhatsApp

## Arquivos

- `.github/workflows/relatorio-crm.yml` - Workflow do GitHub Actions
- `scripts/gerar_relatorio_crm.py` - Script que gera e envia o relatório
- `requirements.txt` - Dependências Python

## Status

✅ Pronto para usar!
