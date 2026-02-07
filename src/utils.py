import os
import unicodedata
import sys
import pandas as pd
from garminconnect import Garmin

# Adiciona o diretório atual ao path para importar o exercise_db corretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa o dicionário do arquivo separado
from exercise_db import EXERCISE_DB

def authenticate_garmin():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        raise ValueError("❌ Credenciais ausentes no .env")
    try:
        client = Garmin(email, password)
        client.login()
        print(f"✅ Autenticado como: {client.display_name}")
        return client
    except Exception as e:
        raise ConnectionError(f"❌ Falha auth: {e}")

def sanitize_text(text):
    if not isinstance(text, str): return str(text)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.strip().upper()

def get_exercise_data(name):
    name_clean = sanitize_text(name).lower()
    for key, data in EXERCISE_DB.items():
        if key in name_clean:
            return data
    return {"cat": "CARRY", "name": "CARRY"}

def generate_workout_payload(workout_name, df):
    workout_steps = []
    global_order_counter = 1

    df = df.fillna(0)
    
    for i, row in df.iterrows():
        raw_nota = str(row['nota_personalizada']).strip()
        nota_limpa = sanitize_text(raw_nota) 
        if not nota_limpa or nota_limpa == "0": nota_limpa = "EXERCICIO"
        
        series = int(row['series'])
        reps = int(row['reps'])
        peso = float(row['peso_kg'])
        descanso = int(row['intervalo_segundos'])
        
        child_id = i + 1
        ex_data = get_exercise_data(raw_nota)
        final_reps = reps if reps > 0 else 1

        # --- Passo de Exercício ---
        exercise_step = {
            "type": "ExecutableStepDTO",
            "stepId": None,
            "stepOrder": None, 
            "childStepId": child_id, 
            "description": nota_limpa,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "category": ex_data["cat"],       
            "exerciseName": ex_data["name"],  
            "endCondition": {"conditionTypeId": 10, "conditionTypeKey": "reps", "displayOrder": 10},
            "endConditionValue": final_reps,
            "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
        }

        if peso > 0:
            exercise_step["weightValue"] = peso
            exercise_step["weightUnit"] = {"unitKey": "kilogram"} 

        # --- Passo de Descanso ---
        rest_step = None
        if descanso > 0:
            rest_step = {
                "type": "ExecutableStepDTO",
                "stepId": None,
                "stepOrder": None,
                "childStepId": child_id,
                
                # AQUI ESTÁ A ALTERAÇÃO SOLICITADA:
                # Inclui a string (ex: "60s") no campo de observação
                "description": f"{descanso}s",
                
                "stepType": {"stepTypeId": 5, "stepTypeKey": "rest", "displayOrder": 5},
                # Mantemos "time" para o relógio vibrar sozinho, mas com a obs visual
                "endCondition": {"conditionTypeId": 1, "conditionTypeKey": "time", "displayOrder": 1},
                "endConditionValue": descanso,
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
            }

        # --- Bloco (Grupo) ---
        block_steps = []
        if series > 1:
            group_order = global_order_counter
            global_order_counter += 1
            
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
                "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
                "childStepId": child_id,
                "numberOfIterations": series,
                "smartRepeat": False,
                "endCondition": {"conditionTypeId": 7, "conditionTypeKey": "iterations"},
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

    return {
        "workoutName": workout_name,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
            "workoutSteps": workout_steps
        }]
    }