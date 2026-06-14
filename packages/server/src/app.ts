import cors from "cors";
import express, { type Request, type Response, type NextFunction } from "express";
import { LANGUAGES } from "./languages.js";
import { translate, TranslationError } from "./translation.js";

export function createApp() {
  const app = express();
  app.use(cors());
  app.use(express.json());

  app.get("/api/health", (_req: Request, res: Response) => {
    res.json({ status: "ok" });
  });

  app.get("/api/languages", (_req: Request, res: Response) => {
    res.json({ languages: LANGUAGES });
  });

  app.post("/api/translate", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { text, from, to } = req.body ?? {};
      const result = await translate(text, from, to);
      res.json(result);
    } catch (err) {
      next(err);
    }
  });

  // Centralized error handler.
  app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (err instanceof TranslationError) {
      res.status(err.statusCode).json({ error: err.message });
      return;
    }
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  });

  return app;
}
