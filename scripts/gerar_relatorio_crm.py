#!/usr/bin/env python3
"""
Script para gerar e enviar relatório CRM do Notion para WhatsApp
Com formatação melhorada e agrupamento por tipo de status
"""

import requests
import os
import urllib.parse
from datetime import datetime, timedelta

# ============================================
# CONFIGURAÇÕES
# ============================================

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE", "5511968526705")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "7883678")

print("🚀 Gerando relatório CRM com dados do Notion...")
print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ============================================
# FUNÇÃO: Ler dados do Notion
# ============================================

def ler_dados_notion():
    """Lê dados da database Notion"""
    try:
        print("\n1️⃣ Lendo dados do Notion...")
        
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        print(f"🔗 Conectando: {NOTION_DATABASE_ID[:20]}...")
        response = requests.post(url, headers=headers, timeout=10)
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erro {response.status_code}")
            return []
        
        data = response.json()
        items = []
        
        for page in data.get('results', []):
            props = page['properties']
            
            cliente = props.get('Cliente', {}).get('title', [])
            cliente_text = cliente[0]['text']['content'] if cliente else 'N/A'
            
            status = props.get('Status', {}).get('select', {})
            status_text = status.get('name', 'N/A') if status else 'N/A'
            
            acao = props.get('Ação Específica', {}).get('rich_text', [])
            acao_text = acao[0]['text']['content'] if acao else ''
            
            fu_date = props.get('Follow Up Date', {}).get('date', {})
            fu_text = fu_date.get('start', '') if fu_date else ''
            
            if fu_text:
                items.append({
                    'cliente': cliente_text,
                    'status': status_text,
                    'acao': acao_text,
                    'fu_date': fu_text
                })
        
        print(f"✅ {len(items)} clientes encontrados")
        return items
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

# ============================================
# FUNÇÃO: Processar dados
# ============================================

def processar_dados(items):
    """Filtra dados da semana"""
    hoje = datetime.now().date()
    fim_semana = hoje + timedelta(days=7)
    
    items_semana = []
    
    for item in items:
        try:
            fu_date = datetime.strptime(item['fu_date'], '%Y-%m-%d').date()
            if hoje <= fu_date <= fim_semana:
                items_semana.append(item)
        except:
            pass
    
    items_semana.sort(key=lambda x: x['fu_date'])
    
    print(f"✅ {len(items_semana)} com Follow Up esta semana")
    
    return items_semana

# ============================================
# FUNÇÃO: Organizar por status
# ============================================

def organizar_por_status(items):
    """Organiza items por tipo de status"""
    
    resultado = {
        'reuniao_enviada': [],
        'spot_recorrente': [],
        'somente_spot': [],
        'lead_perdido': []
    }
    
    for item in items:
        status = item['status'].lower()
        
        # Categoria 1: Reunião, Envios, Follow Ups
        if any(x in status for x in ['reunião', 'enviada', 'iniciar']):
            resultado['reuniao_enviada'].append(item)
        
        # Categoria 2: Spot Atual e Recorrente
        elif any(x in status for x in ['spot atual', 'recorrente']):
            resultado['spot_recorrente'].append(item)
        
        # Categoria 3: Somente Spot
        elif 'somente spot' in status:
            resultado['somente_spot'].append(item)
        
        # Categoria 4: Lead Perdido
        elif 'lead perdido' in status:
            resultado['lead_perdido'].append(item)
    
    return resultado

# ============================================
# FUNÇÃO: Converter data para dd/mm
# ============================================

def formatar_data(data_str):
    """Converte 2026-08-13 para 13/08"""
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m')
    except:
        return data_str

# ============================================
# FUNÇÃO: Gerar mensagem formatada
# ============================================

def gerar_mensagem(items_org):
    """Gera mensagem com formatação melhorada"""
    
    msg = "📋 Relatório CRM - Ação Esta Semana\n\n"
    
    # Seção 1: Reunião, Envios, Follow Ups
    if items_org['reuniao_enviada']:
        msg += "🎯 REUNIÕES, ENVIOS E FOLLOW UPS:\n"
        for item in items_org['reuniao_enviada']:
            data = formatar_data(item['fu_date'])
            acao = item['acao'] if item['acao'] else item['status']
            msg += f"• {data} - {item['cliente']} - {acao}\n"
        msg += "\n"
    
    # Seção 2: Spot Atual e Recorrente
    if items_org['spot_recorrente']:
        msg += "📌 SPOT ATUAL E RECORRENTE:\n"
        for item in items_org['spot_recorrente']:
            data = formatar_data(item['fu_date'])
            acao = item['acao'] if item['acao'] else item['status']
            msg += f"• {data} - {item['cliente']} - {acao}\n"
        msg += "\n"
    
    # Seção 3: Somente Spot
    if items_org['somente_spot']:
        msg += "📦 SOMENTE SPOT:\n"
        for item in items_org['somente_spot']:
            data = formatar_data(item['fu_date'])
            acao = item['acao'] if item['acao'] else item['status']
            msg += f"• {data} - {item['cliente']} - {acao}\n"
        msg += "\n"
    
    # Seção 4: Lead Perdido
    if items_org['lead_perdido']:
        msg += "❌ LEAD PERDIDO:\n"
        for item in items_org['lead_perdido']:
            data = formatar_data(item['fu_date'])
            msg += f"• {data} - {item['cliente']}\n"
        msg += "\n"
    
    msg += "✅ Relatório sincronizado com Notion"
    
    return msg

# ============================================
# FUNÇÃO: Enviar WhatsApp
# ============================================

def enviar_whatsapp(mensagem):
    """Envia para WhatsApp via CallMeBot"""
    try:
        print("\n5️⃣ Enviando para WhatsApp...")
        
        msg_encoded = urllib.parse.quote(mensagem)
        url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&apikey={CALLMEBOT_API_KEY}&text={msg_encoded}"
        
        print(f"📱 Telefone: {CALLMEBOT_PHONE}")
        print(f"🔗 Enviando para CallMeBot...")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print(f"⚠️ Status: {response.status_code}")
            print(f"Resposta: {response.text[:100]}")
            return False
    
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

# ============================================
# MAIN
# ============================================

if not NOTION_TOKEN:
    print("❌ NOTION_API_KEY não configurado!")
    exit(1)

print(f"✅ Token detectado")

# Lê dados
items = ler_dados_notion()

if not items:
    print("⚠️ Sem dados")
    exit(0)

# Processa
print("\n2️⃣ Filtrando Follow Ups...")
items_semana = processar_dados(items)

# Organiza
print("\n3️⃣ Organizando por status...")
items_org = organizar_por_status(items_semana)

# Gera mensagem
print("\n4️⃣ Gerando mensagem...")
mensagem = gerar_mensagem(items_org)

print("\n" + "="*60)
print(mensagem)
print("="*60)

# Envia WhatsApp
enviar_whatsapp(mensagem)

print("\n✅ Processo concluído!")
