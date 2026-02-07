# src/exercise_db.py

# --- MAPA DE EXERCÍCIOS BLINDADO (SAFE MAPPING) ---
# Baseado nos testes de debug:
# - Extensora/Leg Press -> SQUAT (Garante mapa de pernas)
# - Peck Deck/Crucifixo -> BENCH_PRESS (Garante mapa de peito)
# - Chaves inválidas removidas.

EXERCISE_DB = {
    # === PEITO ===
    "supino":         {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "peck":           {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "deck":           {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "crucifixo":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "fly":            {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "crossover":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "flexao":         {"cat": "PUSH_UP", "name": "PUSH_UP"},
    "press":          {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    
    # === COSTAS ===
    "remada":         {"cat": "ROW", "name": "ROW"},
    "puxada":         {"cat": "PULL_UP", "name": "PULL_UP"},
    "barra":          {"cat": "PULL_UP", "name": "PULL_UP"},
    "pulldown":       {"cat": "PULL_UP", "name": "PULL_UP"},
    "dorsal":         {"cat": "PULL_UP", "name": "PULL_UP"},
    
    # === PERNAS ===
    "agachamento":    {"cat": "SQUAT", "name": "SQUAT"},
    "leg":            {"cat": "SQUAT", "name": "SQUAT"}, # Fallback seguro
    "extensora":      {"cat": "SQUAT", "name": "SQUAT"}, # Fallback seguro
    "flexora":        {"cat": "LEG_CURL", "name": "LEG_CURL"},
    "afundo":         {"cat": "LUNGE", "name": "LUNGE"},
    "bulgaro":        {"cat": "SQUAT", "name": "SQUAT"},
    "sumo":           {"cat": "SQUAT", "name": "SQUAT"},
    
    # Glúteos
    "elevacao":       {"cat": "HIP_RAISE", "name": "HIP_RAISE"},
    "pelvica":        {"cat": "HIP_RAISE", "name": "HIP_RAISE"},
    
    # Panturrilha
    "panturrilha":    {"cat": "CALF_RAISE", "name": "CALF_RAISE"},
    "gemeos":         {"cat": "CALF_RAISE", "name": "CALF_RAISE"},
    "solear":         {"cat": "CALF_RAISE", "name": "CALF_RAISE"},
    
    # Posterior/Terra
    "stiff":          {"cat": "DEADLIFT", "name": "DEADLIFT"},
    "terra":          {"cat": "DEADLIFT", "name": "DEADLIFT"},
    
    # === OMBROS ===
    "desenvolvimento": {"cat": "SHOULDER_PRESS", "name": "SHOULDER_PRESS"},
    "lateral":         {"cat": "LATERAL_RAISE", "name": "LATERAL_RAISE"},
    "ombro":           {"cat": "SHOULDER_PRESS", "name": "SHOULDER_PRESS"},

    # === BRAÇOS ===
    "triceps":         {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "testa":           {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "corda":           {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "frances":         {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "mergulho":        {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "pulley":          {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    
    "rosca":           {"cat": "CURL", "name": "CURL"},
    "biceps":          {"cat": "CURL", "name": "CURL"},
    
    # === ABS ===
    "abdominal":       {"cat": "CRUNCH", "name": "CRUNCH"},
    "prancha":         {"cat": "PLANK", "name": "PLANK"}
}