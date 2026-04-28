export {
  askAlpha,
  chatWithAlpha,
} from './alpha-nvidia.js';


export function extractAlphaAnswer(result) {
  if (typeof result === 'string') {
    return result.trim() || 'Нет ответа.';
  }

  if (typeof result?.data === 'string') {
    return result.data.trim() || 'Нет ответа.';
  }

  if (Array.isArray(result?.data)) {
    const [firstItem] = result.data;
    if (typeof firstItem === 'string') {
      return firstItem.trim() || 'Нет ответа.';
    }
  }

  return 'Нет ответа.';
}
