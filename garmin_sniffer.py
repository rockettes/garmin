import time
import json
import os
import undetected_chromedriver as uc

def main():
    print("🕵️  SNIFFER DEBUG LIGADO (Versão Travada no Chrome 144)")
    print("----------------------------------------------------------------------")
    print("1. O Chrome vai abrir.")
    print("2. Clique no Cloudflare se aparecer.")
    print("3. Logue e vá criar o treino.")
    print("4. Digite 'Supino' e veja o terminal.")
    print("----------------------------------------------------------------------")

    options = uc.ChromeOptions()
    # Habilita logs de performance de rede
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # --- A CORREÇÃO ESTÁ AQUI ---
    # version_main=144 obriga o script a baixar o driver compatível com seu navegador atual
    driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)

    try:
        driver.get("https://connect.garmin.com/signin")
        
        while True:
            # Pega TODOS os logs
            try:
                logs = driver.get_log("performance")
            except Exception:
                time.sleep(1)
                continue
            
            for entry in logs:
                try:
                    obj = json.loads(entry["message"])
                    message = obj.get("message", {})
                    method = message.get("method")

                    # Se for uma resposta de rede...
                    if method == "Network.responseReceived":
                        url = message["params"]["response"]["url"]
                        
                        # Filtro: Apenas URLs da API da Garmin
                        if "connectapi.garmin.com" in url:
                            # Se parecer com exercício ou dicionário, tenta ler o corpo
                            if "exercise" in url or "workout-service" in url or "dictionary" in url:
                                print(f"📡 Capturado (Potencial): {url[:100]}...")
                                
                                request_id = message["params"]["requestId"]
                                try:
                                    response_body = driver.execute_cdp_cmd(
                                        "Network.getResponseBody", 
                                        {"requestId": request_id}
                                    )
                                    body = response_body.get('body', '')
                                    
                                    # Tenta ler o JSON para ver se tem exercício dentro
                                    data = json.loads(body)
                                    
                                    # Normaliza lista
                                    items = []
                                    if isinstance(data, list):
                                        items = data
                                    elif isinstance(data, dict) and 'dictionary' in data:
                                        items = data['dictionary']
                                        
                                    # Imprime o que achou
                                    for item in items:
                                        if isinstance(item, dict) and 'exerciseName' in item:
                                            nome = item.get('name') or item.get('display_name')
                                            chave = item.get('exerciseName')
                                            cat = item.get('category')
                                            cat_key = cat.get('typeKey') if isinstance(cat, dict) else cat
                                            
                                            print(f"🔥 ACHOU: {nome} -> Cat: {cat_key} | Ex: {chave}")

                                except Exception as e:
                                    # print(f"   (Não foi possível ler o corpo deste request)")
                                    pass

                except Exception:
                    pass
            
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Debug encerrado.")
        try:
            driver.quit()
        except:
            pass
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()