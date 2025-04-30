// openai.js
import OpenAI from 'openai';
import { createReadStream } from 'fs';

class OpenAi {
  constructor(apiKey) {
    this.openai = new OpenAI({ apiKey });
  }

  async transcription(filepath) {
    try {
      const response = await this.openai.audio.transcriptions.create({
        file: createReadStream(filepath),
        model: 'whisper-1',
      });
      return response.text;
    } catch (e) {
      console.log('Error while transcription:', e.message);
    }
  }

  chat() {
    // потом добавим
  }
}

// 👇 Вот это обязательно внизу:
export function getOpenaiInstance() {
  return new OpenAi(process.env.OPENAI_API_KEY);
}
