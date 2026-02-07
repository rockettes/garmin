import os
import time
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        print("❌ Configure credenciais no .env")
        exit()
    try:
        return Garmin(email, password)
    except Exception as e:
        print(f"❌ Erro Auth: {e}")
        exit()

def test_key(client, test_name, category, exercise_name):
    """Tenta criar um treino com uma chave específica."""
    print(f"\n👉 Testando chave: '{exercise_name}' (Categoria: {category})")
    
    payload = {
        "workoutName": f"DBG_PECK_{test_name}",
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
            "workoutSteps": [{
                "type": "ExecutableStepDTO",
                "stepId": None,
                "stepOrder": 1,
                "childStepId": 1,
                "description": "Teste Peck Deck",
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                
                # VARIÁVEIS DE TESTE
                "category": category, 
                "exerciseName": exercise_name,
                
                "endCondition": {"conditionTypeId": 10, "conditionTypeKey": "reps"},
                "endConditionValue": 10,
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
            }]
        }]
    }

    try:
        client.login()
        client.connectapi("/workout-service/workout", method="POST", json=payload)
        print("   ✅ SUCESSO! A Garmin aceita este nome.")
        return True
    except Exception as e:
        if "400" in str(e):
            print("   ❌ FALHA (400). Nome inválido/rejeitado.")
        else:
            print(f"   ❌ ERRO: {str(e)}")
        return False

def run_peck_debug():
    client = authenticate()
    
    # LISTA DE CANDIDATOS PARA PECK DECK
    candidates = [
        {"id": "GENERIC", "cat": "FLY", "name": "FLY"},               # Genérico (Sabemos que funciona)
        {"id": "SPECIFIC_1", "cat": "FLY", "name": "PEC_DECK"},       # Nome provável
        {"id": "SPECIFIC_2", "cat": "FLY", "name": "MACHINE_FLY"},    # Outro nome comum
        {"id": "SPECIFIC_3", "cat": "FLY", "name": "PECTORAL_FLY"},   # Variação
        {"id": "SPECIFIC_4", "cat": "FLY", "name": "BUTTERFLY"},      # Nome antigo
        {"id": "CAT_TEST",   "cat": "PEC_DECK", "name": "PEC_DECK"},  # Testando se é categoria própria
    ]

    print("🕵️‍♂️ BUSCANDO O NOME DO PECK DECK...")
    print("="*60)

    for c in candidates:
        test_key(client, c['id'], c['cat'], c['name'])
        time.sleep(1.5)

if __name__ == "__main__":
    run_peck_debug()