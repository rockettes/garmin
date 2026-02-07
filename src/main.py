import argparse
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Adiciona o diretório atual ao path para imports funcionarem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import authenticate_garmin, generate_workout_payload

# Carrega variáveis de ambiente
load_dotenv()

def main():
    # Configuração dos argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Gerador de Treinos Garmin via CSV")
    parser.add_argument('--file', type=str, required=True, help="Caminho para o arquivo CSV (ex: data/ficha_treino.csv)")
    parser.add_argument('--name', type=str, default="Treino Customizado Python", help="Nome do treino que aparecerá no Garmin")
    
    args = parser.parse_args()

    # 1. Leitura do CSV
    try:
        print(f"📂 Lendo arquivo: {args.file}")
        df = pd.read_csv(args.file)
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {args.file} não encontrado.")
        return

    # 2. Autenticação
    try:
        print("🔐 Iniciando autenticação...")
        client = authenticate_garmin()
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return

    # 3. Geração do Payload
    print(f"⚙️  Processando {len(df)} etapas para o treino: '{args.name}'...")
    try:
        payload = generate_workout_payload(args.name, df)
    except Exception as e:
        print(f"❌ Erro ao gerar payload JSON: {e}")
        return

    # 4. Envio para a API (Bypass Manual)
    print("🚀 Enviando para a nuvem Garmin (Endpoint Direto)...")
    try:
        # AQUI ESTÁ A CORREÇÃO:
        # Em vez de usar client.create_workout, chamamos o endpoint direto via POST.
        # A biblioteca 'requests' (que o garminconnect usa) aceita o parâmetro 'json' 
        # para serializar o dicionário automaticamente.
        
        url = "/workout-service/workout"
        response = client.connectapi(url, method="POST", json=payload)
        
        # A API geralmente retorna o objeto criado ou 201/200.
        # Se não der exceção, funcionou.
        print("\n✅ SUCESSO! Treino criado.")
        print("📲 Abra o app Garmin Connect > Treinos > Atualize a lista.")
        
    except Exception as e:
        print(f"❌ Erro na API da Garmin: {e}")
        # Dica de debug: Se der erro 400, geralmente é o formato do JSON.
        # Se der erro 403, é permissão/login.

if __name__ == "__main__":
    main()