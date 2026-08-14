#!/usr/bin/env python3
import requests, os, json

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"

print("🚀 MOSTRANDO ESTRUTURA DAS PROPRIEDADES\n")

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

try:
    response = requests.post(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Erro: {response.status_code}")
        exit(1)
    
    data = response.json()
    
    if not data.get('results'):
        print("Sem resultados")
        exit(0)
    
    # Mostra o PRIMEIRO cliente com TODAS as propriedades
    first_page = data['results'][0]
    props = first_page.get('properties', {})
    
    print("PRIMEIRO CLIENTE - TODAS AS PROPRIEDADES:")
    print("="*60)
    
    for key, value in props.items():
        print(f"\n📌 {key}:")
        print(f"   Tipo: {list(value.keys())}")
        print(f"   Valor: {value}")

except Exception as e:
    print(f"❌ Erro: {e}")
