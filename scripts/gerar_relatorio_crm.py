#!/usr/bin/env python3
import requests, os, urllib.parse
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE", "5511968526705")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "7883678")

def ler_dados():
    try:
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28"
        }
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        items = []
        for page in response.json().get('results', []):
            props = page['properties']
            cliente = props.get('Cliente', {}).get('title', [])
            status = props.get('Status', {}).get('select', {})
            acao = props.get('Ação Específica', {}).get('rich_text', [])
            fu_date = props.get('Follow Up Date', {}).get('date', {})
            
            if fu_date.get('start'):
                items.append({
                    'cliente': cliente[0]['text']['content'] if cliente else 'N/A',
                    'status': status.get('name', '').lower() if status else '',
                    'acao': acao[0]['text']['content'] if acao else '',
                    'fu_date': fu_date.get('start', '')
                })
        
        print(f"✅ {len(items)} clientes")
        return items
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def filtrar(items):
    hoje = datetime.now().date()
    fim = hoje + timedelta(days=30)
    filtrado = []
    
    for item in items:
        try:
            fu = datetime.strptime(item['fu_date'], '%Y-%m-%d').date()
            if hoje <= fu <= fim:
                filtrado.append(item)
        except:
            pass
    
    filtrado.sort(key=lambda x: x['fu_date'])
    return filtrado

def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m')
    except:
        return data_str

def gerar_msg(items):
    if not items:
        return "📋 Relatório CRM - Ação Esta Semana\nNenhum Follow Up"
    
    reuniao = []
    spot = []
    
    for item in items:
        status = item['status']
        if 'reunião' in status or 'enviada' in status or 'iniciar' in status:
            reuniao.append(item)
        elif 'spot atual' in status or 'recorrente' in status:
            spot.append(item)
    
    data_ini = formatar_data(items[0]['fu_date'])
    data_fim = formatar_data(items[-1]['fu_date'])
    
    msg = f"📋 Relatório CRM - Ação Esta Semana ({data_ini}-{data_fim})\n"
    
    if reuniao:
        msg += "\n🎯 REUNIÕES, ENVIOS E FOLLOW UPS:\n"
        for item in reuniao:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:60] if item['acao'] else item['status']
            cliente = item['cliente'][:40]
            msg += f"• {data} - {cliente} - {acao}\n"
    
    if spot:
        msg += "\n📌 SPOT ATUAL E RECORRENTE:\n"
        for item in spot:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:60] if item['acao'] else item['status']
            cliente = item['cliente'][:40]
            msg += f"• {data} - {cliente} - {acao}\n"
    
    msg += "\n✅ Sincronizado com Notion"
    return msg

def enviar(msg):
    try:
        msg_enc = urllib.parse.quote(msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&apikey={CALLMEBOT_API_KEY}&text={msg_enc}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print("✅ Enviado!")
        return resp.status_code == 200
    except:
        return False

print("🚀 Gerando relatório...")
if not NOTION_TOKEN:
    exit(1)

items = ler_dados()
if not items:
    exit(0)

items = filtrar(items)
msg = gerar_msg(items)

print("\n" + "="*60)
print(msg)
print("="*60)

enviar(msg)
print("✅ Pronto!")
