import request from "supertest";
import { describe, expect, it } from "vitest";
import { createApp } from "./app.js";

const app = createApp();

describe("API", () => {
  it("GET /api/health returns ok", async () => {
    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("GET /api/languages returns supported languages", async () => {
    const res = await request(app).get("/api/languages");
    expect(res.status).toBe(200);
    expect(res.body.languages).toEqual(
      expect.arrayContaining([{ code: "en", name: "English" }]),
    );
  });

  it("POST /api/translate translates text", async () => {
    const res = await request(app)
      .post("/api/translate")
      .send({ text: "hello world", from: "en", to: "es" });
    expect(res.status).toBe(200);
    expect(res.body.translatedText).toBe("hola mundo");
  });

  it("POST /api/translate rejects invalid input", async () => {
    const res = await request(app)
      .post("/api/translate")
      .send({ text: "", from: "en", to: "es" });
    expect(res.status).toBe(400);
    expect(res.body.error).toBeDefined();
  });
});
