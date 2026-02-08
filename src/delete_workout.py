import os
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        print("❌ Credenciais ausentes.")
        exit()
    try:
        client = Garmin(email, password)
        client.login()
        return client
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        exit()

def cleanup_debug_workouts():
    client = authenticate()
    print("🔐 Logado. Buscando treinos 'DBG_'...")

    try:
        # Tenta usar o método nativo da lib para LISTAR (mais seguro que chutar a URL)
        # Se sua lib for muito antiga, isso pode falhar, aí tentamos o plano B.
        if hasattr(client, 'get_workouts'):
            workouts_list = client.get_workouts()
        else:
            # Fallback manual para o endpoint PLURAL (o anterior falhou por ser singular)
            print("⚠️ Método get_workouts não encontrado, tentando via API bruta...")
            workouts_list = client.connectapi("/workout-service/workouts", method="GET")
            
    except Exception as e:
        print(f"❌ Erro ao buscar lista de treinos: {e}")
        return

    # Filtra apenas os que começam com "DBG_"
    # Nota: A estrutura do retorno pode variar, garantimos que é uma lista de dicts
    targets = []
    if isinstance(workouts_list, list):
        for w in workouts_list:
            if isinstance(w, dict) and w.get('workoutName', '').startswith("DBG_"):
                targets.append(w)

    if not targets:
        print("✅ Nenhum treino de debug encontrado (ou lista vazia).")
        return

    print(f"⚠️ Encontrados {len(targets)} treinos de debug. Iniciando limpeza...")

    # Deleta um por um usando a rota DELETE no singular com ID
    for w in targets:
        w_id = w['workoutId']
        w_name = w['workoutName']
        
        print(f"🗑️ Deletando: {w_name} (ID: {w_id})...", end=" ")
        
        try:
            # AQUI ESTAVA O SEGREDO: Rota singular + ID na URL + Método DELETE
            client.connectapi(f"/workout-service/workout/{w_id}", method="DELETE")
            print("✅ Sucesso")
        except Exception as e:
            print(f"❌ Falha: {e}")

    print("\n🧹 Limpeza concluída!")

if __name__ == "__main__":
    cleanup_debug_workouts()