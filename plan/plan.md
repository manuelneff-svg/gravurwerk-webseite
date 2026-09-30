# Gravurwerk Schweiz – Anfrage-Mails reparieren

Das Anfrageformular soll jede Absendung zuverlässig als E-Mail zustellen, statt „Senden fehlgeschlagen" zu zeigen.
Anfragen landen sicher im Postfach, die anfragende Person bekommt eine Bestätigung, und nichts geht verloren.

## Für wen
Betreiber von gravurwerkschweiz.ch, die Kundenanfragen (Gravur-Wünsche) verlässlich erhalten wollen, sowie Besucher, die über das Formular „Anfrage senden" eine unverbindliche Anfrage stellen.

## Kernfunktionen und Erlebnis
- **Funktionierendes Anfrageformular**: Produkt-Auswahl (z. B. Handyhülle), Wunsch-Text und Kontaktangaben werden abgeschickt und zuverlässig verarbeitet.
- **E-Mail an den Betrieb**: Jede Anfrage geht als sauber formatierte E-Mail an anfrage@gravurwerkschweiz.ch. Antworten auf diese Mail gehen direkt an die anfragende Person zurück.
- **Automatische Bestätigungsmail**: Die anfragende Person erhält sofort eine Eingangsbestätigung mit Zusammenfassung ihrer Anfrage und dem Hinweis „Antwort innert 24 h".
- **Sicheres Backup in der Datenbank**: Jede Anfrage wird gespeichert, auch wenn der Mailversand einmal ausfällt – so geht keine Anfrage verloren.
- **Klare Rückmeldung im Formular**: Erfolgsmeldung nach dem Senden bzw. eine verständliche Fehlermeldung nur dann, wenn wirklich etwas nicht klappt.

## Nutzerablauf
1. Besucher wählt das Produkt, schreibt seinen Wunsch und gibt seine Kontaktdaten (E-Mail, optional Name) an.
2. Besucher tippt auf „Anfrage senden".
3. Anfrage wird gespeichert, eine E-Mail geht an den Betrieb, eine Bestätigung an den Besucher.
4. Besucher sieht eine Erfolgsmeldung; der Betrieb findet die Anfrage im Postfach und kann direkt antworten.

## UI/UX-Gefühl
Bestehende dunkle Optik mit Cyan-Akzenten (wie im Screenshot) bleibt erhalten. Nur das Verhalten des Formulars und die Zustände (Senden läuft, Erfolg, Fehler) werden verlässlich gemacht; keine optische Neugestaltung.

## Umsetzungsphasen

**Phase 1 – MVP (wird jetzt gebaut)**
- Anfrageformular mit Feldern Produkt, Wunsch-Text, E-Mail (und optional Name).
- Absenden speichert die Anfrage und versendet E-Mail an den Betrieb via Resend.
- Automatische Bestätigungsmail an die anfragende Person.
- Klare Erfolgs-/Fehleranzeige im Formular; Reply-To zeigt auf die anfragende Person.

**Phase 2 – später**
- Einfache Admin-Ansicht, um gespeicherte Anfragen im Browser durchzusehen und zu filtern.
- Datei-/Bild-Upload zur Anfrage (z. B. Vorlage für die Gravur).
- Spam-Schutz (z. B. Honeypot/Rate-Limit) und Pflichtfeld-Validierung ausbauen.

**Phase 3 – später**
- Statusverfolgung je Anfrage (neu / in Arbeit / beantwortet) mit Benachrichtigungen.
- Export der Anfragen und Anbindung an bestehende Tools.

## Annahmen
- Zieladresse für Anfragen: anfrage@gravurwerkschweiz.ch.
- E-Mail-Versand über die von Emergent verwaltete Resend-Integration (kein API-Key nötig); der sichtbare Absender-Name ist „Gravurwerk Schweiz", die Absenderadresse ist die verwaltete Plattform-Adresse.
- Die anfragende Person erhält eine Bestätigungsmail; Antworten des Betriebs gehen per Reply-To an die anfragende Person.
- Jede Anfrage wird zusätzlich in der Datenbank gespeichert.
- In diesem Arbeitsbereich liegt aktuell nur die Standard-Vorlage, nicht der komplette Code der Live-Seite. Der Anfrage-Ablauf (Formular + Mailversand) wird hier in derselben dunklen Cyan-Optik neu aufgebaut, damit er funktioniert; die restlichen Seiteninhalte sind nicht Teil dieser Aufgabe.
- Pflichtfelder: Wunsch-Text und eine gültige E-Mail-Adresse der anfragenden Person (nötig für Bestätigung und Antwort).
