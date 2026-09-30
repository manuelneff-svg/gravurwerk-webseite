import { useState } from "react";
import "@/App.css";
import axios from "axios";
import { Zap, Send, Menu, Crosshair, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PRODUCTS = [
  "Handyhülle",
  "Schlüsselanhänger",
  "Feuerzeug",
  "Trinkflasche",
  "Schmuck / Anhänger",
  "Holzschild",
  "Anderes",
];

function App() {
  const [product, setProduct] = useState(PRODUCTS[0]);
  const [wish, setWish] = useState("");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState("");

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const canSubmit = wish.trim().length > 0 && emailValid && status !== "loading";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setStatus("loading");
    setErrorMsg("");
    try {
      await axios.post(`${API}/inquiries`, {
        product,
        wish: wish.trim(),
        email: email.trim(),
        name: name.trim() || null,
      });
      setStatus("success");
      toast.success("Anfrage gesendet – wir melden uns innert 24 h.");
      setWish("");
      setName("");
      setEmail("");
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setStatus("error");
      setErrorMsg(
        typeof detail === "string"
          ? detail
          : "Senden fehlgeschlagen. Bitte versuche es erneut oder schreib direkt an anfrage@gravurwerkschweiz.ch."
      );
    }
  };

  return (
    <div className="gw-root" data-testid="app-root">
      <Toaster position="top-center" theme="dark" richColors />

      {/* Header */}
      <header className="gw-header">
        <div className="gw-header-inner">
          <div className="gw-brand" data-testid="brand-logo">
            <span className="gw-brand-mark">
              <Crosshair size={22} strokeWidth={2.5} />
              <span className="gw-flag">+</span>
            </span>
            <span className="gw-brand-text">
              GRAVURWERK<br />
              <span className="gw-brand-accent">SCHWEIZ</span>
            </span>
          </div>
          <button className="gw-cta-pill" data-testid="header-cta-button">
            <Zap size={18} strokeWidth={2.5} />
            Jetzt anfragen
          </button>
          <button className="gw-menu" aria-label="Menü" data-testid="menu-button">
            <Menu size={26} />
          </button>
        </div>
      </header>

      {/* Form */}
      <main className="gw-main">
        <div className="gw-card" data-testid="inquiry-card">
          <form onSubmit={handleSubmit}>
            <label className="gw-eyebrow">Produkt</label>
            <div className="gw-select-wrap">
              <select
                className="gw-select"
                value={product}
                onChange={(e) => setProduct(e.target.value)}
                data-testid="product-select"
              >
                {PRODUCTS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>

            <label className="gw-eyebrow gw-mt">Dein Name <span className="gw-optional">(optional)</span></label>
            <input
              className="gw-input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Vor- und Nachname"
              data-testid="name-input"
            />

            <label className="gw-eyebrow gw-mt">Deine E-Mail *</label>
            <input
              className="gw-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@beispiel.ch"
              data-testid="email-input"
            />

            <label className="gw-eyebrow gw-mt">Dein Wunsch *</label>
            <textarea
              className="gw-textarea"
              rows={4}
              value={wish}
              onChange={(e) => setWish(e.target.value)}
              placeholder="Beschreibe deine Gravur…"
              data-testid="wish-input"
            />

            <button
              type="submit"
              className="gw-submit"
              disabled={!canSubmit}
              data-testid="submit-button"
            >
              {status === "loading" ? (
                <>
                  <Loader2 size={20} className="gw-spin" /> Wird gesendet…
                </>
              ) : (
                <>
                  <Send size={20} strokeWidth={2.5} /> Anfrage senden
                </>
              )}
            </button>

            <p className="gw-note">100% unverbindlich · Antwort innert 24 h</p>

            {status === "success" && (
              <div className="gw-alert gw-alert-ok" data-testid="success-message">
                <CheckCircle2 size={22} />
                <div>
                  <strong>Anfrage gesendet</strong>
                  <p>Danke! Wir haben dir eine Bestätigung geschickt und melden uns innert 24 h.</p>
                </div>
              </div>
            )}

            {status === "error" && (
              <div className="gw-alert gw-alert-err" data-testid="error-message">
                <XCircle size={22} />
                <div>
                  <strong>Senden fehlgeschlagen</strong>
                  <p>{errorMsg}</p>
                </div>
              </div>
            )}
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
