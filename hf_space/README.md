
title: Alpha - Advisor of Allodium
emoji: 🤖
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 6.10.0
app_file: app.py
pinned: false
---

# Alpha - Hugging Face Space

This Space runs Alpha, the in-world advisor for Allodium.

## Runtime notes

- The Space uses the Gradio SDK managed by Hugging Face.
- Do not pin a conflicting Gradio version in `requirements.txt`.
- Extra Python dependencies should be listed in `requirements.txt`.

## Environment variables

- `MODEL_ID`
- `MAX_CONTEXT_TURNS`
- `MAX_NEW_TOKENS`
- `TEMPERATURE`
- `TOP_P`
- `MAX_RETRIEVED_CHUNKS`

## Knowledge sources

- `knowledge.py` contains the compact built-in world summary.
- `knowledge_base/` contains curated local facts and role docs.
- `../datasets/` can provide larger reference texts such as the whitepaper when present in the repo.