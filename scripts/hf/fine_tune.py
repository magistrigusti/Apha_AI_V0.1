# fine_tune.py — дообучение той же базы, что и в Space (Qwen Instruct).
# Colab: Runtime → GPU, смонтируй Drive или залей datasets/ и этот скрипт.
# Локально: нужен CUDA и ~6+ ГБ VRAM для 0.5B полного fine-tune.

from __future__ import annotations

import os
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# Путь к репозиторию: scripts/hf → корень
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DATASET_PATH = REPO_ROOT / "datasets" / "allod_advisor.jsonl"

# Должно совпадать с hf_space/config.py MODEL_ID, иначе веса не подойдут Space.
BASE_MODEL = os.environ.get(
    "ALPHA_BASE_MODEL",
    "Qwen/Qwen2.5-0.5B-Instruct",
)
OUTPUT_DIR = os.environ.get("ALPHA_OUTPUT_DIR", "./alpha-qwen-allodium")
EPOCHS = int(os.environ.get("ALPHA_EPOCHS", "3"))
BATCH_SIZE = int(os.environ.get("ALPHA_BATCH", "2"))
LEARNING_RATE = float(os.environ.get("ALPHA_LR", "2e-5"))
MAX_LENGTH = int(os.environ.get("ALPHA_MAX_LEN", "512"))


def _format_chat_text(example: dict, tokenizer) -> dict:
    messages = [
        {"role": "user", "content": example["prompt"]},
        {"role": "assistant", "content": example["response"]},
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


def _tokenize_batch(examples: dict, tokenizer):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
    )


def main() -> None:
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Нет файла датасета: {DATASET_PATH}")

    use_cuda = torch.cuda.is_available()
    print(f"[Alpha FT] Модель: {BASE_MODEL}, CUDA: {use_cuda}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    # Без device_map: Trainer сам разложит веса на GPU при обучении.
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if use_cuda else torch.float32,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = load_dataset(
        "json",
        data_files=str(DATASET_PATH),
        split="train",
    )
    dataset = dataset.map(
        lambda ex: _format_chat_text(ex, tokenizer),
        remove_columns=["prompt", "response"],
    )
    dataset = dataset.map(
        lambda batch: _tokenize_batch(batch, tokenizer),
        batched=True,
        remove_columns=["text"],
    )

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        save_strategy="epoch",
        logging_steps=10,
        fp16=use_cuda,
        report_to="none",
    )
    collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        data_collator=collator,
    )
    print("[Alpha FT] Старт обучения…")
    trainer.train()
    print(f"[Alpha FT] Сохранение в {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(
        "[Alpha FT] Готово. Залей папку на HF Hub и в Space "
        "укажи MODEL_ID=твой/репозиторий."
    )


if __name__ == "__main__":
    main()
