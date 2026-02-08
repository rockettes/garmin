# src/exercise_db.py

# --- MAPA DE EXERCÍCIOS "PLATINUM EDITION" ---
# Versão Final Pós-Payload:
# 1. Cadeira Extensora: A descoberta do ano -> Categoria "CRUNCH", Nome "LEG_EXTENSIONS".
# 2. Leg Press: Confirmado em SQUAT + LEG_PRESS.
# 3. Face Pull: Confirmado em SHOULDER_PRESS + FACE_PULL.

EXERCISE_DB = {
    # ==========================
    # 1. BRAÇOS (BÍCEPS/TRÍCEPS)
    # ==========================
    # Bíceps
    "rosca scott":    {"cat": "CURL", "name": "PREACHER_CURL"},
    "banco scott":    {"cat": "CURL", "name": "PREACHER_CURL"},
    "rosca polia":    {"cat": "CURL", "name": "CABLE_CURL"},
    "polia baixa":    {"cat": "CURL", "name": "CABLE_CURL"},
    "rosca direta":   {"cat": "CURL", "name": "CURL"},
    "rosca inversa":  {"cat": "CURL", "name": "CURL"},
    "rosca martelo":  {"cat": "CURL", "name": "CURL"},
    
    # Genéricos de Bíceps
    "rosca":          {"cat": "CURL", "name": "CURL"},
    "biceps":         {"cat": "CURL", "name": "CURL"},
    "scott":          {"cat": "CURL", "name": "PREACHER_CURL"},

    # Tríceps
    "triceps pulley": {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "triceps corda":  {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "triceps testa":  {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "triceps banco":  {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "frances":        {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "mergulho":       {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},
    "triceps":        {"cat": "TRICEPS_EXTENSION", "name": "TRICEPS_EXTENSION"},

    # ==========================
    # 2. COSTAS
    # ==========================
    # Posteriores de Ombro
    "peck deck inverso":  {"cat": "SHOULDER_PRESS", "name": "REVERSE_FLY_MACHINE"},
    "crucifixo inverso":  {"cat": "SHOULDER_PRESS", "name": "REVERSE_FLY"},
    "voador inverso":     {"cat": "SHOULDER_PRESS", "name": "REVERSE_FLY_MACHINE"},

    # Pulley Frente
    "pulley frente":      {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"}, 
    "pulley costas":      {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"},
    "pulley triangulo":   {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"},
    "puxada alta":        {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"},
    "puxada frente":      {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"},
    "puxada":             {"cat": "PULL_UP", "name": "CABLE_PULLDOWN"},
    
    # Pull Down
    "pull down":          {"cat": "ROW", "name": "STRAIGHT_ARM_PULLDOWN"},
    "pulldown":           {"cat": "ROW", "name": "STRAIGHT_ARM_PULLDOWN"},
    
    # Remadas
    "remada articulada":  {"cat": "ROW", "name": "MACHINE_ROW"},
    "remada maquina":     {"cat": "ROW", "name": "MACHINE_ROW"},
    "remada baixa":       {"cat": "ROW", "name": "SEATED_CABLE_ROW"},
    "remada cabo":        {"cat": "ROW", "name": "SEATED_CABLE_ROW"},
    "remada cavalinho":   {"cat": "ROW", "name": "V_BAR_ROW"},
    
    "serrote":            {"cat": "ROW", "name": "ROW"},
    "remada curvada":     {"cat": "ROW", "name": "ROW"},
    "remada":             {"cat": "ROW", "name": "ROW"},
    
    "barra fixa":         {"cat": "PULL_UP", "name": "PULL_UP"},
    "graviton":           {"cat": "PULL_UP", "name": "PULL_UP"},
    
    "hiperextensao":      {"cat": "HYPEREXTENSION", "name": "HYPEREXTENSION"},
    "lombar":             {"cat": "HYPEREXTENSION", "name": "HYPEREXTENSION"},

    # ==========================
    # 3. PEITO
    # ==========================
    "supino reto":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "supino inclinado": {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "supino declinado": {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "supino vertical":  {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "supino":           {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    
    "peck deck":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"}, 
    "crucifixo":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "crossover":      {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "fly":            {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},
    "flexao":         {"cat": "PUSH_UP", "name": "PUSH_UP"},
    "press":          {"cat": "BENCH_PRESS", "name": "BENCH_PRESS"},

    # ==========================
    # 4. PERNAS (CORREÇÃO FINAL VIA PAYLOAD)
    # ==========================
    "agachamento":          {"cat": "SQUAT", "name": "SQUAT"},
    "agachamento smith":    {"cat": "SQUAT", "name": "SQUAT"},
    "agachamento pendulo":  {"cat": "SQUAT", "name": "SQUAT"},
    "hack":                 {"cat": "SQUAT", "name": "SQUAT"},
    "smith":                {"cat": "SQUAT", "name": "SQUAT"},
    "bulgaro":              {"cat": "SQUAT", "name": "SQUAT"},
    "sumo":                 {"cat": "SQUAT", "name": "SQUAT"},
    
    # Leg Press
    "leg press":            {"cat": "SQUAT", "name": "LEG_PRESS"}, 
    "leg press 45":         {"cat": "SQUAT", "name": "LEG_PRESS"},
    "leg":                  {"cat": "SQUAT", "name": "LEG_PRESS"},
    
    # Cadeira Extensora (A MÁGICA ACONTECE AQUI)
    # A Garmin classifica como CRUNCH (Abdominal) internamente. Não pergunte, apenas aceite.
    "cadeira extensora":    {"cat": "CRUNCH", "name": "LEG_EXTENSIONS"},
    "extensora":            {"cat": "CRUNCH", "name": "LEG_EXTENSIONS"},
    
    # Flexoras (Posterior)
    "mesa flexora":         {"cat": "LEG_CURL", "name": "LYING_LEG_CURL"},
    "cadeira flexora":      {"cat": "LEG_CURL", "name": "SEATED_LEG_CURL"},
    "flexora":              {"cat": "LEG_CURL", "name": "LEG_CURL"},
    
    "afundo":               {"cat": "LUNGE", "name": "LUNGE"},
    "stiff":                {"cat": "DEADLIFT", "name": "DEADLIFT"},
    "terra":                {"cat": "DEADLIFT", "name": "DEADLIFT"},
    "elevacao pelvica":     {"cat": "HIP_RAISE", "name": "HIP_RAISE"},
    "pelvica":              {"cat": "HIP_RAISE", "name": "HIP_RAISE"},
    
    # Panturrilhas
    "panturrilha":          {"cat": "CALF_RAISE", "name": "CALF_RAISE"},
    "gemeos":               {"cat": "CALF_RAISE", "name": "CALF_RAISE"},
    "gemeos sentado":       {"cat": "CALF_RAISE", "name": "SEATED_CALF_RAISE"},
    "gemeos em pe":         {"cat": "CALF_RAISE", "name": "STANDING_CALF_RAISE"},
    "solear":               {"cat": "CALF_RAISE", "name": "SEATED_CALF_RAISE"},

    # ==========================
    # 5. OMBROS
    # ==========================
    "desenvolvimento":  {"cat": "SHOULDER_PRESS", "name": "SHOULDER_PRESS"},
    
    # Elevação Lateral
    "elevacao lateral": {"cat": "LATERAL_RAISE", "name": "LATERAL_RAISE"},
    "lateral":          {"cat": "LATERAL_RAISE", "name": "LATERAL_RAISE"},
    "lateral polia":    {"cat": "LATERAL_RAISE", "name": "CABLE_LATERAL_RAISE"},
    
    # Elevação Frontal
    "elevacao frontal":        {"cat": "LATERAL_RAISE", "name": "FRONT_RAISE"},
    "elevacao frontal polia":  {"cat": "LATERAL_RAISE", "name": "CABLE_FRONT_RAISE"},
    "elevacao frontal cabo":   {"cat": "LATERAL_RAISE", "name": "CABLE_FRONT_RAISE"},
    "elevacao frontal halter": {"cat": "LATERAL_RAISE", "name": "DUMBBELL_FRONT_RAISE"},
    "frontal":                 {"cat": "LATERAL_RAISE", "name": "FRONT_RAISE"},

    # Face Pull
    "face pull":      {"cat": "SHOULDER_PRESS", "name": "FACE_PULL"},
    "facepull":       {"cat": "SHOULDER_PRESS", "name": "FACE_PULL"},
    "puxada face":    {"cat": "SHOULDER_PRESS", "name": "FACE_PULL"},
    "face pull cabo": {"cat": "SHOULDER_PRESS", "name": "CABLE_FACE_PULL"},

    "ombro":          {"cat": "SHOULDER_PRESS", "name": "SHOULDER_PRESS"},

    # ==========================
    # 6. ABS
    # ==========================
    "abdominal maquina":   {"cat": "CRUNCH", "name": "MACHINE_CRUNCH"},
    "abdominal":           {"cat": "CRUNCH", "name": "CRUNCH"},
    "abdominal paralelas": {"cat": "CRUNCH", "name": "KNEE_RAISE_PARALLEL_BARS"},
    "infra":               {"cat": "CRUNCH", "name": "CRUNCH"},
    "supra":               {"cat": "CRUNCH", "name": "CRUNCH"},
    "remador":             {"cat": "CRUNCH", "name": "CRUNCH"},
    "prancha":             {"cat": "PLANK", "name": "PLANK"}
}