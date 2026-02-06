# Hugging Face Hub

Этот блок нужен для работы с HF Hub через Python
(huggingface_hub).

## Быстрый старт (Windows, PowerShell)

1) Создать виртуальное окружение
   python -m venv .venv

2) Активировать
   .\.venv\Scripts\Activate.ps1

3) Установить зависимости
   pip install --upgrade -r scripts/hf/requirements.txt

4) Логин (если нужен доступ к приватным)
   hf auth login

5) Проверка установки
   python scripts/hf/check_install.py

## Примечания

- Токен можно хранить в HF_TOKEN.
- На Windows кеш HF может использовать симлинки
  только при включенном Developer Mode.
