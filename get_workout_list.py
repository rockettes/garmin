import os
import json
import csv
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        print("❌ Credenciais ausentes.")
        exit()
    return Garmin(email, password)

def fetch_full_dictionary():
    client = authenticate()
    client.login()
    print("🔐 Logado. Iniciando download do dicionário mestre...")

    all_exercises = []
    start = 0
    limit = 100 # Baixa de 100 em 100 para não estourar
    
    while True:
        print(f"⬇️  Baixando página: {start} a {start + limit}...", end="\r")
        try:
            # Endpoint Mágico: Lista todos os exercícios disponíveis
            # Nota: O parametro 'locale' é inferido pelo perfil ou header, 
            # torcemos para vir em PT-BR se sua conta for BR.
            url = f"/exercise-service/exercises?start={start}&limit={limit}"
            response = client.connectapi(url, method="GET")
            
            if not response:
                break
            
            all_exercises.extend(response)
            
            if len(response) < limit:
                # Chegou no fim da lista
                break
                
            start += limit
            
        except Exception as e:
            print(f"\n❌ Erro ao baixar página {start}: {e}")
            break

    print(f"\n✅ Download concluído! Total de exercícios encontrados: {len(all_exercises)}")
    return all_exercises

def save_data(exercises):
    # 1. Salva o JSON Bruto (Para backup e análise futura)
    with open("garmin_dictionary_raw.json", "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=4, ensure_ascii=False)
    print("💾 JSON bruto salvo em 'garmin_dictionary_raw.json'")

    # 2. Cria o CSV Mapa (O que nos interessa)
    # Filtramos apenas o que é relevante para o seu script
    csv_file = "mapa_completo_garmin.csv"
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["NOME_NO_APP (PT)", "CATEGORIA_INTERNA (Key)", "EXERCICIO_INTERNO (Key)", "ID"])
        
        for item in exercises:
            # Tenta extrair os campos. A estrutura exata pode variar, 
            # mas geralmente é 'name', 'category', 'exerciseKey'
            name_pt = item.get('name', 'N/A')
            
            # As vezes a category vem como objeto, as vezes string
            cat_obj = item.get('category', {})
            cat_key = cat_obj.get('typeKey') if isinstance(cat_obj, dict) else item.get('categoryKey', 'UNK')
            
            # A chave do exercício
            ex_key = item.get('exerciseKey', 'UNK')
            ex_id = item.get('id', '')

            writer.writerow([name_pt, cat_key, ex_key, ex_id])

    print(f"💎 MAPA DE OURO salvo em '{csv_file}'")
    print("➡️  Abra o CSV e procure por 'Extensora' ou 'Agachamento' para ver a verdade!")

if __name__ == "__main__":
    data = fetch_full_dictionary()
    if data:
        save_data(data)