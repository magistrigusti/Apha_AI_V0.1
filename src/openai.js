// openai.js
import OpenAI from 'openai';
import { createReadStream } from 'fs';
import dotenv from 'dotenv';
dotenv.config();

class OpenAi {
  constructor(apiKey) {
    this.openai = new OpenAI({
      apiKey: apiKey || process.env.OPENAI_KEY,
    });
  }

  async transcription(filepath) {
    try {
      console.log('Transcribing file:', filepath);
      const response = await this.openai.audio.transcriptions.create({
        file: createReadStream(filepath),
        model: 'whisper-1',
      });

      return response.text;
    } catch (e) {
      console.error('Ошибка при расшифровке:', e.message);
      return 'Ошибка при расшифровке';
    }
  }

  async chat(promptText) {
    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [{ role: 'user', content: promptText }],
        temperature: 0.7,
      });

      return response.choices[0].message.content;
    } catch (e) {
      console.error('Ошибка при генерации ответа:', e.message);
      return 'Ошибка при генерации ответа';
    }
  }
}

// 👇 Без config. Только .env
export const openai = new OpenAi();
