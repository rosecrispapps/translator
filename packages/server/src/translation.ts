import { DICTIONARY, Translations } from "./dictionary.js";
import { isSupported } from "./languages.js";

export interface TranslationResult {
  translatedText: string;
  from: string;
  to: string;
  provider: string;
}

export class TranslationError extends Error {
  constructor(
    message: string,
    public statusCode = 400,
  ) {
    super(message);
    this.name = "TranslationError";
  }
}

type TargetLang = keyof Translations;

const WORD_RE = /[A-Za-zÀ-ÿ]/;

function isWord(token: string): boolean {
  return WORD_RE.test(token);
}

function matchCase(source: string, target: string): string {
  if (source.length === 0) return target;
  if (source === source.toUpperCase() && source !== source.toLowerCase()) {
    return target.toUpperCase();
  }
  if (source[0] === source[0].toUpperCase()) {
    return target.charAt(0).toUpperCase() + target.slice(1);
  }
  return target;
}

interface Lookup {
  phrases: Map<string, string>;
  maxWords: number;
}

/**
 * Build a map from a source phrase (lowercased, space-joined) to its English
 * dictionary key, for the given source language. English is the pivot language,
 * so when translating from a non-English language we map back to the key first.
 */
function buildLookup(from: string): Lookup {
  const phrases = new Map<string, string>();
  let maxWords = 1;

  if (from === "en") {
    for (const key of Object.keys(DICTIONARY)) {
      phrases.set(key, key);
      maxWords = Math.max(maxWords, key.split(" ").length);
    }
  } else {
    for (const [english, translations] of Object.entries(DICTIONARY)) {
      const phrase = translations[from as TargetLang].toLowerCase();
      if (!phrases.has(phrase)) phrases.set(phrase, english);
      maxWords = Math.max(maxWords, phrase.split(" ").length);
    }
  }

  return { phrases, maxWords };
}

function fromEnglish(englishKey: string, to: string): string | null {
  if (to === "en") return englishKey;
  return DICTIONARY[englishKey]?.[to as TargetLang] ?? null;
}

/**
 * Collect up to `count` consecutive word tokens starting at `start`, requiring
 * that the separators between them are whitespace only. Returns the collected
 * words and the index just past the last consumed word, or null if a phrase of
 * that length cannot be formed.
 */
function collectWords(
  parts: string[],
  start: number,
  count: number,
): { words: string[]; endIndex: number } | null {
  const words = [parts[start]];
  let idx = start + 1;
  while (words.length < count) {
    const sep = parts[idx];
    if (sep === undefined || !/^\s+$/.test(sep)) return null;
    const next = parts[idx + 1];
    if (next === undefined || !isWord(next)) return null;
    words.push(next);
    idx += 2;
  }
  return { words, endIndex: idx };
}

/**
 * Offline translation using the bundled dictionary with English as the pivot
 * language. Supports multi-word phrases (longest match wins). Unknown tokens are
 * passed through unchanged so output is never empty; punctuation and whitespace
 * are preserved.
 */
export function translateOffline(text: string, from: string, to: string): string {
  if (from === to) return text;

  const { phrases, maxWords } = buildLookup(from);
  const parts = text.match(/[A-Za-zÀ-ÿ]+|[^A-Za-zÀ-ÿ]+/g) ?? [];
  const out: string[] = [];

  let i = 0;
  while (i < parts.length) {
    if (!isWord(parts[i])) {
      out.push(parts[i]);
      i += 1;
      continue;
    }

    let matched = false;
    for (let w = maxWords; w >= 1; w -= 1) {
      const collected = collectWords(parts, i, w);
      if (!collected) continue;
      const phrase = collected.words.map((x) => x.toLowerCase()).join(" ");
      const englishKey = phrases.get(phrase);
      if (englishKey === undefined) continue;
      const translatedBase = fromEnglish(englishKey, to);
      if (translatedBase === null) continue;
      out.push(matchCase(collected.words[0], translatedBase));
      i = collected.endIndex;
      matched = true;
      break;
    }

    if (!matched) {
      out.push(parts[i]);
      i += 1;
    }
  }

  return out.join("");
}

async function translateWithMyMemory(
  text: string,
  from: string,
  to: string,
): Promise<string> {
  const url = new URL("https://api.mymemory.translated.net/get");
  url.searchParams.set("q", text);
  url.searchParams.set("langpair", `${from}|${to}`);

  const response = await fetch(url, { signal: AbortSignal.timeout(8000) });
  if (!response.ok) {
    throw new TranslationError(
      `MyMemory provider returned ${response.status}`,
      502,
    );
  }
  const data = (await response.json()) as {
    responseData?: { translatedText?: string };
  };
  const translated = data.responseData?.translatedText;
  if (!translated) {
    throw new TranslationError("MyMemory provider returned no translation", 502);
  }
  return translated;
}

export async function translate(
  text: string,
  from: string,
  to: string,
): Promise<TranslationResult> {
  if (typeof text !== "string" || text.trim() === "") {
    throw new TranslationError("`text` must be a non-empty string");
  }
  if (!isSupported(from)) {
    throw new TranslationError(`Unsupported source language: ${from}`);
  }
  if (!isSupported(to)) {
    throw new TranslationError(`Unsupported target language: ${to}`);
  }

  const provider = process.env.TRANSLATION_PROVIDER ?? "offline";

  if (provider === "mymemory") {
    const translatedText = await translateWithMyMemory(text, from, to);
    return { translatedText, from, to, provider };
  }

  return {
    translatedText: translateOffline(text, from, to),
    from,
    to,
    provider: "offline",
  };
}
