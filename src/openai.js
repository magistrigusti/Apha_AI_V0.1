import { Configuration, OpenAIApi} from 'openai';
import config from 'config';

class OpenAi {
  constructor(apiKey) {
    const configuration = new Configuration({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.openai = new OpenAIApi(configuration);
  }

  chat() {}

  transcription() { }
}

export const openai = new OpenAi();