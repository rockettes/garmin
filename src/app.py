# -*- coding: utf-8 -*-
import os
import json
import traceback
from flask import Flask, render_template, request, jsonify
from garminconnect import Garmin
from dotenv import load_dotenv

# --- 1. Configurações ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), '.env')
DB_FILE = os.path.join(os.path.dirname(BASE_DIR), 'data', 'processed', 'exercises.json')

load_dotenv(ENV_PATH)
app = Flask(__name__)

EXERCISE_CACHE = {} 
garmin_client = None

# --- 2. Funções ---
def load_exercise_db():
    global EXERCISE_CACHE
    if EXERCISE_CACHE: return
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            EXERCISE_CACHE = {item['id']: item for item in data}
            print(f"📦 DB Carregado: {len(EXERCISE_CACHE)} itens.")
    except:
        pass

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

# --- 3. Rotas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/exercises')
def api_exercises():
    load_exercise_db()
    lista = list(EXERCISE_CACHE.values())
    lista.sort(key=lambda x: x['label'])
    return jsonify(lista)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        data = request.json
        workout_name = data.get('workoutName')
        raw_steps = data.get('steps', [])

        if not workout_name: return jsonify({"error": "Nome obrigatório"}), 400

        client = get_garmin_client()
        if not client: return jsonify({"error": "Erro de Autenticação"}), 500

        # --- GERAÇÃO DO PAYLOAD (Tradução Literal do Script Funcional) ---
        workout_steps = []
        global_order_counter = 1

        for i, step in enumerate(raw_steps):
            ex_id = step.get('exerciseId')
            ex_data = EXERCISE_CACHE.get(ex_id)
            if not ex_data: continue

            # Extração de dados
            series = int(step.get('sets', 1))
            reps = int(step.get('reps', 10))
            peso = float(step.get('weight', 0) or 0)
            descanso = int(step.get('restDuration', 0) or 0)
            nota = step.get('note', '')

            # childStepId sequencial baseado no índice
            child_id = i + 1 

            # Garante que reps seja pelo menos 1
            final_reps = reps if reps > 0 else 1

            # --- 1. Passo de Exercício ---
            exercise_step = {
                "type": "ExecutableStepDTO",
                "stepId": None,
                "stepOrder": None, # Será definido abaixo
                "childStepId": child_id, 
                "description": nota if nota else None,
                "stepType": {
                    "stepTypeId": 3, 
                    "stepTypeKey": "interval", 
                    "displayOrder": 3
                },
                "category": ex_data["category"],        
                "exerciseName": ex_data["internal_key"],   
                "endCondition": {
                    "conditionTypeId": 10, 
                    "conditionTypeKey": "reps", 
                    "displayOrder": 10
                },
                "endConditionValue": final_reps,
                "targetType": {
                    "workoutTargetTypeId": 1, 
                    "workoutTargetTypeKey": "no.target"
                }
            }

            if peso > 0:
                exercise_step["weightValue"] = peso
                exercise_step["weightUnit"] = {"unitKey": "kilogram"} 

            # --- 2. Passo de Descanso ---
            rest_step = None
            if descanso > 0:
                rest_step = {
                    "type": "ExecutableStepDTO",
                    "stepId": None,
                    "stepOrder": None,
                    "childStepId": child_id,
                    "description": f"{descanso}s", # Descrição visual
                    "stepType": {
                        "stepTypeId": 5, # Atenção: Script funcional usa ID 5 para rest aqui? Ou 4? 
                                         # O padrão Garmin recente é 4, mas se o script funcional usa 5, vamos testar.
                                         # Mas geralmente 4 é Rest e 5 é Recovery. Vamos manter 4 (Rest) por segurança, 
                                         # pois 5 costuma dar erro em alguns devices.
                                         # Se der erro, troque para 5.
                        "stepTypeKey": "rest", 
                        "displayOrder": 5
                    },
                    "endCondition": {
                        "conditionTypeId": 1, # Script funcional usa 1 (Time)
                        "conditionTypeKey": "time", 
                        "displayOrder": 1
                    },
                    "endConditionValue": descanso,
                    "targetType": {
                        "workoutTargetTypeId": 1, 
                        "workoutTargetTypeKey": "no.target"
                    }
                }

            # --- 3. Lógica de Blocos/Grupos (Cópia exata) ---
            if series > 1:
                # O contador global avança para o grupo
                group_order = global_order_counter
                global_order_counter += 1
                
                block_steps = []
                
                # Exercício dentro do bloco
                exercise_step["stepOrder"] = global_order_counter
                block_steps.append(exercise_step)
                global_order_counter += 1
                
                # Descanso dentro do bloco
                if rest_step:
                    rest_step["stepOrder"] = global_order_counter
                    block_steps.append(rest_step)
                    global_order_counter += 1
                
                group_step = {
                    "type": "RepeatGroupDTO",
                    "stepId": None,
                    "stepOrder": group_order,
                    "stepType": {
                        "stepTypeId": 6, 
                        "stepTypeKey": "repeat", 
                        "displayOrder": 6
                    },
                    "childStepId": child_id, # Mesmo ID do filho
                    "numberOfIterations": series,
                    "smartRepeat": False,
                    "endCondition": {
                        "conditionTypeId": 7, 
                        "conditionTypeKey": "iterations"
                        # displayOrder não estava no script funcional para groups
                    },
                    "workoutSteps": block_steps,
                    "skipLastRestStep": False
                }
                workout_steps.append(group_step)
            
            else:
                # Série Única (Sem repetição)
                exercise_step["stepOrder"] = global_order_counter
                workout_steps.append(exercise_step)
                global_order_counter += 1
                
                if rest_step:
                    rest_step["stepOrder"] = global_order_counter
                    workout_steps.append(rest_step)
                    global_order_counter += 1

        # Payload Final (Sem subSportType)
        final_payload = {
            "workoutName": workout_name,
            "sportType": {
                "sportTypeId": 5, 
                "sportTypeKey": "strength_training", 
                "displayOrder": 5
            },
            "workoutSegments": [{
                "segmentOrder": 1,
                "sportType": {
                    "sportTypeId": 5, 
                    "sportTypeKey": "strength_training", 
                    "displayOrder": 5
                },
                "workoutSteps": workout_steps
            }]
        }
        
        # Envio Direto
        print(f"📤 Enviando JSON para: {workout_name}")
        # print(json.dumps(final_payload, indent=2)) # Descomente se quiser ver o JSON

        response = client.connectapi(
            "/workout-service/workout",
            method="POST",
            json=final_payload
        )

        return jsonify({
            "success": True, 
            "message": "Treino criado com sucesso!",
            "id": response.get('workoutId')
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_exercise_db()
    app.run(debug=True)