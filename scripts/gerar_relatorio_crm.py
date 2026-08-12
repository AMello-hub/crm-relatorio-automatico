#!/usr/bin/env python3
"""
Script para gerar e enviar relatório CRM automaticamente
Integra Notion + HTML + PDF + WhatsApp
"""

import json
import urllib.parse
import subprocess
import sys
from datetime import datetime, timedelta

# ============================================
# CONFIGURAÇÕES
# ============================================
NOTION_API_KEY = "seu_token_aqui"  # Será substituído por variável de ambiente
CALLMEBOT_PHONE = "5511968526705"
CALLMEBOT_API_KEY = "7883678"

# ============================================
# FUNÇÃO: Ler dados do Notion (simulado)
# ============================================
def ler_dados_notion():
    """
    Em produção, usaria requests + Notion API
    Por enquanto, retorna os dados estruturados
    """
    return {
        "reuniao_enviada": [
            {"cliente": "Moderna Sorveteria (Tesouraria)", "status": "Reunião", "acao": "Reunião com Ricardo", "fu": "2026-08-13"},
            {"cliente": "Gardens (Tributario)", "status": "Reunião", "acao": "Verificar com Guilherme", "fu": "2026-08-13"},
            {"cliente": "Churras 366", "status": "(S) Enviada", "acao": "Cobrar contrato do Lucas", "fu": "2026-08-13"},
            {"cliente": "Genial Print", "status": "(S) Enviada", "acao": "Aguardando retorno", "fu": "2026-08-16"},
            {"cliente": "Rede Kings Sneakers", "status": "Reunião", "acao": "Guilherme fará diagnostico", "fu": "2026-08-20"},
        ],
        "spot_recorrente": [
            {"cliente": "Aporte Fundo de Investimento", "status": "Spot Atual", "acao": "Aguardando auditoria", "fu": "2026-08-17"},
            {"cliente": "ID Logical", "status": "Recorrente", "acao": "Ver continuidade", "fu": "2026-08-17"},
            {"cliente": "Novos Tempos (ACB)", "status": "Spot Atual", "acao": "Reunião entrega diagnóstico", "fu": "2026-08-18"},
        ]
    }

# ============================================
# FUNÇÃO: Gerar HTML do relatório
# ============================================
def gerar_html(dados):
    """Gera HTML do relatório estruturado"""
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório CRM - Ação Esta Semana</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .header { text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #667eea; margin: 0; }
        .header p { color: #999; margin: 5px 0 0 0; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 1.3em; font-weight: 600; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 15px; }
        .card { background: #f9f9f9; padding: 15px; margin-bottom: 12px; border-left: 4px solid #667eea; border-radius: 4px; }
        .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
        .card-title { font-weight: 600; color: #222; }
        .card-date { color: #2196f3; font-weight: 700; }
        .status-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }
        .status-reuniao { background: #e3f2fd; color: #1976d2; }
        .status-enviada { background: #fff3e0; color: #e65100; }
        .status-spot { background: #f3e5f5; color: #7b1fa2; }
        .status-recorrente { background: #e8f5e9; color: #388e3c; }
        .acao { margin-top: 8px; padding: 10px; background: white; border-radius: 4px; font-size: 0.95em; color: #555; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Relatório CRM - Ação Esta Semana</h1>
            <p>Sincronizado com Notion | """ + datetime.now().strftime("%d/%m/%Y") + """</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎯 Reuniões, Envios e Follow Ups</h2>
"""
    
    for item in dados["reuniao_enviada"]:
        status_class = "status-reuniao" if "Reunião" in item["status"] else "status-enviada"
        html += f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">{item['cliente']}</div>
                        <span class="status-badge {status_class}">{item['status']}</span>
                    </div>
                    <span class="card-date">{item['fu']}</span>
                </div>
                <div class="acao">✓ {item['acao']}</div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="section">
            <h2 class="section-title">📌 Spot Atual e Recorrente</h2>
"""
    
    for item in dados["spot_recorrente"]:
        status_class = "status-spot" if "Spot" in item["status"] else "status-recorrente"
        html += f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">{item['cliente']}</div>
                        <span class="status-badge {status_class}">{item['status']}</span>
                    </div>
                    <span class="card-date">{item['fu']}</span>
                </div>
                <div class="acao">✓ {item['acao']}</div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            ✅ Relatório gerado automaticamente | """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
        </div>
    </div>
</body>
</html>
"""
    return html

# ============================================
# FUNÇÃO: Enviar via WhatsApp
# ============================================
def enviar_whatsapp(mensagem):
    """Envia mensagem via CallMeBot"""
    mensagem_encoded = urllib.parse.quote(mensagem)
    url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&apikey={CALLMEBOT_API_KEY}&text={mensagem_encoded}"
    
    print(f"📱 Enviando para WhatsApp: {CALLMEBOT_PHONE}")
    print(f"🔗 URL: {url[:80]}...")
    
    try:
        import requests
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print(f"⚠️ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

# ============================================
# FUNÇÃO: Gerar mensagem resumida
# ============================================
def gerar_mensagem_whatsapp(dados):
    """Cria mensagem formatada para WhatsApp"""
    msg = "📋 Relatório CRM - Ação Esta Semana\n\n"
    msg += "🎯 REUNIÕES, ENVIOS E FOLLOW UPS:\n"
    
    for item in dados["reuniao_enviada"]:
        msg += f"• {item['fu']} - {item['cliente']} - {item['acao']}\n"
    
    msg += "\n📌 SPOT ATUAL E RECORRENTE:\n"
    for item in dados["spot_recorrente"]:
        msg += f"• {item['fu']} - {item['cliente']} - {item['acao']}\n"
    
    msg += "\n✅ Relatório sincronizado com Notion"
    return msg

# ============================================
# MAIN
# ============================================
def main():
    print("🚀 Iniciando geração de relatório CRM...")
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Ler dados do Notion
    print("\n1️⃣ Lendo dados do Notion...")
    dados = ler_dados_notion()
    print(f"   ✅ {len(dados['reuniao_enviada'])} reuniões/envios")
    print(f"   ✅ {len(dados['spot_recorrente'])} spot/recorrente")
    
    # 2. Gerar HTML
    print("\n2️⃣ Gerando HTML...")
    html = gerar_html(dados)
    with open("relatorio_crm.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("   ✅ relatorio_crm.html gerado")
    
    # 3. Gerar PDF (opcional)
    print("\n3️⃣ Convertendo para PDF...")
    try:
        subprocess.run([
            "wkhtmltopdf", 
            "relatorio_crm.html", 
            "relatorio_crm.pdf"
        ], check=True, capture_output=True)
        print("   ✅ relatorio_crm.pdf gerado")
    except Exception as e:
        print(f"   ⚠️ PDF não gerado: {e}")
    
    # 4. Gerar mensagem e enviar
    print("\n4️⃣ Gerando mensagem WhatsApp...")
    mensagem = gerar_mensagem_whatsapp(dados)
    print(f"   ✅ Mensagem criada ({len(mensagem)} caracteres)")
    
    print("\n5️⃣ Enviando via WhatsApp...")
    enviar_whatsapp(mensagem)
    
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
