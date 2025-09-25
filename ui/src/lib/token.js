import { Tiktoken } from "tiktoken/lite";
import cl100k_base from "tiktoken/encoders/cl100k_base.json";

const encoding = new Tiktoken(
  cl100k_base.bpe_ranks,
  cl100k_base.special_tokens,
  cl100k_base.pat_str
);

/**
 * Calculates the number of tokens in the given text.
 *
 * @param {string} text - The input string for which to calculate the token count.
 * @returns {number} The length of the encoded tokens array.
 * @throws {Error} If the encoding fails or if the input is not a valid string.
 */
export function calculateTokens(text) {
  const tokens = encoding.encode(text);
  return tokens.length;
}
