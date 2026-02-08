# -*- coding: utf-8 -*-
import os
import json
import re
import unidecode

# --- CONFIGURAÇÕES ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_DIR = os.path.join(os.path.dirname(CURRENT_DIR), 'data')
RAW_DATA_DIR = os.path.join(BASE_DATA_DIR, 'raw')
OUTPUT_FILE = os.path.join(BASE_DATA_DIR, 'processed', 'exercises.json')

# 🎛️ CONTROLES DE QUALIDADE (AQUI ESTÁ O QUE VOCÊ PEDIU)
# Mude para True se quiser ignorar arquivos que não sejam pt_BR
USE_ONLY_BR = True 

# Lista Negra: Removemos estes termos de busca específicos se a categoria for X.
# Isso corrige o erro onde a Garmin chama Crucifixo (FLYE) de Supino.
TERM_BLACKLIST = {
    "FLYE": ["supino", "supino com halteres"],
    "HIP_RAISE": ["ponte", "ponte com faixa"], # As vezes confunde com Bridge
}

KNOWN_CATEGORIES = [
    "BANDED_EXERCISES", "BATTLE_ROPE", "BENCH_PRESS", "BIKE_OUTDOOR", "CALF_RAISE",
    "CARDIO", "CARRY", "CHOP", "CORE", "CRUNCH", "CURL", "DEADLIFT", "ELLIPTICAL",
    "FLOOR_CLIMB", "FLYE", "HIP_RAISE", "HIP_STABILITY", "HIP_SWING", "HYPEREXTENSION",
    "INDOOR_BIKE", "LADDER", "LATERAL_RAISE", "LEG_CURL", "LEG_RAISE", "LUNGE",
    "OLYMPIC_LIFT", "PLANK", "PLYO", "POSE", "PULL_UP", "PUSH_UP", "ROW", "RUN_INDOOR",
    "RUN", "SANDBAG", "SHOULDER_PRESS", "SHOULDER_STABILITY", "SHRUG", "SIT_UP",
    "SLED", "SLEDGE_HAMMER", "SQUAT", "STAIR_STEPPER", "SUSPENSION", "TIRE",
    "TOTAL_BODY", "TRICEPS_EXTENSION", "WARM_UP", "BIKE", "SWIM"
]
KNOWN_CATEGORIES.sort(key=len, reverse=True)

def sanitize_text(text):
    if not text: return ""
    text = unidecode.unidecode(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return " ".join(text.split())

def get_sorted_files():
    if not os.path.exists(RAW_DATA_DIR): return []
    all_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.txt')]
    
    valid_files = []
    for f in all_files:
        # Se a trava estiver ativada, ignora arquivos que não tenham "pt_BR" no nome
        if USE_ONLY_BR and "pt_BR" not in f:
            print(f"🚫 Ignorando arquivo (Não é BR): {f}")
            continue
        valid_files.append(os.path.join(RAW_DATA_DIR, f))

    # Prioridade: Arquivos pt_BR sempre primeiro para definir o Label
    valid_files.sort(key=lambda x: 0 if 'pt_BR' in x else 1)
    return valid_files

def parse_files(file_list):
    raw_data_map = {}
    print("📖 Lendo arquivos...")

    for file_path in file_list:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or '=' not in line: continue
            if line.startswith("exercise_picker") or line.startswith("primary_muscle"): continue

            full_key, pt_name = line.split('=', 1)
            full_key = full_key.strip().replace("exercise_type_", "")
            pt_name = pt_name.strip()

            if pt_name == full_key: continue

            category = "UNCATEGORIZED"
            internal_name = full_key

            for cat in KNOWN_CATEGORIES:
                if full_key.startswith(cat + "_") or full_key == cat:
                    category = cat
                    if full_key == cat: internal_name = cat
                    else: internal_name = full_key[len(cat)+1:]
                    break
            
            # Prioriza categorias reais sobre UNCATEGORIZED
            if full_key in raw_data_map:
                current_cat = raw_data_map[full_key]['category']
                if current_cat != "UNCATEGORIZED" and category == "UNCATEGORIZED":
                    continue 
            
            if full_key not in raw_data_map:
                raw_data_map[full_key] = {
                    "id": full_key,
                    "label": pt_name, # pt_BR ganha no label
                    "category": category,
                    "internal_key": internal_name,
                    "search_vocab": set()
                }
            
            # Sanitização e Limpeza
            clean_term = sanitize_text(pt_name)
            
            # Aplica a Lista Negra (Remove termos errados de categorias específicas)
            is_blacklisted = False
            if category in TERM_BLACKLIST:
                for bad_term in TERM_BLACKLIST[category]:
                    if bad_term in clean_term:
                        is_blacklisted = True
                        break
            
            if not is_blacklisted:
                raw_data_map[full_key]["search_vocab"].add(clean_term)
                # Adiciona o nome em inglês também (opcional, pode comentar se quiser só PT)
                raw_data_map[full_key]["search_vocab"].add(sanitize_text(full_key.replace('_', ' ')))

    return raw_data_map

def deduplicate_and_clean(data_dict):
    print("🧹 Iniciando a faxina...")
    grouped_by_label = {}

    for key, item in data_dict.items():
        label_key = item['label'].lower()
        if label_key not in grouped_by_label:
            grouped_by_label[label_key] = []
        grouped_by_label[label_key].append(item)

    final_list = []

    for label, candidates in grouped_by_label.items():
        if len(candidates) == 1:
            final_list.append(candidates[0])
            continue
        
        # Desempate: 1. Categoria definida, 2. Chave mais curta
        candidates.sort(key=lambda x: (
            0 if x['category'] != 'UNCATEGORIZED' else 1,
            len(x['id'])
        ))
        
        winner = candidates[0]
        # Funde vocabulários
        for loser in candidates[1:]:
            winner['search_vocab'].update(loser['search_vocab'])
            
        final_list.append(winner)

    return final_list

def save_json(clean_list):
    output = []
    for item in clean_list:
        output.append({
            "id": item['id'],
            "label": item['label'],
            "search_term": " ".join(item['search_vocab']),
            "category": item['category'],
            "internal_key": item['internal_key']
        })

    output.sort(key=lambda x: x['label'])

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Banco gerado com {len(output)} exercícios.")
    print(f"ℹ️  Modo Apenas BR: {USE_ONLY_BR}")

if __name__ == "__main__":
    files = get_sorted_files()
    if not files:
        print("❌ Nenhum arquivo encontrado.")
    else:
        raw_map = parse_files(files)
        clean_data = deduplicate_and_clean(raw_map)
        save_json(clean_data)