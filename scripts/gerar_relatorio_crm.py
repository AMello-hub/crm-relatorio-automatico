#!/usr/bin/env python3
import requests, os, json

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"

print("🚀 TESTE DIRETO COM A API NOTION\n")

print(f"Token: {NOTION_TOKEN[:30]}..." if NOTION_TOKEN else "Token: VAZIO!")
print(f"Database ID: {NOTION_DATABASE_ID}\n")

if not NOTION_TOKEN:
    print("❌ Token não configurado!")
    exit(1)

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

print(f"URL: {url}\n")
print("Enviando requisição...\n")

try:
    response = requests.post(url, headers=headers, timeout=10)
    
    print(f"Status HTTP: {response.status_code}")
    print(f"Headers: {response.headers}\n")
    
    print("RESPOSTA COMPLETA:")
    print("="*60)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:2000])
    print("="*60)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Sucesso!")
        print(f"Total de resultados: {len(data.get('results', []))}")
        
        # Mostra o primeiro resultado
        if data.get('results'):
            print(f"\nPrimeiro resultado:")
            print(json.dumps(data['results'][0], indent=2, ensure_ascii=False)[:500])
    else:
        print(f"\n❌ Erro {response.status_code}")
        print(f"Resposta: {response.text}")

except Exception as e:
    print(f"❌ Erro na requisição: {e}")
    import traceback
    traceback.print_exc()
