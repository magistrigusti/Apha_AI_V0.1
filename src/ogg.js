import axios from "axios";
import { createWriteStream } from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

class OggConverter {
  constructor() {}

  toMp3(input, output) {
    try {

    } catch (e) {
      console.log('Error while creating ogg', e.message);
    }
  }

  async create(url, filename) {
    try {
      const oggPath = resolve(__dirname, '../voices', `${filename}.ogg`);
      const response = await axios({
        method: 'get',
        url,
        responseType: 'streem',
      });

      return new Promise(resolve => {
        const stream = createWriteStream(oggPath);
        response.data.pipe(stream);
        stream.on('finish', () => resolve(oggPath));
      });
    } catch (e) {
      console.log('Error while creating ogg', e.message)
    }
  }
}

export const ogg = new OggConverter();