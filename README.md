# 🏋️‍♂️ Garmin Workout Creator (Python)

> **Automatize a criação de treinos de musculação no Garmin Connect via CSV, com suporte garantido ao Mapa de Calor Muscular.**

Este projeto permite criar treinos complexos de musculação (*Strength Training*) no Garmin Connect lendo um simples arquivo CSV. Ele resolve o problema da criação manual lenta no aplicativo e contorna as limitações da API para garantir que o **Mapa de Calor Muscular** (*Muscle Heatmap*) do seu relógio funcione corretamente.

---

## 🚀 Funcionalidades

- **Importação via CSV:** Crie treinos inteiros editando uma planilha simples.
- **Mapeamento Inteligente ("Safe Mapping"):** Converte exercícios específicos (como "Cadeira Extensora" ou "Peck Deck") em chaves internas que a Garmin aceita (como `SQUAT` ou `BENCH_PRESS`), garantindo que o grupo muscular correto seja registrado.
- **Agrupamento de Séries:** Gera automaticamente a estrutura de repetição (ex: "3 Séries de 12 repetições") para visualização limpa no relógio.
- **Sanitização de Texto:** Remove acentos e caracteres especiais automaticamente para evitar erros de API (Erro 400).
- **Intervalos Personalizados:** Insere o tempo de descanso na tela do relógio e na nota do passo (ex: "60s") para fácil visualização durante o treino.

---

## 📋 Pré-requisitos

- Python 3.10 ou superior.
- Uma conta no Garmin Connect.
- Arquivos de treino em formato `.csv`.

---

## 🔧 Instalação

1. **Clone este repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/garmin-workout-creator.git](https://github.com/SEU_USUARIO/garmin-workout-creator.git)
   cd garmin-workout-creator

```

2. **Crie um ambiente virtual (recomendado):**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

```


3. **Instale as dependências:**
Crie um arquivo `requirements.txt` com o conteúdo abaixo e instale:
```bash
pip install -r requirements.txt

```


**Conteúdo do requirements.txt:**
```text
garminconnect
pandas
python-dotenv
requests

```



---

## ⚙️ Configuração

1. Crie um arquivo chamado `.env` na raiz do projeto (baseado no `.env.example` se houver).
2. Adicione suas credenciais do Garmin Connect:

```ini
GARMIN_EMAIL=seu_email@gmail.com
GARMIN_PASSWORD=sua_senha_secreta

```

> **Nota de Segurança:** O arquivo `.env` deve ser incluído no `.gitignore` para proteger suas senhas de serem enviadas ao GitHub.

---

## 🏃‍♂️ Como Usar

1. **Prepare seu CSV:**
Crie um arquivo na pasta `data/` (ex: `treino_a.csv`). O formato deve ser exatamente este (cabeçalho obrigatório):
| nota_personalizada | series | reps | peso_kg | intervalo_segundos |
| --- | --- | --- | --- | --- |
| SUPINO INCLINADO | 4 | 12 | 30 | 60 |
| PECK DECK | 3 | 15 | 45 | 60 |
| TRICEPS CORDA | 3 | 12 | 25 | 45 |


2. **Execute o script:**
Abra o terminal na raiz do projeto e rode:
```bash
python src/main.py --file data/treino_a.csv --name "Treino A - Peito"

```


* `--file`: Caminho relativo do arquivo CSV.
* `--name`: O nome que aparecerá no seu relógio/app Garmin.


3. **Verifique no App:**
Abra o Garmin Connect > Treinos. Seu novo treino estará lá, pronto para ser enviado ao dispositivo!

---

## 🧠 A Lógica do "Mapa de Calor" (Safe Mapping)

A API da Garmin para contas pessoais é restrita e rejeita códigos específicos de máquinas (como `LEG_EXTENSION`, `PEC_DECK` ou `CALF_PRESS`), causando falha no upload (Erro 400).

Para contornar isso e **garantir que o mapa muscular funcione**, este script usa uma estratégia de mapeamento seguro (`src/exercise_db.py`):

| Exercício no CSV | Mapeado Internamente como | Benefício |
| --- | --- | --- |
| **Peck Deck / Crucifixo** | `BENCH_PRESS` (Supino) | Registra como **Peitoral** ✅ |
| **Cadeira Extensora** | `SQUAT` (Agachamento) | Registra como **Quadríceps** ✅ |
| **Leg Press** | `SQUAT` (Agachamento) | Registra como **Pernas** ✅ |
| **Elevação Pélvica** | `HIP_RAISE` | Registra como **Glúteos** ✅ |
| **Tríceps Máquina** | `TRICEPS_EXTENSION` | Registra como **Tríceps** ✅ |

**O que isso muda para você?**

* **Visual:** No relógio, você lerá o nome correto que colocou no CSV (ex: "CADEIRA EXTENSORA").
* **Ícone:** O ícone pode ser genérico (um halter ou agachamento) dependendo do mapeamento.
* **Dados:** O **Mapa de Calor** ao final do treino ficará com as cores corretas (Pernas vermelhas, Peito vermelho, etc.).

---

## 📂 Estrutura do Projeto

```
garmin-workout-creator/
├── data/                  # Seus arquivos CSV de treino
│   ├── peito_triceps.csv
│   └── perna_completo.csv
├── src/
│   ├── main.py            # Ponto de entrada (CLI)
│   ├── utils.py           # Lógica de geração do JSON e API
│   └── exercise_db.py     # Banco de dados de mapeamento de exercícios
├── .env                   # Credenciais (NÃO COMITAR)
├── .gitignore             # Arquivos ignorados pelo Git
├── requirements.txt       # Bibliotecas Python necessárias
└── README.md              # Documentação

```

---

## ⚠️ Isenção de Responsabilidade

Este projeto utiliza a biblioteca `garminconnect`, que é um wrapper não oficial da API da Garmin. O uso é de sua inteira responsabilidade. A Garmin pode alterar a API a qualquer momento, o que pode impactar a funcionalidade deste script.

---

## 🤝 Contribuição

Sinta-se à vontade para abrir Issues ou Pull Requests para melhorar o mapeamento de exercícios ou adicionar novas funcionalidades!

```