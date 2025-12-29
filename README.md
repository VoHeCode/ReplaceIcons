# ReplaceIcons

Ein Tool zur schnellen und konsistenten Ersetzung vieler Bilddateien, inklusive automatischer Größen‑ und Farbmodus‑Anpassung. Ideal für Icon‑Sets, UI‑Assets oder andere Bildsammlungen, die einheitlich aktualisiert werden müssen.

Beim Arbeiten mit `flet build apk` habe ich in der generierten Struktur zahlreiche Icon‑Ordner gefunden – allerdings enthalten sie ausschließlich das Standard‑Flet‑Icon. 

## Typische Flet-Build-Struktur

Nach `flet build apk` findest du die Icons hier:

```
MeinProjekt/
├── main.py
├── assets/
├── build/
│   └── flutter/
│       └── android/
│           └── app/
│               └── src/
│                   └── main/
│                       └── res/
│                           ├── mipmap-hdpi/
│                           │   └── ic_launcher.png        (72×72)
│                           ├── mipmap-mdpi/
│                           │   └── ic_launcher.png        (48×48)
│                           ├── mipmap-xhdpi/
│                           │   └── ic_launcher.png        (96×96)
│                           ├── mipmap-xxhdpi/
│                           │   └── ic_launcher.png        (144×144)
│                           ├── mipmap-xxxhdpi/
│                           │   └── ic_launcher.png        (192×192)
│                           └── drawable-*/
│                               └── weitere Icons...
```

Mit diesem Tool lassen sich alle diese Icons durch ein eigenes Muster ersetzen, einzeln oder gesammelt. Das Vorlagebild sollte ausreichend groß sein (z. B. 1024×1024 Pixel). Die App lädt jedes gefundene Bild aus allen Unterordnern, analysiert Größe, Farbtiefe und Alphakanal und transformiert das Musterbild entsprechend, bevor es das Zielicon ersetzt.

## Features

- 🔍 Rekursive Dateisuche mit Filter
- 🖼️ Automatische Bildtransformation (Fit-Modus, Farbmodus-Anpassung)
- 💾 Einzeln oder alle Dateien auf einmal ersetzen
- ⚡ Asynchrone Verarbeitung (UI blockiert nicht)
- 👁️ Live-Vorschau der Transformation
- 🌐 Mehrsprachige Oberfläche (i18n-Support)

## Installation

```bash
pip install -e .
```

## Usage

```bash
python main.py
```

### Workflow

1. **Verzeichnis wählen** und nach Bildern suchen (z.B. `*.png`)
2. **Primärbild** aus der Liste auswählen (Zielbild)
3. **Ersatzbild** hochladen (wird automatisch transformiert)
4. **Vorschau prüfen** - das Ersatzbild wird angezeigt wie es nach der Transformation aussieht
5. **Einzeln ersetzen** oder **Alle ersetzen**

### Beispiel: Flet APK Icons ersetzen

```bash
# Navigiere zum res-Verzeichnis deines Flet-Projekts
cd build/flutter/android/app/src/main/res/

# Starte ReplaceIcons
python /pfad/zu/ReplaceIcons/main.py

# In der App:
# 1. Wähle das res-Verzeichnis (enthält alle mipmap-* Ordner)
# 2. Filter: *.png
# 3. Ersatzbild: dein-icon-1024x1024.png
# 4. Klicke "ALLE ERSETZEN"
```

## Technologie

- **Flet** - Desktop UI
- **Pillow** - Bildverarbeitung
- **Async** - Non-blocking UI
- **i18n** - Mehrsprachigkeit via TranslationSystem

## Transformation

Das Ersatzbild wird automatisch:
- Auf die Größe des Zielbildes skaliert (Fit-Modus, aspect ratio bleibt erhalten)
- Zentriert mit transparentem Padding
- In den Farbmodus des Zielbildes konvertiert (RGB, RGBA, etc.)

## Struktur

```
ReplaceIcons/
├── main.py              # Hauptanwendung
├── translator.py        # i18n-System
├── assets/
│   └── locales/        # Übersetzungsdateien
│       ├── main_de_DE.json
│       └── main_en_US.json
├── pyproject.toml
├── .gitignore
└── README.md
```

## Sprachen hinzufügen

1. Kopiere eine bestehende Locale-Datei (z.B. `main_de_DE.json`) nach `assets/locales/main_en_US.json`
2. Öffne den Translation-Editor mit:
   ```bash
   python -c "from translator import TranslationSystem; TranslationSystem().run_tr_extractor_ui()"
   ```
3. Wähle im Editor die neue Locale (`en_US`) und bearbeite die Übersetzungen
4. Speichere - fertig! Die neue Sprache erscheint automatisch im Dropdown
