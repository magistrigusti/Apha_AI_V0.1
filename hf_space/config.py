# ========================================
# config.py — Настройки агента Альфа
# ========================================

import os

# ========== МОДЕЛЬ ==========
MODEL_ID = os.getenv(
    "MODEL_ID",
    "Qwen/Qwen2.5-0.5B-Instruct",
)

# ========== ПАРАМЕТРЫ ГЕНЕРАЦИИ ==========
MAX_CONTEXT_TURNS = int(
    os.getenv("MAX_CONTEXT_TURNS", "4")
)

MAX_NEW_TOKENS = int(
    os.getenv("MAX_NEW_TOKENS", "200")
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.7")
)

TOP_P = float(
    os.getenv("TOP_P", "0.9")
)