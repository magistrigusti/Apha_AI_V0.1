# fine_tune.py
# Скрипт дообучения модели на данных Аллода
# Запускать в Google Colab (бесплатный GPU)
# или локально если есть видеокарта

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset


# --- Настройки ---
BASE_MODEL = "distilgpt2"
DATASET_PATH = "../../datasets/allod_advisor.jsonl"
OUTPUT_DIR = "./allod-alpha-model"
EPOCHS = 5
BATCH_SIZE = 2
LEARNING_RATE = 5e-5
MAX_LENGTH = 256


def format_example(example):
    """Форматируем пару промпт-ответ в текст"""
    text = (
        f"Вопрос: {example['prompt']}\n"
        f"Ответ: {example['response']}\n"
    )
    return {"text": text}


def tokenize(example, tokenizer):
    """Токенизируем текст"""
    return tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
    )


def main():
    # 1. Загружаем токенизатор и модель
    print(f"Загружаем модель: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL
    )

    # Устанавливаем pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Загружаем датасет
    print(f"Загружаем датасет: {DATASET_PATH}")
    dataset = load_dataset(
        "json",
        data_files=DATASET_PATH,
        split="train",
    )

    # 3. Форматируем
    dataset = dataset.map(format_example)

    # 4. Токенизируем
    dataset = dataset.map(
        lambda x: tokenize(x, tokenizer),
        remove_columns=["prompt", "response", "text"],
    )

    # 5. Настраиваем обучение
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        save_strategy="epoch",
        logging_steps=10,
        fp16=False,
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

    # 6. Обучаем
    print("Начинаем обучение...")
    trainer.train()

    # 7. Сохраняем
    print(f"Сохраняем модель: {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Готово!")


if __name__ == "__main__":
    main()
