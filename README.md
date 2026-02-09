# 💪 Garmin Studio: O Editor de Treinos para Quem Levanta Peso

> **"A Garmin é ótima para quem corre maratona. Para quem constrói shape, ela é um desastre. Nós consertamos isso."**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Garmin](https://img.shields.io/badge/Garmin-Hacked-black?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-ANABÓLICO-red?style=for-the-badge)

---

## 😡 O Problema
Você gasta 2 horas na academia destruindo as pernas, mas gasta **3 horas no computador** tentando montar o treino no Garmin Connect?

A interface da Garmin foi feita para *runners*. Cliques infinitos, menus escondidos, e uma lentidão absurda para adicionar uma simples série de Supino. Se você treina de verdade, **você não tem tempo para isso.**

## 🚀 A Solução: Garmin Studio
O **Garmin Studio** é a ferramenta definitiva para Bodybuilders, Powerlifters e entusiastas da musculação. Esqueça o mouse. Nós usamos dados.

* **Excel/CSV -> Relógio:** Monte seu treino no Excel em 2 minutos, importe e suba para o relógio.
* **Busca Inteligente:** Digite "Supino" e nós achamos o ID técnico bizarro da Garmin (`BENCH_PRESS_BARBELL_...`) para você.
* **Gestão em Massa:** Baixe seus treinos atuais, edite, duplique ou apague tudo com um clique.
* **Dark Mode Nativo:** Porque ninguém treina com luz branca na cara.

---

## ⚡ Funcionalidades (O "Pump")

1.  **Importação via CSV:** Crie sua periodização completa (Mesociclo) em uma planilha e suba de uma vez.
2.  **Pull & Push:** Baixe seus treinos da nuvem da Garmin ("Pull"), edite localmente com agilidade e envie de volta ("Push").
3.  **Smart Match:** Nosso algoritmo entende "linguagem de academia". Se você escrever `peckdeck`, ele sabe que é `FLYE_PEC_DECK_FLYE`.
4.  **Gerenciador de Limpeza:** Apague aqueles 50 treinos de teste "Sem Título" em segundos.
5.  **Controle Total:** Define séries, reps, carga (kg) e **tempo de descanso** (que a Garmin adora ignorar).

---

## 🛠️ Instalação (O Aquecimento)

Você precisa de **Python 3** instalado. Se você sabe contar anilhas, sabe rodar isso.

1.  **Clone o projeto:**
    ```bash
    git clone [https://github.com/seu-usuario/garmin-studio.git](https://github.com/seu-usuario/garmin-studio.git)
    cd garmin-studio
    ```

2.  **Crie seu ambiente virtual (opcional, mas recomendado):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure suas credenciais:**
    Crie um arquivo `.env` na raiz do projeto (copie o `.env.example`) e coloque seu login da Garmin:
    ```env
    GARMIN_EMAIL=seu_email@exemplo.com
    GARMIN_PASSWORD=sua_senha_secreta
    ```

---

## 🏋️‍♂️ Como Usar (O Treino)

### 1. Iniciando a Aplicação
Rode o comando:
```bash
python src/app.py
```

O servidor vai subir. Acesse no navegador: http://127.0.0.1:5000.

### 2. O Fluxo de Trabalho (Workflow)
A interface é dividida em duas abas para separar a **Criação** da **Destruição**.

#### Aba EDITOR (Criar e Editar)
* **Manual:** Adicione linhas, digite o nome do exercício (ex: "Agachamento") e veja o autocomplete encontrar o exercício certo.
* **PULL (Baixar):** Clique em `PULL` para baixar tudo que está no seu relógio agora. Edite na tabela e reenvie.
* **CSV (Importar):** Tem uma planilha pronta? Importe o CSV e a mágica acontece.
* **PUSH (Enviar):** Clique, espere a barra verde, e pronto. Sincronize seu relógio.

#### Aba GERENCIADOR (Deletar)
* Use para limpar a bagunça.
* Filtre por nome (ex: "Treino Antigo"), selecione tudo e **DELETE**. Sem piedade.

### 3. Formato do CSV
Quer criar no Excel? Salve como `.csv` (separado por vírgula) com estas colunas:

| Coluna | Descrição | Exemplo |
| :--- | :--- | :--- |
| `treino` | Nome do Treino (agrupa exercícios) | `Treino A - Peito` |
| `exercicio` | (Opcional) ID técnico se souber | *deixe vazio* |
| `nota_personalizada` | Nome que você usa (Busca Inteligente) | `Supino Inclinado` |
| `series` | Número de Sets | `4` |
| `reps` | Repetições Alvo | `12` |
| `peso_kg` | Carga | `30` |
| `intervalo_segundos` | Descanso entre séries | `60` |

---

## 🤖 A Inteligência por trás (Backstage)

Utilizamos um dicionário de sinônimos poderoso (`search_rules.json`).
* Você digita: `pulley`
* Nós buscamos: `LAT_PULLDOWN`, `PULL_DOWN`, `COSTAS`...
* Resultado: O exercício correto aparece no relógio, e o nome "Pulley" fica na anotação para você ler durante o treino.

---

## ⚠️ Disclaimer

Este projeto utiliza a API da Garmin de forma não oficial. Use com responsabilidade. Não nos responsabilizamos se você colocar 500kg no Deadlift e seu relógio achar que você é um guindaste.

**By ROCKETTES** 🚀
*Train Hard, Code Harder.*