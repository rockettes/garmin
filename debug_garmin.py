import os
import time
import json
import unicodedata
from garminconnect import Garmin
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv()

def authenticate():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        print("❌ Configure credenciais no .env")
        exit()
    try:
        client = Garmin(email, password)
        client.login()
        print(f"🔐 Logado como: {client.display_name}")
        return client
    except Exception as e:
        print(f"❌ Erro Auth: {e}")
        exit()

def send_test_payload(client, test_id, description, category, ex_name, weight, note_text):
    """Envia um payload unitário para testar uma combinação específica."""
    
    # Monta objeto de peso (se > 0)
    weight_obj = {}
    if weight is not None and weight > 0:
        weight_obj = {
            "weightValue": weight,
            "weightUnit": {"unitKey": "kilogram"}
        }

    # Payload Minimalista (Estrutura Web Validada)
    payload = {
        "workoutName": f"DBG_{test_id}",
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
            "workoutSteps": [{
                "type": "ExecutableStepDTO",
                "stepId": None,
                "stepOrder": 1,
                "childStepId": 1,
                "description": note_text, # Testando acentuação aqui
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                
                # AS VARIÁVEIS CRÍTICAS:
                "category": category, 
                "exerciseName": ex_name,
                
                "endCondition": {"conditionTypeId": 10, "conditionTypeKey": "reps"},
                "endConditionValue": 10,
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"},
                **weight_obj
            }]
        }]
    }

    try:
        client.connectapi("/workout-service/workout", method="POST", json=payload)
        return True, "200 OK"
    except Exception as e:
        msg = str(e)
        if "400" in msg: return False, "400 Bad Request"
        if "500" in msg: return False, "500 Server Error"
        return False, f"Erro: {msg}"

