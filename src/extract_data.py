# -*- coding: utf-8 -*-
import os
import requests
from urllib.parse import urlparse, parse_qs

# Links que descobrimos
URLS = [
    "https://connect.garmin.com/web-translations/exercise_types/exercise_types_pt.properties?bust=5.21.0.16",
    "https://connect.garmin.com/web-translations/exercise_types/exercise_types_pt_BR.properties?bust=5.21.0.16",
    "https://connect.garmin.com/web-translations/exercise_types/exercise_types_pt_BR.properties?bust=5.21.0.15a",
    "https://connect.garmin.com/web-translations/exercise_types/exercise_types_pt.properties?bust=5.21.0.15a"
]

# Configuração de Caminhos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível e entra em data/raw
RAW_DATA_DIR = os.path.join(os.path.dirname(CURRENT_DIR), 'data', 'raw')

def get_filename_from_url(url):
    """Gera um nome de arquivo único baseado na URL e na versão (bust)."""
    parsed_url = urlparse(url)
    # Pega o nome base (ex: exercise_types_pt.properties)
    base_name = os.path.basename(parsed_url.path)
    # Remove a extensão .properties para limpar
    name_without_ext = base_name.replace('.properties', '')
    
    # Pega a versão (bust)
    query_params = parse_qs(parsed_url.query)
    version = query_params.get('bust', ['unknown'])[0]
    
    # Monta o nome final: exercise_types_pt_BR_5.21.0.16.txt
    return f"{name_without_ext}_{version}.txt"

def download_data():
    print(f"🚀 Iniciando extração de dados...")
    print(f"📂 Pasta de destino: {RAW_DATA_DIR}")
    
    # Garante que a pasta existe
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
        print("   -> Pasta criada.")

    for url in URLS:
        filename = get_filename_from_url(url)
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        print(f"⬇️  Baixando: {filename}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status() # Lança erro se der 404/500
            
            # Salva o conteúdo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print(f"   ✅ Salvo!")
            
        except Exception as e:
            print(f"   ❌ Erro ao baixar {url}: {e}")

    print("\n✨ Download concluído! Agora rode o 'build_db.py' para processar.")

if __name__ == "__main__":
    download_data()