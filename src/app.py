# -*- coding: utf-8 -*-
import os
import json
import traceback
import pandas as pd
import unicodedata
from flask import Flask, render_template, request, jsonify
from garminconnect import Garmin
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

ENV_PATH = os.path.join(ROOT_DIR, '.env')
DB_FILE = os.path.join(ROOT_DIR, 'data', 'processed', 'exercises.json')
SEARCH_RULES_FILE = os.path.join(ROOT_DIR, 'data', 'config', 'search_rules.json')

load_dotenv(ENV_PATH)
app = Flask(__name__)

EXERCISE_CACHE = {} 
SEARCH_RULES_CACHE = {}
garmin_client = None

def normalize_text(text):
    if not isinstance(text, str): return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

def load_data():
    global EXERCISE_CACHE, SEARCH_RULES_CACHE
    if not EXERCISE_CACHE:
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                EXERCISE_CACHE = {item['id']: item for item in data}
                print(f"📦 DB Carregado: {len(EXERCISE_CACHE)} itens.")
        except Exception as e:
            print(f"❌ Erro ao carregar DB: {e}")

    try:
        if os.path.exists(SEARCH_RULES_FILE):
            with open(SEARCH_RULES_FILE, 'r', encoding='utf-8') as f:
                SEARCH_RULES_CACHE = json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar regras: {e}")
        SEARCH_RULES_CACHE = {}

def find_exercise_id(query):
    if not query: return None, ""
    
    query_norm = normalize_text(query)
    
    # 1. ID Exato
    if "_" in query and query.isupper() and query in EXERCISE_CACHE:
        return query, EXERCISE_CACHE[query]['label']

    # 2. Expansão de Termos
    search_phrases = set()
    search_phrases.add(query_norm)

    for rule_key, synonyms in SEARCH_RULES_CACHE.items():
        norm_key = normalize_text(rule_key)
        norm_synonyms = [normalize_text(s) for s in synonyms]
        
        if query_norm in norm_key or any(query_norm in s for s in norm_synonyms):
            search_phrases.add(norm_key)
            for s in norm_synonyms:
                search_phrases.add(s)

    # 3. Varredura no Banco
    best_match = None
    best_score = 0

    for ex_id, ex_data in EXERCISE_CACHE.items():
        db_text = normalize_text(ex_data.get('search_term', '') + " " + ex_data['label'])
        
        for phrase in search_phrases:
            if phrase in db_text:
                score = len(phrase)
                if db_text.startswith(phrase):
                    score += 50
                len_diff = len(db_text) - len(phrase)
                score -= (len_diff * 0.1)

                if score > best_score:
                    best_score = score
                    best_match = ex_data

    if best_match and best_score > 3: 
        return best_match['id'], best_match['label']
    
    return None, ""

def get_garmin_client():
    global garmin_client
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if garmin_client:
        try:
            garmin_client.connectapi("/userprofile-service/userprofile/user-settings")
            return garmin_client
        except:
            garmin_client = None
    try:
        client = Garmin(email, password)
        client.login()
        garmin_client = client
        return garmin_client
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/exercises')
def api_exercises():
    load_data()
    lista = list(EXERCISE_CACHE.values())
    lista.sort(key=lambda x: x['label'])
    return jsonify(lista)
    
@app.route('/api/search_rules')
def api_search_rules():
    load_data()
    return jsonify(SEARCH_RULES_CACHE)

