#!/usr/bin/env python3
import requests, os
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"

def ler_dados():
    try:
        print("Lendo...")
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        items = []
        for page in response.json().get('results', []):
            props = page['properties']
            cliente_prop = props.get('Cliente', {}).get('title', [])
            cliente = cliente_prop[0]['text']['content'] if cliente_prop else None
            status_prop = props.get('Status', {}).get('status', {})
            status = status_prop.get('name', '') if status_prop else ''
            acao_prop = props.get('Ação Específica', {}).get('rich_text', [])
            acao = acao_prop[0]['text']['content'] if acao_prop else ''
            fu_prop = props.get('Follow Up Date', {}).get('date', {})
            fu_date = fu_prop.get('start') if fu_prop else None
            if cliente and fu_date and status:
                items.append({'cliente': cliente, 'status': status, 'acao': acao, 'fu_date': fu_date})
        print(f"Total: {len(items)} clientes\n")
        
        # MOSTRA TODOS OS CLIENTES
        print("="*60)
        for item in items:
            print(f"Cliente: {item['cliente']}")
            print(f"  Status: {item['status']}")
            print(f"  FUP: {item['fu_date']}")
            print(f"  Acao: {item['acao']}")
            print()
        
        return items
    except Exception as e:
        print(f"Erro: {e}")
        return []

print("DEBUG - Todos os clientes do Notion:\n")
items = ler_dados()
