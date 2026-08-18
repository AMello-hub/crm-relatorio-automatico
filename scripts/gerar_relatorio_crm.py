#!/usr/bin/env python3
import requests, os, urllib.parse, time
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE", "5511968526705")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "7883678")

def ler_dados():
    try:
        print("1 Lendo...")
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
        print(f"OK {len(items)} clientes")
        return items
    except Exception as e:
        print(f"Erro: {e}")
        return []

def filtrar(items):
    hoje = datetime.now().date()
    limite_vencidos = hoje - timedelta(days=30)
    
    segunda_dessa = hoje - timedelta(days=hoje.weekday())
    domingo_dessa = segunda_dessa + timedelta(days=6)
    
    filtrado = []
    for item in items:
        try:
            fu = datetime.strptime(item['fu_date'], '%Y-%m-%d').date()
            if limite_vencidos <= fu <= domingo_dessa:
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
    status_lower = status.lower()
    status_sem_acento = status_lower.replace('ã', 'a').replace('é', 'e').replace('í', 'i')
    if 'reuniao' in status_sem_acento or 'enviada' in status_sem_acento or 'iniciar' in status_sem_acento:
        return 'reuniao'
    elif 'spot atual' in status_sem_acento or 'recorrente' in status_sem_acento:
        return 'spot'
    elif 'somente spot' in status_sem_acento:
        return 'spot_only'
    elif 'lead' in status_sem_acento:
        return 'lead'
    return 'outro'

def gerar_msgs_duas_partes(items):
    if not items:
        return "Relatorio CRM\nNenhum Follow Up", ""
    
    hoje = datetime.now().date()
    segunda_dessa = hoje - timedelta(days=hoje.weekday())
    domingo_dessa = segunda_dessa + timedelta(days=6)
    data_ini = formatar_data(segunda_dessa.isoformat())
    data_fim = formatar_data(domingo_dessa.isoformat())
    
    reuniao = [i for i in items if categorizar(i['status']) == 'reuniao']
    spot = [i for i in items if categorizar(i['status']) == 'spot']
    spot_only = [i for i in items if categorizar(i['status']) == 'spot_only']
    lead = [i for i in items if categorizar(i['status']) == 'lead']
    
    total_clientes = len(reuniao) + len(spot) + len(spot_only) + len(lead)
    meio = total_clientes // 2
    
    msg1 = f"📋 Relatorio CRM - Acao Esta Semana ({data_ini}-{data_fim})\n"
    msg2 = ""
    
    contador = 0
    na_parte2 = False
    
    if reuniao:
        if not na_parte2:
            msg1 += "\n🎯 Reunies, Envios e Follow Ups:\n"
        else:
            msg2 += "\n🎯 Reunies, Envios e Follow Ups:\n"
        
        for item in reuniao:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:35] if item['acao'] else "Sem acao"
            cliente = item['cliente'][:30]
            linha = f"* *{data}* - {cliente} - {acao}\n"
            
            if not na_parte2 and contador < meio:
                msg1 += linha
            else:
                if not na_parte2:
                    na_parte2 = True
                msg2 += linha
            contador += 1
    
    if spot:
        if not na_parte2:
            msg1 += "\n📌 Spot Atual e Recorrente:\n"
        else:
            msg2 += "\n📌 Spot Atual e Recorrente:\n"
        
        for item in spot:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:35] if item['acao'] else "Sem acao"
            cliente = item['cliente'][:30]
            linha = f"* *{data}* - {cliente} - {acao}\n"
            
            if not na_parte2 and contador < meio:
                msg1 += linha
            else:
                if not na_parte2:
                    na_parte2 = True
                msg2 += linha
            contador += 1
    
    if spot_only:
        if not na_parte2:
            msg1 += "\n📦 Somente Spot:\n"
        else:
            msg2 += "\n📦 Somente Spot:\n"
        
        for item in spot_only:
            data = formatar_data(item['fu_date'])
            acao = item['acao'][:35] if item['acao'] else "Sem acao"
            cliente = item['cliente'][:30]
            linha = f"* *{data}* - {cliente} - {acao}\n"
            
            if not na_parte2 and contador < meio:
                msg1 += linha
            else:
                if not na_parte2:
                    na_parte2 = True
                msg2 += linha
            contador += 1
    
    if lead:
        if not na_parte2:
            msg1 += "\n❌ Lead Perdido:\n"
        else:
            msg2 += "\n❌ Lead Perdido:\n"
        
        for item in lead:
            data = formatar_data(item['fu_date'])
            cliente = item['cliente'][:30]
            fu_date = datetime.strptime(item['fu_date'], '%Y-%m-%d').date()
            if fu_date <= hoje:
                linha = f"* *{data}* - {cliente}\n"
                
                if not na_parte2 and contador < meio:
                    msg1 += linha
                else:
                    if not na_parte2:
                        na_parte2 = True
                    msg2 += linha
                contador += 1
    
    msg2 += "\n✅ Sincronizado com Notion"
    
    return msg1, msg2

def enviar(msg, parte):
    try:
        print(f"Enviando Parte {parte}...")
        msg_enc = urllib.parse.quote(msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&apikey={CALLMEBOT_API_KEY}&text={msg_enc}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"OK Parte {parte} enviada!")
        return resp.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

print("Gerando relatorio em 2 partes...")
if not NOTION_TOKEN:
    exit(1)

items = ler_dados()
if not items:
    exit(0)

print("\nFiltrando...")
items = filtrar(items)

print("\nGerando 2 mensagens...")
msg1, msg2 = gerar_msgs_duas_partes(items)

print("\n" + "="*50)
print("PARTE 1:")
print("="*50)
print(msg1)

print("\n" + "="*50)
print("PARTE 2:")
print("="*50)
print(msg2)

print("\nEnviando Parte 1...")
enviar(msg1, 1)

print("\nAguardando 90 segundos...")
time.sleep(90)

print("\nEnviando Parte 2...")
enviar(msg2, 2)

print("\nPronto!")
