# -*- coding: utf-8 -*-
import os
import json
import traceback
import pandas as pd
import unicodedata
from flask import Flask, render_template, request, jsonify
from garminconnect import Garmin
from dotenv import load_dotenv

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

ENV_PATH = os.path.join(ROOT_DIR, '.env')
DB_FILE = os.path.join(ROOT_DIR, 'data', 'processed', 'exercises.json')
SEARCH_RULES_FILE = os.path.join(ROOT_DIR, 'data', 'config', 'search_rules.json')

load_dotenv(ENV_PATH)
app = Flask(__name__)

# Caches globais
EXERCISE_CACHE = {}         
INTERNAL_KEY_MAP = {}       
SEARCH_RULES_CACHE = {}
garmin_client = None

# --- FUNÇÕES AUXILIARES ---

def normalize_text(text):
    if not isinstance(text, str): return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

def load_data():
    """Carrega dados e cria índices para busca rápida"""
    global EXERCISE_CACHE, SEARCH_RULES_CACHE, INTERNAL_KEY_MAP
    
    if not EXERCISE_CACHE:
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    EXERCISE_CACHE = {item['id']: item for item in data}
                    INTERNAL_KEY_MAP = {item.get('internal_key'): item['id'] for item in data if 'internal_key' in item}
                    print(f"📦 DB Carregado: {len(EXERCISE_CACHE)} itens.")
            else:
                print(f"❌ DB não encontrado em: {DB_FILE}")
        except Exception as e:
            print(f"❌ Erro ao carregar DB: {e}")

    try:
        if os.path.exists(SEARCH_RULES_FILE):
            with open(SEARCH_RULES_FILE, 'r', encoding='utf-8') as f:
                SEARCH_RULES_CACHE = json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar regras: {e}")
        SEARCH_RULES_CACHE = {}

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

def resolve_exercise_label(category, internal_name):
    if not category or not internal_name: return None, internal_name
    cat_upper = str(category).upper()
    name_upper = str(internal_name).upper()

    composite_id = f"{cat_upper}_{name_upper}"
    if composite_id in EXERCISE_CACHE:
        return composite_id, EXERCISE_CACHE[composite_id]['label']
    
    if name_upper in INTERNAL_KEY_MAP:
        real_id = INTERNAL_KEY_MAP[name_upper]
        return real_id, EXERCISE_CACHE[real_id]['label']
    
    if name_upper in EXERCISE_CACHE:
        return name_upper, EXERCISE_CACHE[name_upper]['label']

    return None, internal_name 

def find_exercise_id(query):
    if not query: return None, ""
    query_norm = normalize_text(query)
    
    if "_" in query and query.isupper() and query in EXERCISE_CACHE:
        return query, EXERCISE_CACHE[query]['label']

    search_phrases = set()
    search_phrases.add(query_norm)
    for rule_key, synonyms in SEARCH_RULES_CACHE.items():
        norm_key = normalize_text(rule_key)
        norm_synonyms = [normalize_text(s) for s in synonyms]
        if query_norm in norm_key or any(query_norm in s for s in norm_synonyms):
            search_phrases.add(norm_key)
            for s in norm_synonyms: search_phrases.add(s)

    best_match = None
    best_score = 0
    for ex_id, ex_data in EXERCISE_CACHE.items():
        db_text = normalize_text((ex_data.get('search_term', '') or '') + " " + ex_data['label'])
        for phrase in search_phrases:
            if phrase in db_text:
                score = len(phrase)
                if db_text.startswith(phrase): score += 50
                len_diff = len(db_text) - len(phrase)
                score -= (len_diff * 0.1)
                if score > best_score:
                    best_score = score
                    best_match = ex_data

    if best_match and best_score > 3:
        return best_match['id'], best_match['label']
    return None, ""

# --- ROTAS ---

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

