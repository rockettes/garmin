Markdown

# 🏋️ Garmin Workout Studio

Uma aplicação web local para criar, editar e injetar treinos de musculação complexos diretamente na plataforma Garmin Connect.

## Funcionalidades
- Banco de dados offline com todos os exercícios oficiais da Garmin.
- Busca inteligente de exercícios (ignora acentos).
- Criação de treinos em lote.
- Injeção direta na API da Garmin.

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv .venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Crie um arquivo `.env` na raiz com suas credenciais:

GARMIN_EMAIL=seu@email.com GARMIN_PASSWORD=sua_senha


## Como Usar

1. **Atualizar Dados (Opcional):** Se a Garmin mudar os nomes, coloque o arquivo bruto em `data/raw/garmin_properties.txt` e rode:

```bash
python src/build_db.py

    Rodar a Aplicação:
    Bash

    python run.py

    Acesse https://www.google.com/search?q=http://127.0.0.1:5000
```

#### 3. `LICENSE` (Jurídico ⚖️)
Para projetos open-source pessoais, a **MIT License** é a mais comum (permite tudo, sem garantia).

MIT License

Copyright (c) 2024 [Seu Nome]

Permission is hereby granted, free of charge, to any person obtaining a copy...
[Pode copiar o texto padrão da licença MIT no Google, é bem curto]
