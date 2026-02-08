import os
import argparse
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        print("❌ Credenciais ausentes no arquivo .env")
        exit()
    try:
        client = Garmin(email, password)
        client.login()
        return client
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        exit()

def get_all_workouts(client):
    """Busca a lista completa de treinos com fallback de método."""
    try:
        if hasattr(client, 'get_workouts'):
            return client.get_workouts()
        else:
            print("⚠️ Método get_workouts nativo não encontrado, usando API direta...")
            return client.connectapi("/workout-service/workouts", method="GET")
    except Exception as e:
        print(f"❌ Erro ao buscar lista de treinos: {e}")
        return []

def delete_workouts(filter_name=None, delete_all=False):
    if not filter_name and not delete_all:
        print("❌ Você precisa especificar um filtro (--filter) ou usar --all.")
        return

    client = authenticate()
    print("🔐 Logado. Buscando treinos...")

    workouts_list = get_all_workouts(client)
    
    if not isinstance(workouts_list, list):
        print("❌ Formato de resposta inválido da Garmin.")
        return

    # Lógica de Filtragem
    targets = []
    for w in workouts_list:
        if not isinstance(w, dict): continue
        
        w_name = w.get('workoutName', '')
        
        if delete_all:
            targets.append(w)
        elif filter_name and filter_name in w_name:
            # Verifica se o nome do treino CONTÉM o texto do filtro
            targets.append(w)

    if not targets:
        print("✅ Nenhum treino encontrado com os critérios fornecidos.")
        return

    print(f"\n⚠️  ATENÇÃO: Foram encontrados {len(targets)} treinos para deletar.")
    if delete_all:
        print(f"🚨 MODO DELETAR TUDO ATIVADO! Isso apagará TODOS os seus treinos.")
    else:
        print(f"🎯 Filtro aplicado: '{filter_name}'")
        # Lista os primeiros 5 nomes para o usuário conferir
        print("Exemplos que serão deletados:", [t['workoutName'] for t in targets[:5]])

    # Confirmação de Segurança
    confirm = input("\nTem certeza que deseja continuar? Digite 'SIM' para confirmar: ")
    if confirm != 'SIM':
        print("⛔ Operação cancelada.")
        return

    # Loop de Deleção
    print("\n🚀 Iniciando remoção...")
    count = 0
    for w in targets:
        w_id = w['workoutId']
        w_name = w['workoutName']
        
        print(f"[{count+1}/{len(targets)}] Deletando: {w_name} (ID: {w_id})...", end=" ")
        
        try:
            client.connectapi(f"/workout-service/workout/{w_id}", method="DELETE")
            print("✅ Sucesso")
            count += 1
        except Exception as e:
            print(f"❌ Falha: {e}")

    print(f"\n🧹 Limpeza concluída! {count} treinos removidos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para deletar treinos do Garmin Connect")
    
    # Argumento Opcional: Filtro por nome
    parser.add_argument("--filter", type=str, help="Texto que deve estar no nome do treino para ser deletado (ex: 'DBG_')")
    
    # Argumento Opcional: Deletar tudo
    parser.add_argument("--all", action="store_true", help="Deleta TODOS os treinos da conta")

    args = parser.parse_args()

    # Executa a função passando os argumentos
    delete_workouts(filter_name=args.filter, delete_all=args.all)
