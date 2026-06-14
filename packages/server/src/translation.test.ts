import { describe, expect, it } from "vitest";
import { translate, translateOffline, TranslationError } from "./translation.js";

describe("translateOffline", () => {
  it("translates English to Spanish word by word", () => {
    expect(translateOffline("hello world", "en", "es")).toBe("hola mundo");
  });

  it("preserves capitalization", () => {
    expect(translateOffline("Hello World", "en", "fr")).toBe("Bonjour Monde");
  });

  it("uses English as a pivot between two non-English languages", () => {
    expect(translateOffline("hola mundo", "es", "de")).toBe("hallo welt");
  });

  it("passes unknown words through unchanged", () => {
    expect(translateOffline("hello xyzzy", "en", "es")).toBe("hola xyzzy");
  });

  it("preserves punctuation and spacing", () => {
    expect(translateOffline("hello, world!", "en", "es")).toBe("hola, mundo!");
  });

  it("returns text unchanged when languages match", () => {
    expect(translateOffline("hello", "en", "en")).toBe("hello");
  });

  it("translates multi-word phrases (longest match wins)", () => {
    expect(translateOffline("Thank you my friend", "en", "fr")).toBe(
      "Merci mon ami",
    );
  });

  it("maps multi-word phrases back through English", () => {
    expect(translateOffline("au revoir", "fr", "es")).toBe("adiós");
  });
});

describe("translate", () => {
  it("returns a structured result via the offline provider", async () => {
    const result = await translate("hello", "en", "de");
    expect(result).toEqual({
      translatedText: "hallo",
      from: "en",
      to: "de",
      provider: "offline",
    });
  });

  it("rejects empty text", async () => {
    await expect(translate("", "en", "es")).rejects.toBeInstanceOf(TranslationError);
  });

  it("rejects unsupported languages", async () => {
    await expect(translate("hello", "en", "xx")).rejects.toBeInstanceOf(
      TranslationError,
    );
  });
});