# --- CORREÇÃO AQUI: Importação CSV Completa ---
@app.route('/api/import_csv', methods=['POST'])
def api_import_csv():
    try:
        if 'file' not in request.files: return jsonify({"error": "Nenhum arquivo"}), 400
        file = request.files['file']
        
        # Lê CSV
        df = pd.read_csv(file)
        # Normaliza colunas
        df.columns = [c.lower().strip() for c in df.columns]
        load_data()
        
        imported_rows = []
        for _, row in df.iterrows():
            # Limpeza segura de NaNs (Not a Number) que o Pandas gera
            def clean_val(val):
                s = str(val).strip()
                return "" if s.lower() == 'nan' else s

            nota = clean_val(row.get('nota_personalizada', ''))
            col_ex = clean_val(row.get('exercicio', ''))
            
            # Prioridade: Coluna Exercício > Nota Personalizada
            search_term = col_ex if col_ex else nota
            
            # Tenta encontrar ID
            found_id = None
            found_label = ""
            if search_term:
                found_id, found_label = find_exercise_id(search_term)

            # Valores numéricos com fallback seguro para zero/padrão
            def get_num(key, default):
                try:
                    val = row.get(key)
                    if pd.isna(val) or str(val).strip() == '': return default
                    return float(val)
                except: return default

            imported_rows.append({
                "workoutName": clean_val(row.get('treino', 'Treino Importado')),
                "exerciseId": found_id, 
                "exerciseLabel": found_label if found_id else "",
                "exerciseSearch": found_label if found_id else search_term, 
                "note": nota, 
                "sets": int(get_num('series', 3)),
                "reps": int(get_num('reps', 10)),
                "weight": get_num('peso_kg', 0),
                "rest": int(get_num('intervalo_segundos', 60))
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
            
            category = "STRENGTH_EQUIPMENT"
            internal_name = "UNIDENTIFIED"
            
            if ex_data:
                category = ex_data.get("category", "STRENGTH_EQUIPMENT")
                internal_name = ex_data.get("internal_key", ex_id)
            elif ex_id:
                parts = ex_id.split('_', 1)
                if len(parts) > 1:
                    category, internal_name = parts[0], parts[1]

            series = int(step.get('sets', 1))
            reps = int(step.get('reps', 10))
            peso = float(step.get('weight', 0) or 0)
            descanso = int(step.get('restDuration', 0) or step.get('rest', 0) or 0)
            nota = step.get('note', '')

            child_id = i + 1 
            final_reps = reps if reps > 0 else 1

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

            if series > 1:
                group_order = global_order_counter
                global_order_counter += 1
                block_steps = [exercise_step]
                exercise_step["stepOrder"] = global_order_counter
                global_order_counter += 1
                
                if rest_step:
                    rest_step["stepOrder"] = global_order_counter
                    block_steps.append(rest_step)
                    global_order_counter += 1
                
                workout_steps.append({
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
                })
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
        response = client.connectapi("/workout-service/workout", method="POST", json=final_payload)
        return jsonify({ "success": True, "message": "Treino criado!", "id": response.get('workoutId') })

    except Exception as e:
        if "400" in str(e) and 'final_payload' in locals():
            print("\n❌ ERRO 400 - DUMP:\n", json.dumps(final_payload, indent=2))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/pull_workouts', methods=['GET'])
def api_pull_workouts():
    try:
        load_data()
        client = get_garmin_client()
        if not client: return jsonify({"error": "Erro de Autenticação"}), 500

        workouts = client.get_workouts()
        full_data = []
        
        count = 0
        for w_summary in workouts:
            if count > 20: break 
            
            w_id = w_summary['workoutId']
            w_name = w_summary['workoutName']
            
            if w_summary.get('sportType', {}).get('sportTypeKey') != 'strength_training':
                continue

            try:
                w_data = client.connectapi(f"/workout-service/workout/{w_id}", method="GET")
                steps = w_data.get('workoutSegments', [{}])[0].get('workoutSteps', [])
                
                i = 0
                while i < len(steps):
                    step = steps[i]
                    
                    # Grupo
                    if step['type'] == 'RepeatGroupDTO':
                        iterations = step.get('numberOfIterations', 1)
                        sub_steps = step.get('workoutSteps', [])
                        
                        ex_step = next((s for s in sub_steps if s.get('stepType', {}).get('stepTypeKey') == 'interval'), None)
                        rest_step = next((s for s in sub_steps if s.get('stepType', {}).get('stepTypeKey') in ['rest', 'recovery']), None)
                        
                        if ex_step:
                            cat = ex_step.get('category')
                            name = ex_step.get('exerciseName')
                            found_id, found_label = resolve_exercise_label(cat, name)
                            
                            full_data.append({
                                "workoutName": w_name,
                                "exerciseId": found_id,
                                "exerciseLabel": found_label,
                                "exerciseSearch": found_label,
                                "note": ex_step.get('description', ''),
                                "sets": iterations,
                                "reps": ex_step.get('endConditionValue', 0),
                                "weight": ex_step.get('weightValue', 0),
                                "rest": rest_step.get('endConditionValue', 0) if rest_step else 0
                            })
                    
                    # Passo Simples
                    elif step['type'] == 'ExecutableStepDTO' and step.get('stepType', {}).get('stepTypeKey') == 'interval':
                         cat = step.get('category')
                         name = step.get('exerciseName')
                         found_id, found_label = resolve_exercise_label(cat, name)
                         
                         rest_val = 0
                         if i + 1 < len(steps):
                             next_step = steps[i+1]
                             if next_step['type'] == 'ExecutableStepDTO' and next_step.get('stepType', {}).get('stepTypeKey') in ['rest', 'recovery']:
                                 rest_val = next_step.get('endConditionValue', 0)
                                 i += 1 

                         full_data.append({
                            "workoutName": w_name,
                            "exerciseId": found_id,
                            "exerciseLabel": found_label,
                            "exerciseSearch": found_label,
                            "note": step.get('description', ''),
                            "sets": 1,
                            "reps": step.get('endConditionValue', 0),
                            "weight": step.get('weightValue', 0),
                            "rest": rest_val 
                        })
                    
                    i += 1 
                
                count += 1
            except Exception as e:
                print(f"Erro ao processar treino {w_name}: {e}")
                continue

        return jsonify(full_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/list_workouts', methods=['POST'])
def api_list_workouts():
    try:
        data = request.json
        filter_type, filter_text = data.get('filterType'), data.get('filterText', '').lower().strip()
        client = get_garmin_client()
        if not client: return jsonify({"error": "Auth Error"}), 500

        workouts = client.get_workouts()
        filtered = []
        for w in workouts:
            name = w['workoutName'].lower()
            match = False
            if filter_type == 'all': match = True
            elif filter_type == 'starts_with': match = name.startswith(filter_text)
            elif filter_type == 'ends_with': match = name.endswith(filter_text)
            elif filter_type == 'contains': match = filter_text in name
            
            if match:
                filtered.append({"id": w['workoutId'], "name": w['workoutName'], "sport": w.get('sportType', {}).get('sportTypeKey')})
        return jsonify(filtered)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/delete_workouts', methods=['POST'])
def api_delete_workouts():
    try:
        ids = request.json.get('ids', [])
        client = get_garmin_client()
        deleted = 0
        for w_id in ids:
            try: client.connectapi(f"/workout-service/workout/{w_id}", method="DELETE"); deleted+=1
            except: pass
        return jsonify({"success": True, "deleted": deleted})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_data()
    app.run(debug=True)