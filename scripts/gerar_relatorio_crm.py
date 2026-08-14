#!/usr/bin/env python3
import requests, os, urllib.parse
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE", "5511968526705")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "7883678")

def ler_dados():
    try:
        print("1️⃣ Lendo...")
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
            
            # Cliente (title)
            cliente_prop = props.get('Cliente', {}).get('title', [])
            cliente = cliente_prop[0]['text']['content'] if cliente_prop else None
            
            # Status (STATUS, não select!)
            status_prop = props.get('Status', {}).get('status', {})
            status = status_prop.get('name', '') if status_prop else ''
            
            # Ação Específica (rich_text)
            acao_prop = props.get('Ação Específica', {}).get('rich_text', [])
            acao = acao_prop[0]['text']['content'] if acao_prop else ''
            
            # Follow Up Date (date)
            fu_prop = props.get('Follow Up Date', {}).get('date', {})
            fu_date = fu_prop.get('start') if fu_prop else None
            
            if cliente and fu_date and status:
                items.append({
                    'cliente': cliente,
                    'status': status,
                    'acao': acao,
                    'fu_date': fu_date
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

def categorizar(status):
    if not status:
        return 'outro'
    
    status_lower = status.lower()
    
    if 'reunião' in status_lower or 'enviada' in status_lower or 'iniciar' in status_lower:
        return 'reuniao'
    elif 'spot atual' in status_lower or 'recorrente' in status_lower:
        return 'spot'
    elif 'somente spot' in status_lower:
        return 'spot_only'
    elif 'lead' in status_lower:
        return 'lead'
    
    return 'outro'

def gerar_msg(items):
    if not items:
        return "📋 Relatório CRM - Ação Esta Semana\nNenhum Follow Up"
    
    reuniao = [i for i in items if categorizar(i['status']) == 'reuniao']
    spot = [i for i in items if categorizar(i['status']) == 'spot']
    spot_only = [i for i in items if categorizar(i['status']) == 'spot_only']
    lead = [i for i in items if categorizar(i['status']) == 'lead']
    
    data_ini = formatar_data(items[0]['fu_date'])
    data_fim = formatar_data(items[-1]['fu_date'])
    
    msg = f"📋 Relatório CRM - Ação Esta Semana ({data_ini}-{data_fim})\n"
    
    if reuniao:
        msg += "\n🎯 REUNIÕES, ENVIOS E FOLLOW UPS:\n"
        for item in reuniao:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:50] if item['acao'] else "Sem ação"
            cliente = item['cliente'][:35]
            msg += f"• {data} - {cliente} - {acao}\n"
    
    if spot:
        msg += "\n📌 SPOT ATUAL E RECORRENTE:\n"
        for item in spot:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:50] if item['acao'] else "Sem ação"
            cliente = item['cliente'][:35]
            msg += f"• {data} - {cliente} - {acao}\n"
    
    if spot_only:
        msg += "\n📦 SOMENTE SPOT:\n"
        for item in spot_only:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:50] if item['acao'] else "Sem ação"
            cliente = item['cliente'][:35]
            msg += f"• {data} - {cliente} - {acao}\n"
    
    if lead:
        msg += "\n❌ LEAD PERDIDO:\n"
        for item in lead:
            data = formatar_data(item['fu_date'])
            cliente = item['cliente'][:35]
            msg += f"• {data} - {cliente}\n"
    
    msg += "\n✅ Sincronizado com Notion"
    return msg

def enviar(msg):
    try:
        print("2️⃣ Enviando...")
        msg_enc = urllib.parse.quote(msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&apikey={CALLMEBOT_API_KEY}&text={msg_enc}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print("✅ Enviado!")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

print("🚀 Gerando relatório...")
if not NOTION_TOKEN:
    exit(1)

items = ler_dados()
if not items:
    print("Sem dados")
    exit(0)

print("\n2️⃣ Filtrando...")
items = filtrar(items)

print("\n3️⃣ Gerando mensagem...")
msg = gerar_msg(items)

print("\n" + "="*60)
print(msg)
print("="*60)

enviar(msg)
print("✅ Pronto!")
