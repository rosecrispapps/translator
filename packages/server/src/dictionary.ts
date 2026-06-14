/**
 * Small offline phrase/word dictionary keyed by the English form.
 *
 * The offline provider uses English as a pivot language: to translate between
 * two non-English languages it first maps the source back to English, then out
 * to the target. This keeps the demo fully functional without any network
 * access or API keys, while remaining easy to extend with more entries.
 */
export type Translations = {
  es: string;
  fr: string;
  de: string;
};

export const DICTIONARY: Record<string, Translations> = {
  hello: { es: "hola", fr: "bonjour", de: "hallo" },
  world: { es: "mundo", fr: "monde", de: "welt" },
  goodbye: { es: "adiós", fr: "au revoir", de: "auf wiedersehen" },
  please: { es: "por favor", fr: "s'il vous plaît", de: "bitte" },
  "thank you": { es: "gracias", fr: "merci", de: "danke" },
  thanks: { es: "gracias", fr: "merci", de: "danke" },
  yes: { es: "sí", fr: "oui", de: "ja" },
  no: { es: "no", fr: "non", de: "nein" },
  good: { es: "bueno", fr: "bon", de: "gut" },
  morning: { es: "mañana", fr: "matin", de: "morgen" },
  night: { es: "noche", fr: "nuit", de: "nacht" },
  friend: { es: "amigo", fr: "ami", de: "freund" },
  water: { es: "agua", fr: "eau", de: "wasser" },
  food: { es: "comida", fr: "nourriture", de: "essen" },
  cat: { es: "gato", fr: "chat", de: "katze" },
  dog: { es: "perro", fr: "chien", de: "hund" },
  house: { es: "casa", fr: "maison", de: "haus" },
  book: { es: "libro", fr: "livre", de: "buch" },
  love: { es: "amor", fr: "amour", de: "liebe" },
  welcome: { es: "bienvenido", fr: "bienvenue", de: "willkommen" },
  i: { es: "yo", fr: "je", de: "ich" },
  you: { es: "tú", fr: "tu", de: "du" },
  and: { es: "y", fr: "et", de: "und" },
  the: { es: "el", fr: "le", de: "der" },
  is: { es: "es", fr: "est", de: "ist" },
  my: { es: "mi", fr: "mon", de: "mein" },
  name: { es: "nombre", fr: "nom", de: "name" },
};
