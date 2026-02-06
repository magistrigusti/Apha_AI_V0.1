from huggingface_hub import model_info


def main():
    # Быстрая проверка, что HF Hub доступен
    info = model_info("gpt2")
    print(info)


if __name__ == "__main__":
    main()