def run_exhaustive_suite():
    client = authenticate()
    
    # --- SEUS DADOS REAIS DO CSV PARA TESTE ---
    # Vamos testar variações de Chave, Peso e Texto para cada item.
    
    tests = [
        # 1. AGACHAMENTO SUMO (30kg)
        {"id": "01_A", "cat": "SQUAT", "key": "SQUAT", "w": 30, "txt": "AGACHAMENTO SUMO", "desc": "Base: SQUAT"},
        
        # 2. ELEVACAO PELVICA (20kg) - Onde costuma dar erro
        {"id": "02_A", "cat": "HIP_RAISE", "key": "HIP_RAISE", "w": 20, "txt": "ELEVACAO PELVICA", "desc": "Tenta HIP_RAISE"},
        {"id": "02_B", "cat": "HIP_THRUST", "key": "HIP_THRUST", "w": 20, "txt": "ELEVACAO PELVICA", "desc": "Tenta HIP_THRUST"},
        {"id": "02_C", "cat": "BRIDGE", "key": "BRIDGE", "w": 20, "txt": "ELEVACAO PELVICA", "desc": "Tenta BRIDGE"},
        {"id": "02_D", "cat": "HIP_RAISE", "key": "HIP_RAISE", "w": 20, "txt": "ELEVACAO PELVICA", "desc": "Tenta HIP_RAISE (Repete)"},

        # 3. BULGARO (Peso 0) - Teste de peso zero
        {"id": "03_A", "cat": "SQUAT", "key": "SQUAT", "w": 0, "txt": "AGACHAMENTO BULGARO", "desc": "Peso Zero (Int)"},
        {"id": "03_B", "cat": "SQUAT", "key": "SQUAT", "w": None, "txt": "AGACHAMENTO BULGARO", "desc": "Peso None (Bodyweight)"},

        # 4. FLEXORA EM PÉ (12.5kg) - Teste de Acento e Decimal
        {"id": "04_A", "cat": "LEG_CURL", "key": "LEG_CURL", "w": 12.5, "txt": "FLEXORA EM PÉ", "desc": "Acento + Decimal"},
        {"id": "04_B", "cat": "LEG_CURL", "key": "LEG_CURL", "w": 12.5, "txt": "FLEXORA EM PE", "desc": "Sem Acento + Decimal"},
        {"id": "04_C", "cat": "LEG_CURL", "key": "LEG_CURL", "w": 12, "txt": "FLEXORA EM PE", "desc": "Sem Acento + Inteiro"},

        # 5. CADEIRA FLEXORA (51kg)
        {"id": "05_A", "cat": "LEG_CURL", "key": "LEG_CURL", "w": 51, "txt": "CADEIRA FLEXORA", "desc": "Base: LEG_CURL"},

        # 6. MESA FLEXORA (38kg)
        {"id": "06_A", "cat": "LEG_CURL", "key": "LEG_CURL", "w": 38, "txt": "MESA FLEXORA", "desc": "Base: LEG_CURL"},

        # 7. EXTENSORA (30kg) - O Grande Vilão
        {"id": "07_A", "cat": "LEG_EXTENSION", "key": "LEG_EXTENSION", "w": 30, "txt": "CADEIRA EXTENSORA", "desc": "Tenta LEG_EXTENSION (Falhou antes)"},
        {"id": "07_B", "cat": "LEG_PRESS", "key": "LEG_PRESS", "w": 30, "txt": "CADEIRA EXTENSORA", "desc": "Fallback Seguro: LEG_PRESS"},
        {"id": "07_C", "cat": "SQUAT", "key": "SQUAT", "w": 30, "txt": "CADEIRA EXTENSORA", "desc": "Fallback Ultimate: SQUAT"},

        # 8. GEMEOS (50kg)
        {"id": "08_A", "cat": "CALF_RAISE", "key": "CALF_RAISE", "w": 50, "txt": "GEMEOS", "desc": "Tenta CALF_RAISE"},
        {"id": "08_B", "cat": "CALF_PRESS", "key": "CALF_PRESS", "w": 50, "txt": "GEMEOS", "desc": "Tenta CALF_PRESS"},
    ]

    print(f"\n🧪 INICIANDO BATERIA DE {len(tests)} TESTES")
    print("="*80)
    print(f"{'ID':<6} | {'STATUS':<10} | {'EXERCICIO (KEY)':<25} | {'DETALHE'}")
    print("-" * 80)
    
    results = []

    for t in tests:
        success, msg = send_test_payload(client, t['id'], t['txt'], t['cat'], t['key'], t['w'], t['txt'])
        
        status_icon = "✅ PASS" if success else "❌ FAIL"
        print(f"{t['id']:<6} | {status_icon:<10} | {t['key']:<25} | {t['desc']} -> {msg}")
        
        results.append((t['id'], success, t['key'], msg))
        time.sleep(1.5) # Pausa de segurança

    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL")
    print("="*80)
    
    failures = [r for r in results if not r[1]]
    if not failures:
        print("🎉 TODOS OS TESTES PASSARAM! O problema foi resolvido.")
    else:
        print(f"⚠️ {len(failures)} FALHAS ENCONTRADAS:")
        for f in failures:
            print(f"   -> {f[0]} ({f[2]}): {f[3]}")
            
    print("\n💡 AÇÃO SUGERIDA:")
    if any(r[0] == "04_A" and not r[1] for r in results) and any(r[0] == "04_B" and r[1] for r in results):
        print("   -> O problema são os ACENTOS ('PÉ'). Use sanitização.")
    if any(r[0] == "04_B" and not r[1] for r in results) and any(r[0] == "04_C" and r[1] for r in results):
        print("   -> O problema são PESOS DECIMAIS (12.5). Arredonde para int.")
    if any(r[0] == "07_A" and not r[1] for r in results) and any(r[0] == "07_B" and r[1] for r in results):
        print("   -> 'LEG_EXTENSION' é inválido. Mapeie Extensora para 'LEG_PRESS'.")

if __name__ == "__main__":
    run_exhaustive_suite()