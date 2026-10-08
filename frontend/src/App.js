import "@/App.css";
import { Zap, Mail, Facebook, ArrowUpRight, Crosshair, Menu } from "lucide-react";

const CONTACT_EMAIL = "anfrage@gravurwerkschweiz.ch";
const FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61595086887343";
const MAILTO = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent("Anfrage Gravur")}`;

function App() {
  return (
    <div className="gw-root" data-testid="app-root">
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
          <a className="gw-cta-pill" href={MAILTO} data-testid="header-cta-button">
            <Zap size={18} strokeWidth={2.5} />
            Jetzt anfragen
          </a>
          <a className="gw-menu" href={MAILTO} aria-label="E-Mail schreiben" data-testid="menu-button">
            <Menu size={26} />
          </a>
        </div>
      </header>

      {/* Main */}
      <main className="gw-main">
        {/* Direct contact card */}
        <section className="gw-card" data-testid="contact-card">
          <span className="gw-eyebrow">Kontakt</span>
          <h1 className="gw-title">Schreib uns direkt</h1>
          <p className="gw-lead">
            Erzähl uns, was du gravieren möchtest – Produkt und Wunsch genügen.
            Wir antworten <strong>innert 24 h</strong>.
          </p>

          <a className="gw-submit" href={MAILTO} data-testid="email-cta-button">
            <Mail size={20} strokeWidth={2.5} />
            E-Mail senden
          </a>

          <a className="gw-mail-line" href={MAILTO} data-testid="email-address-link">
            {CONTACT_EMAIL}
          </a>

          <p className="gw-note">100% unverbindlich · Antwort innert 24 h</p>
        </section>

        {/* Facebook card */}
        <a
          className="gw-fb-card"
          href={FACEBOOK_URL}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="facebook-link"
        >
          <div className="gw-fb-icon">
            <Facebook size={26} strokeWidth={2.4} />
          </div>
          <div className="gw-fb-body">
            <span className="gw-eyebrow">Neueste Produkte</span>
            <h2 className="gw-fb-title">
              Folge uns auf Facebook
              <ArrowUpRight size={20} className="gw-fb-arrow" />
            </h2>
            <p className="gw-fb-text">
              Auf <strong>Gravurwerk Schweiz</strong> siehst du laufend unsere
              neuesten Gravuren und Produkte.
            </p>
          </div>
        </a>
      </main>
    </div>
  );
}

export default App;
