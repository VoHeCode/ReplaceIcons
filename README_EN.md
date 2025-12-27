# ReplaceIcons

A tool for quick and consistent replacement of many image files, including automatic size and color mode adjustment. Ideal for icon sets, UI assets, or other image collections that need to be updated uniformly.

When working with `flet build apk`, I found numerous icon folders in the generated structure – but they only contain the default Flet icon.

## Typical Flet Build Structure

After `flet build apk` you'll find the icons here:

```
MyProject/
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
│                               └── more icons...
```

With this tool, you can replace all these icons with your own template, individually or all at once. The template image should be sufficiently large (e.g., 1024×1024 pixels). The app loads each image found in all subdirectories, analyzes size, color depth, and alpha channel, and transforms the template image accordingly before replacing the target icon.

## Features

- 🔍 Recursive file search with filter
- 🖼️ Automatic image transformation (fit mode, color mode adjustment)
- 💾 Replace individually or all at once
- ⚡ Asynchronous processing (UI doesn't block)
- 👁️ Live preview of transformation
- 🌐 Multilingual interface (i18n support)

## Installation

```bash
pip install -e .
```

## Usage

```bash
python main.py
```

### Workflow

1. **Choose directory** and search for images (e.g., `*.png`)
2. **Select primary image** from the list (target image)
3. **Upload replacement image** (automatically transformed)
4. **Check preview** - the replacement image is shown as it will look after transformation
5. **Replace individually** or **Replace all**

### Example: Replace Flet APK Icons

```bash
# Navigate to the res directory of your Flet project
cd build/flutter/android/app/src/main/res/

# Start ReplaceIcons
python /path/to/ReplaceIcons/main.py

# In the app:
# 1. Select the res directory (contains all mipmap-* folders)
# 2. Filter: *.png
# 3. Replacement image: your-icon-1024x1024.png
# 4. Click "REPLACE ALL"
```

## Technology

- **Flet** - Desktop UI
- **Pillow** - Image processing
- **Async** - Non-blocking UI
- **i18n** - Multilingual support via TranslationSystem

## Transformation

The replacement image is automatically:
- Scaled to the target image size (fit mode, aspect ratio preserved)
- Centered with transparent padding
- Converted to the target image color mode (RGB, RGBA, etc.)

## Structure

```
ReplaceIcons/
├── main.py              # Main application
├── translator.py        # i18n system
├── assets/
│   └── locales/        # Translation files
│       ├── main_de_DE.json
│       └── main_en_US.json
├── pyproject.toml
├── .gitignore
└── README.md
```

## Adding Languages

1. Copy an existing locale file (e.g., `main_de_DE.json`) to `assets/locales/main_en_US.json`
2. Open the translation editor with:
   ```bash
   python -c "from translator import TranslationSystem; TranslationSystem().run_tr_extractor_ui()"
   ```
3. Select the new locale (`en_US`) in the editor and edit the translations
4. Save - done! The new language appears automatically in the dropdown
