import { useEffect, useState } from "react";

interface Language {
  code: string;
  name: string;
}

export default function App() {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [text, setText] = useState("Hello world");
  const [from, setFrom] = useState("en");
  const [to, setTo] = useState("es");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/languages")
      .then((res) => res.json())
      .then((data) => setLanguages(data.languages ?? []))
      .catch(() => setError("Could not load languages."));
  }, []);

  async function handleTranslate(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult("");
    try {
      const res = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, from, to }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error ?? "Translation failed");
      }
      setResult(data.translatedText);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Translation failed");
    } finally {
      setLoading(false);
    }
  }

  function swap() {
    setFrom(to);
    setTo(from);
    setText(result || text);
    setResult("");
  }

  return (
    <main className="app">
      <h1>🌐 Translator</h1>
      <p className="subtitle">Translate text between languages.</p>

      <form className="card" onSubmit={handleTranslate}>
        <div className="lang-row">
          <label>
            From
            <select value={from} onChange={(e) => setFrom(e.target.value)}>
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="swap" onClick={swap} title="Swap languages">
            ⇄
          </button>
          <label>
            To
            <select value={to} onChange={(e) => setTo(e.target.value)}>
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to translate..."
          rows={4}
        />

        <button type="submit" className="translate" disabled={loading}>
          {loading ? "Translating…" : "Translate"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="card result" aria-live="polite">
          <span className="result-label">Translation</span>
          <p className="result-text">{result}</p>
        </div>
      )}
    </main>
  );
}
