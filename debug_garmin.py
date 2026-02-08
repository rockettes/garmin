import os
import time
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

def run_visual_test():
    client = authenticate()
    client.login()
    print(f"🔐 Logado. Criando treino 'TESTE_EXTENSORA_V2'...")

    # Apenas combinações que deram "PASS" no debug anterior.
    # Queremos ver qual delas ganha o nome correto na tela.
    candidates = [
        # 1. Categoria SQUAT + Chave genérica
        {"cat": "SQUAT", "name": "LEG_EXTENSION", "desc": "1. SQUAT / LEG_EXTENSION"},
        
        # 2. Categoria SQUAT + Chave técnica (Joelhos)
        {"cat": "SQUAT", "name": "KNEE_EXTENSION", "desc": "2. SQUAT / KNEE_EXTENSION"},
        
        # 3. Categoria SQUAT + Chave específica (Sentado) -> (Essa deu 'Agachamento' antes?)
        {"cat": "SQUAT", "name": "SEATED_LEG_EXTENSION", "desc": "3. SQUAT / SEATED_LEG_EXTENSION"},
        
        # 4. Categoria FLEXORA + Chave técnica (Será que vira Extensão?)
        {"cat": "LEG_CURL", "name": "KNEE_EXTENSION", "desc": "4. LEG_CURL / KNEE_EXTENSION"},
        
        # 5. Categoria PANTURRILHA (O azarão)
        {"cat": "CALF_RAISE", "name": "LEG_EXTENSION", "desc": "5. CALF_RAISE / LEG_EXTENSION"},
    ]

    steps = []
    for i, c in enumerate(candidates):
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": i + 1,
            "description": c['desc'],
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
            "category": c['cat'], 
            "exerciseName": c['name'],
            "endCondition": {"conditionTypeId": 10, "conditionTypeKey": "reps"},
            "endConditionValue": 10
        })

    timestamp = int(time.time())
    payload = {
        "workoutName": f"TESTE_EXTENSORA_V2_{timestamp}",
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
            "workoutSteps": steps
        }]
    }

    try:
        client.connectapi("/workout-service/workout", method="POST", json=payload)
        print("\n✅ Treino criado! Sincronize o relógio/app.")
        print("👀 Abra o treino e veja os nomes dos 5 exercícios.")
        print("-" * 40)
        for c in candidates:
            print(f"  {c['desc']}")
        print("-" * 40)
        print("Me diga qual número (1 a 5) apareceu escrito 'Cadeira Extensora' ou 'Extensão'.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_visual_test()