@app.route('/api/import_csv', methods=['POST'])
def api_import_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        df.columns = [c.lower().strip() for c in df.columns]
        load_data()
        
        imported_rows = []
        
        for _, row in df.iterrows():
            nota_original = str(row.get('nota_personalizada', '')).strip()
            if nota_original == 'nan': nota_original = ''
            
            col_exercicio = str(row.get('exercicio', '')).strip()
            if col_exercicio == 'nan': col_exercicio = ''

            # Prioridade: 'exercicio' se existir, senão 'nota'
            search_term = col_exercicio if col_exercicio else nota_original
            
            found_id = None
            found_label = ""
            
            if col_exercicio and "_" in col_exercicio and col_exercicio.isupper() and col_exercicio in EXERCISE_CACHE:
                found_id = col_exercicio
                found_label = EXERCISE_CACHE[col_exercicio]['label']
            else:
                if search_term:
                    found_id, found_label = find_exercise_id(search_term)

            imported_rows.append({
                "workoutName": str(row.get('treino', 'Treino Importado')),
                "exerciseId": found_id, 
                "exerciseLabel": found_label if found_id else "",
                "exerciseSearch": found_label if found_id else search_term, 
                "note": nota_original, 
                "sets": int(float(row.get('series', 3))),
                "reps": int(float(row.get('reps', 10))),
                "weight": float(row.get('peso_kg', 0)),
                "rest": int(float(row.get('intervalo_segundos', 60)))
            })

        return jsonify(imported_rows)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        data = request.json
        workout_name = data.get('workoutName')
        raw_steps = data.get('steps', [])

        if not workout_name: return jsonify({"error": "Nome obrigatório"}), 400

        load_data()
        client = get_garmin_client()
        if not client: return jsonify({"error": "Erro de Autenticação"}), 500

        workout_steps = []
        global_order_counter = 1

        for i, step in enumerate(raw_steps):
            ex_id = step.get('exerciseId')
            ex_data = EXERCISE_CACHE.get(ex_id)
            
            # Fallback
            category = "STRENGTH_EQUIPMENT"
            internal_name = "UNIDENTIFIED"
            
            if ex_data:
                category = ex_data.get("category", "STRENGTH_EQUIPMENT")
                internal_name = ex_data.get("internal_key", ex_id)
            elif ex_id:
                parts = ex_id.split('_', 1)
                if len(parts) > 1:
                    category = parts[0]
                    internal_name = parts[1]

            series = int(step.get('sets', 1))
            reps = int(step.get('reps', 10))
            peso = float(step.get('weight', 0) or 0)
            
            # CORREÇÃO: Lê 'restDuration' (frontend) ou 'rest' (csv import)
            descanso = int(step.get('restDuration', 0) or step.get('rest', 0) or 0)
            
            nota = step.get('note', '')

            child_id = i + 1 
            final_reps = reps if reps > 0 else 1

            # 1. Passo de Exercício
            exercise_step = {
                "type": "ExecutableStepDTO",
                "stepId": None,
                "stepOrder": None,
                "childStepId": child_id, 
                "description": nota if nota else None,
                "stepType": { "stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3 },
                "category": category,        
                "exerciseName": internal_name,   
                "endCondition": { "conditionTypeId": 10, "conditionTypeKey": "reps", "displayOrder": 10 },
                "endConditionValue": final_reps,
                "targetType": { "workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target" }
            }

            if peso > 0:
                exercise_step["weightValue"] = peso
                exercise_step["weightUnit"] = {"unitKey": "kilogram"} 

            # 2. Passo de Descanso
            rest_step = None
            if descanso > 0:
                rest_step = {
                    "type": "ExecutableStepDTO",
                    "stepId": None,
                    "stepOrder": None,
                    "childStepId": child_id,
                    "description": f"{descanso}s",
                    "stepType": { "stepTypeId": 4, "stepTypeKey": "rest", "displayOrder": 4 },
                    "endCondition": { "conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2 },
                    "endConditionValue": descanso,
                    "targetType": { "workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target" }
                }

            # 3. Montagem do Bloco
            if series > 1:
                group_order = global_order_counter
                global_order_counter += 1
                block_steps = []
                
                exercise_step["stepOrder"] = global_order_counter
                block_steps.append(exercise_step)
                global_order_counter += 1
                
                if rest_step:
                    rest_step["stepOrder"] = global_order_counter
                    block_steps.append(rest_step)
                    global_order_counter += 1
                
                group_step = {
                    "type": "RepeatGroupDTO",
                    "stepId": None,
                    "stepOrder": group_order,
                    "stepType": { "stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6 },
                    "childStepId": child_id,
                    "numberOfIterations": series,
                    "smartRepeat": False,
                    "endCondition": { "conditionTypeId": 7, "conditionTypeKey": "iterations", "displayOrder": 7 },
                    "workoutSteps": block_steps,
                    "skipLastRestStep": False
                }
                workout_steps.append(group_step)
            else:
                exercise_step["stepOrder"] = global_order_counter
                workout_steps.append(exercise_step)
                global_order_counter += 1
                if rest_step:
                    rest_step["stepOrder"] = global_order_counter
                    workout_steps.append(rest_step)
                    global_order_counter += 1

        final_payload = {
            "workoutName": workout_name,
            "sportType": { "sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5 },
            "workoutSegments": [{
                "segmentOrder": 1,
                "sportType": { "sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5 },
                "workoutSteps": workout_steps
            }]
        }
        
        print(f"📤 Tentando enviar: {workout_name}")

        try:
            response = client.connectapi("/workout-service/workout", method="POST", json=final_payload)
            return jsonify({ "success": True, "message": "Treino criado com sucesso!", "id": response.get('workoutId') })
        except Exception as api_error:
            # DEBUG: Imprime o JSON se der erro 400
            print("\n" + "="*50)
            print(f"❌ ERRO API GARMIN (400 Bad Request) no treino: {workout_name}")
            print("👇 DUMP DO PAYLOAD QUE CAUSOU O ERRO:")
            print(json.dumps(final_payload, indent=2))
            print("="*50 + "\n")
            raise api_error

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_data()
    app.run(debug=True)