# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
from garminconnect import Garmin
from dotenv import load_dotenv
import traceback

# --- 1. Configurações de Caminhos ---
# BASE_DIR é a pasta 'src'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR é a pasta raiz do projeto
ROOT_DIR = os.path.dirname(BASE_DIR)

# Caminho corrigido conforme solicitado: /data/raw/treino_manual.csv
CSV_FILE = os.path.join(ROOT_DIR, 'data', 'raw', 'treino_manual.csv')
DB_FILE = os.path.join(ROOT_DIR, 'data', 'processed', 'exercises.json')
ENV_PATH = os.path.join(ROOT_DIR, '.env')

load_dotenv(ENV_PATH)

# --- 2. Funções Auxiliares ---

def get_garmin_client():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        raise ValueError("❌ Credenciais não encontradas no .env")
    
    try:
        print(f"🔐 Autenticando {email}...")
        client = Garmin(email, password)
        client.login()
        return client
    except Exception as e:
        raise ConnectionError(f"❌ Erro ao conectar na Garmin: {e}")

def load_exercise_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {item['id']: item for item in data}
    except FileNotFoundError:
        print(f"⚠️  Aviso: {DB_FILE} não encontrado. Categorias serão inferidas.")
        return {}

def generate_payload(workout_name, group_df, db_cache):
    workout_steps = []
    global_order_counter = 1
    
    # Itera sobre cada exercício do treino
    for i, (_, row) in enumerate(group_df.iterrows()):
        
        # Dados do CSV
        ex_id = str(row['exercicio']).strip()
        nota = str(row['nota_personalizada']).strip() if pd.notna(row['nota_personalizada']) else ""
        
        # Garante valores numéricos seguros
        try:
            series = int(float(row['series'])) # float->int para garantir caso venha 3.0
            reps = int(float(row['reps']))
            peso = float(row['peso_kg'])
            descanso = int(float(row['intervalo_segundos']))
        except ValueError:
            print(f"⚠️ Erro de formato na linha {i}. Usando padrões.")
            series, reps, peso, descanso = 1, 10, 0, 60

        # Busca detalhes técnicos
        if ex_id in db_cache:
            category = db_cache[ex_id]['category']
            internal_name = db_cache[ex_id]['internal_key']
        else:
            # Fallback (tenta extrair do ID se não achar no banco)
            parts = ex_id.split('_', 1)
            category = parts[0] if len(parts) > 1 else ex_id
            internal_name = parts[1] if len(parts) > 1 else ex_id

        # Limpeza de categorias inválidas
        if category in ['UNCATEGORIZED', 'NOT_FOUND', 'nan']:
            category = None
            internal_name = None

        child_id = i + 1
        final_reps = reps if reps > 0 else 1

        # --- Passo de Exercício ---
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
            exercise_step["weightUnit"] = { "unitKey": "kilogram" }

        # --- Passo de Descanso ---
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

        # --- Agrupamento (Séries) ---
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

    # Payload Final
    return {
        "workoutName": workout_name,
        "sportType": { "sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5 },
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": { "sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5 },
            "workoutSteps": workout_steps
        }]
    }

# --- 3. Execução Principal ---

def main():
    print(f"📂 Buscando arquivo em: {CSV_FILE}")
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ Erro: Arquivo não encontrado!")
        print(f"   Certifique-se de salvar o CSV em: garmin_studio/data/raw/treino_manual.csv")
        return

    # Carrega dados
    db_cache = load_exercise_db()
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return
    
    # Verifica coluna obrigatória
    if 'treino' not in df.columns:
        print("❌ Erro: O CSV precisa ter uma coluna chamada 'treino' para agrupar os exercícios.")
        print(f"   Colunas encontradas: {list(df.columns)}")
        return

    treinos_unicos = df['treino'].unique()
    print(f"✅ CSV carregado. {len(treinos_unicos)} treinos identificados: {treinos_unicos}")

    client = get_garmin_client()

    for nome_treino in treinos_unicos:
        print(f"\n⚙️  Processando: {nome_treino}...")
        
        # Filtra apenas as linhas desse treino
        treino_df = df[df['treino'] == nome_treino]
        
        try:
            payload = generate_payload(nome_treino, treino_df, db_cache)
            
            print(f"📤 Enviando para Garmin Connect...")
            # Envio usando connectapi (método seguro)
            response = client.connectapi(
                "/workout-service/workout",
                method="POST",
                json=payload
            )
            
            print(f"✅ SUCESSO! Treino '{nome_treino}' criado.")
            
        except Exception as e:
            print(f"❌ Falha ao enviar '{nome_treino}': {e}")
            # traceback.print_exc() # Descomente para ver detalhes do erro se falhar

if __name__ == "__main__":
    main()