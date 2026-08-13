#!/usr/bin/env python3
"""
Script para gerar e enviar relatório CRM do Notion para WhatsApp
Compatível com novo token Notion (ntn_)
"""

import requests
import os
from datetime import datetime, timedelta

# ============================================
# CONFIGURAÇÕES
# ============================================

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = "35427a5ac10780d599a8f851bdead6c8"

print("🚀 Gerando relatório CRM com dados do Notion...")
print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ============================================
# FUNÇÃO: Ler dados do Notion com novo token
# ============================================

def ler_dados_notion():
    """Lê dados da database Notion com novo token ntn_"""
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
        
        if response.status_code == 401:
            print("❌ Erro 401: Token não autorizado ou inválido")
            print("⚠️ Verifique o token NOTION_API_KEY no GitHub Secrets")
            return []
        
        if response.status_code != 200:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return []
        
        response.raise_for_status()
        
        data = response.json()
        items = []
        
        for page in data.get('results', []):
            props = page['properties']
            
            # Extrai dados
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
        print(f"❌ Erro ao ler Notion: {e}")
        return []

# ============================================
# FUNÇÃO: Filtrar e organizar dados
# ============================================

def processar_dados(items):
    """Filtra e organiza dados da semana"""
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
# FUNÇÃO: Gerar mensagem
# ============================================

def gerar_mensagem(items):
    """Gera mensagem formatada"""
    
    msg = "📋 Relatório CRM - Ação Esta Semana\n\n"
    
    if not items:
        msg += "Nenhum Follow Up para esta semana"
        return msg
    
    for item in items:
        data = item['fu_date'].split('-')
        data_fmt = f"{data[2]}/{data[1]}"
        msg += f"• {data_fmt} - {item['cliente']}\n"
        if item['acao']:
            msg += f"  → {item['acao']}\n"
    
    msg += "\n✅ Sincronizado com Notion"
    
    return msg

# ============================================
# MAIN
# ============================================

# Valida token
if not NOTION_TOKEN or NOTION_TOKEN == "":
    print("❌ ERRO: NOTION_API_KEY não configurado!")
    print("⚠️ Adicione o token nos GitHub Secrets")
    exit(1)

print(f"✅ Token Notion detectado: {NOTION_TOKEN[:20]}...")

# Lê dados
items = ler_dados_notion()

if not items:
    print("⚠️ Sem dados. Verifique a conexão com Notion.")
    exit(0)

# Processa
print("\n2️⃣ Filtrando Follow Ups...")
items_semana = processar_dados(items)

# Gera mensagem
print("\n3️⃣ Gerando mensagem...")
mensagem = gerar_mensagem(items_semana)

print("\n" + "="*60)
print(mensagem)
print("="*60)

print("\n✅ Processo concluído!")
print("📱 Mensagem pronta para WhatsApp")
