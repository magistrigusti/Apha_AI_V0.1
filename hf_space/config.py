import os


MODEL_ID = os.getenv(
    "MODEL_ID",
    "Qwen/Qwen2.5-1.5B-Instruct",
)

MAX_CONTEXT_TURNS = int(
    os.getenv("MAX_CONTEXT_TURNS", "4")
)

# Для Telegram и игрового клиента полезно дать чуть больше места на ответ.
MAX_NEW_TOKENS = int(
    os.getenv("MAX_NEW_TOKENS", "260")
)

# Чуть ниже температура = меньше фантазий, больше привязка к знаниям.
TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.4")
)

TOP_P = float(
    os.getenv("TOP_P", "0.9")
)

# 6 чанков позволяют взять:
# короткий ответ + длинний ответ + knowledge_base + запас.
MAX_RETRIEVED_CHUNKS = int(
    os.getenv("MAX_RETRIEVED_CHUNKS", "6")
)