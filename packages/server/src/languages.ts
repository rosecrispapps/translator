export interface Language {
  code: string;
  name: string;
}

export const LANGUAGES: Language[] = [
  { code: "en", name: "English" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
];

export const LANGUAGE_CODES = LANGUAGES.map((l) => l.code);

export function isSupported(code: string): boolean {
  return LANGUAGE_CODES.includes(code);
}
