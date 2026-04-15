import {
  handleAlphaHttpRequest,
} from '../src/alpha-http.js';


export default async function handler(
  req,
  res,
) {
  await handleAlphaHttpRequest(req, res);
}
