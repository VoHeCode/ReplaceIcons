# BuildIconizer

Massen-Bildersetzung mit automatischer Transformation für identische Bildgrößen.

## Features

- 🔍 Rekursive Dateisuche mit Filter
- 🖼️ Automatische Bildtransformation (Fit-Modus, Farbmodus-Anpassung)
- 💾 Einzeln oder alle Dateien auf einmal ersetzen
- ⚡ Asynchrone Verarbeitung (UI blockiert nicht)
- 👁️ Live-Vorschau der Transformation

## Installation

```bash
pip install -e .
```

## Usage

```bash
python main.py
```

### Workflow

1. **Verzeichnis wählen** und nach Bildern suchen
2. **Primärbild** aus der Liste auswählen
3. **Ersatzbild** hochladen (wird automatisch transformiert)
4. **Einzeln ersetzen** oder **Alle ersetzen**

## Technologie

- **Flet** - Desktop UI
- **Pillow** - Bildverarbeitung
- **Async** - Non-blocking UI

## Transformation

Das Ersatzbild wird automatisch:
- Auf die Größe des Zielbildes skaliert (Fit-Modus)
- Zentriert mit transparentem Padding
- In den Farbmodus des Zielbildes konvertiert
