#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""BuildIconizer - Massen-Bildersetzung mit automatischer Transformation."""

import asyncio
import base64
import io
import os
from glob import glob
from pathlib import Path

import flet as ft
from PIL import Image
from translator import TranslationSystem

# Translator Setup
ts = TranslationSystem()
_ = ts.tr


def main(page: ft.Page):
    """Hauptfunktion der Anwendung."""
    # Page-Konfiguration
    page.title = _("Flet Massen-Bildsynchronisation")
    page.window_width = 1300
    page.window_height = 700
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 15

    # Zustandsvariablen für aktuelles Primärbild
    selected_directory_path = ""
    current_primary_width = 0
    current_primary_height = 0
    current_primary_mode = ""

    def apply_transformation(source_img_path, target_width, target_height, target_mode):
        """
        Transformiert ein Bild mit Fit-Modus auf Zielgröße.

        Args:
            source_img_path: Pfad zum Quellbild
            target_width: Zielbreite
            target_height: Zielhöhe
            target_mode: Ziel-Farbmodus (RGB, RGBA, etc.)

        Returns:
            Tuple[Image, int, int]: Transformiertes Bild, neue Breite, neue Höhe
        """
        # Als RGBA laden für Transparenz-Support
        img = Image.open(source_img_path).convert("RGBA")

        # Fit-Dimensionen berechnen (aspect ratio beibehalten)
        original_width, original_height = img.size
        ratio_w = target_width / original_width
        ratio_h = target_height / original_height
        scale_factor = min(ratio_w, ratio_h)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Skalieren und zentrieren
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        target_canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))

        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2

        target_canvas.paste(resized_img, (x_offset, y_offset))

        # Farbmodus konvertieren
        converted_img = target_canvas.convert(target_mode)

        return converted_img, new_width, new_height

    def transform_replacement_image(file_path):
        """Transformiert Ersatzbild auf Primärbild-Spezifikationen."""
        nonlocal current_primary_width, current_primary_height, current_primary_mode

        # Primärbild muss zuerst gewählt werden
        if current_primary_width == 0:
            replacement_image_label.value = _("Primärbild muss zuerst ausgewählt werden.")
            replacement_image_control.visible = False
            replace_button.disabled = True
            page.update()
            return

        try:
            # Transformation anwenden
            converted_img, new_width, new_height = apply_transformation(file_path, current_primary_width,
                                                                        current_primary_height, current_primary_mode, )

            # Als Base64 für Vorschau speichern
            buffer = io.BytesIO()
            converted_img.save(buffer, format="PNG")
            base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

            # UI aktualisieren
            replacement_image_control.src = ""
            replacement_image_control.src_base64 = base64_img
            replacement_image_control.data = file_path
            replacement_image_control.visible = True
            replace_button.disabled = False

            # Alle-Ersetzen aktivieren wenn Verzeichnis geladen
            if selected_directory_path:
                replace_all_button.disabled = False

            replacement_image_label.value = (_("Ersatzbild ({}) transformiert:\n").format(Path(file_path).name) +
                                             _("Größe: {}x{} zentriert in ").format(new_width, new_height) +
                                             _("{}x{} | ").format(current_primary_width, current_primary_height) +
                                             _("Modus: {}").format(current_primary_mode))

        except Exception as ex:
            print(_("[LOG] FEHLER bei der Transformation: {}").format(ex))
            replacement_image_control.src_base64 = None
            replacement_image_control.visible = False
            replace_button.disabled = True
            replace_all_button.disabled = True
            replacement_image_label.value = _("Ersatzbild: Transformation fehlgeschlagen ({})").format(ex)

        page.update()

    def replacement_picker_result(e: ft.FilePickerResultEvent):
        """Callback für Ersatzbild-Auswahl."""
        if e.files:
            file_path = e.files[0].path
            transform_replacement_image(file_path)
        else:
            replacement_image_label.value = _("Ersatzbild: Auswahl abgebrochen.")
            page.update()

    def replace_file(e):
        """Ersetzt das aktuell ausgewählte Primärbild."""
        # Validierung
        if not replacement_image_control.data or not image_control.src:
            selected_dir_text.value = _("Fehler: Primär- und Ersatzbild müssen ausgewählt sein.")
            page.update()
            return

        target_path = image_control.src
        base64_img = replacement_image_control.src_base64

        try:
            # Base64 zurück in PIL Image konvertieren
            img_bytes = base64.b64decode(base64_img)
            img_to_save = Image.open(io.BytesIO(img_bytes))

            # Speichern und UI aktualisieren
            img_to_save.save(target_path)

            selected_dir_text.value = _("✅ ERFOLG: Datei ersetzt! Neuer Inhalt von '{}' gespeichert.").format(
                Path(target_path).name)

            replace_button.disabled = True
            replace_all_button.disabled = True
            image_control.src = target_path
            replacement_image_control.visible = False
            replacement_image_label.value = _("Ersatzbild erfolgreich gespeichert und entfernt.")

            page.update()
            start_search(None)

        except Exception as ex:
            print(_("[LOG] FEHLER beim Ersetzen: {}").format(ex))
            selected_dir_text.value = _("❌ FEHLER beim Ersetzen von {}: {}").format(Path(target_path).name, ex)
            replace_button.disabled = False

        page.update()

    async def replace_all_files(e):
        """Ersetzt alle gefundenen Dateien asynchron (UI blockiert nicht)."""
        global _  # IDE-Hint für async Funktion

        # Validierung
        if not replacement_image_control.data:
            selected_dir_text.value = _("Fehler: Zuerst ein Ersatzbild auswählen.")
            page.update()
            return

        if not file_list_view.controls:
            selected_dir_text.value = _("Fehler: Zuerst Dateien suchen.")
            page.update()
            return

        # Buttons während Verarbeitung deaktivieren
        replace_all_button.disabled = True
        replace_button.disabled = True
        action_button.disabled = True

        selected_dir_text.value = _("🤖 START: Verarbeite alle gefundenen Dateien...")
        page.update()

        source_replacement_path = replacement_image_control.data
        success_count = 0
        total_count = len(file_list_view.controls)

        try:
            for index, list_tile in enumerate(file_list_view.controls):
                target_path = list_tile.data

                # Primärbild-Eigenschaften ermitteln
                img_primary = Image.open(target_path)
                target_width, target_height = img_primary.size
                target_mode = img_primary.mode

                # Progress alle 5 Dateien aktualisieren
                if index % 5 == 0:
                    selected_dir_text.value = (
                        _("🤖 VERARBEITE ({}/{}): {}...").format(index + 1, total_count, Path(target_path).name))
                    await page.update_async()
                    await asyncio.sleep(0.01)  # UI-Refresh ermöglichen

                # Transformation anwenden und speichern
                converted_img, _, _ = apply_transformation(source_replacement_path, target_width, target_height,
                                                           target_mode)
                converted_img.save(target_path)
                success_count += 1

            # Erfolgsbestätigung
            selected_dir_text.value = _("✅ FERTIG: {} von {} Dateien erfolgreich ersetzt!").format(success_count,
                                                                                                   total_count)

            replacement_image_control.visible = False
            replacement_image_label.value = _("Ersatzbild erfolgreich auf alle Dateien angewendet.")

            await page.update_async()
            start_search(None)

        except Exception as ex:
            selected_dir_text.value = _("❌ FEHLER bei der Massenverarbeitung bei Datei {}: {}").format(index + 1, ex)
            print(_("[LOG] FEHLER bei Massenverarbeitung: {}").format(ex))

        finally:
            # Buttons wieder aktivieren
            replace_all_button.disabled = False
            action_button.disabled = False
            replace_button.disabled = True
            page.update()

    def show_image_details(e):
        """Zeigt Details des ausgewählten Bildes und aktualisiert Primärbild."""
        nonlocal current_primary_width, current_primary_height, current_primary_mode
        file_path = e.control.data

        try:
            img = Image.open(file_path)

            # Primärbild-Eigenschaften setzen
            current_primary_width, current_primary_height = img.size
            current_primary_mode = img.mode

            # Eigenschaften-Liste erstellen
            props_list = [_("Pfad: {}").format(file_path),
                          _("Format: {}").format(img.format),
                          _("Breite: {} px (Zielbreite)").format(current_primary_width),
                          _("Höhe: {} px (Zielhöhe)").format(current_primary_height),
                          _("Farbmodus: {} (Zielmodus)").format(current_primary_mode),
                          _("Alphakanal: {}").format(_('Ja') if 'A' in current_primary_mode else _('Nein')),
                          _("Größe: {:.2f} MB").format(os.path.getsize(file_path) / (1024 * 1024)), ]

            image_properties_text.value = "\n".join(props_list)
            image_control.src = file_path
            image_control.visible = True

            # Ersatzbild neu transformieren falls vorhanden
            if replacement_image_control.data:
                transform_replacement_image(replacement_image_control.data)

        except Exception as ex:
            image_properties_text.value = _("Fehler beim Laden/Parsen des Bildes: {}").format(ex)
            image_control.visible = False
            replace_button.disabled = True
            replace_all_button.disabled = True

        page.update()

    def start_search(e):
        """Startet die Dateisuche im ausgewählten Verzeichnis."""
        nonlocal selected_directory_path

        if not selected_directory_path:
            selected_dir_text.value = _("Fehler: Zuerst ein Verzeichnis auswählen.")
            page.update()
            return

        file_filter = filter_input.value.strip() or "*"
        file_list_view.controls.clear()

        try:
            # Rekursive Suche
            search_path = str(Path(selected_directory_path) / "**" / file_filter)
            found_files = glob(search_path, recursive=True)

            if found_files:
                # Liste mit gefundenen Dateien füllen
                for file_path in found_files:
                    file_list_view.controls.append(ft.ListTile(title=ft.Text(Path(file_path).name, size=12),
                                                               subtitle=ft.Text(str(Path(file_path).parent), size=10),
                                                               data=file_path,
                                                               on_click=show_image_details, dense=True,
                                                               hover_color=ft.Colors.BLUE_GREY_100, ))
                selected_dir_text.value = (_("Verzeichnis: {}\n").format(selected_directory_path) +
                                           _("Filter: {} | {} Dateien gefunden.").format(file_filter, len(found_files)))
            else:
                selected_dir_text.value = (_("Verzeichnis: {}\n").format(selected_directory_path) +
                                           _("Filter: {} | Keine Dateien gefunden.").format(file_filter))

        except Exception as ex:
            selected_dir_text.value = _("Fehler bei der Suche: {}").format(ex)

        page.update()

    def directory_picker_result(e: ft.FilePickerResultEvent):
        """Callback für Verzeichnis-Auswahl."""
        nonlocal selected_directory_path

        if e.path:
            selected_directory_path = e.path
            selected_dir_text.value = _("Verzeichnis ausgewählt: {}").format(selected_directory_path)

            # Button zu Suchen umwandeln
            action_button.text = _("Suchen starten")
            action_button.icon = ft.Icons.SEARCH
            action_button.on_click = start_search

            # Alle-Ersetzen aktivieren falls Ersatzbild vorhanden
            if replacement_image_control.data:
                replace_all_button.disabled = False
        else:
            selected_dir_text.value = _("Verzeichnisauswahl abgebrochen.")

        page.update()

    def exit_app(e):
        """Beendet die Anwendung."""
        page.window.close()

    def on_locale_change(e):
        """Callback für Sprachwechsel."""
        if not locale_dropdown.value:
            return
        ts.set_locale(locale_dropdown.value)
        page.clean()
        build_ui()

    def build_ui():
        """Baut die komplette UI auf."""
        nonlocal image_control, image_properties_text, image_container
        nonlocal replacement_image_control, replacement_image_container, replacement_image_label
        nonlocal filter_input, selected_dir_text, file_list_view
        nonlocal action_button, replace_button, replace_all_button, exit_button
        nonlocal directory_picker, replacement_file_picker, locale_dropdown

        # --- UI-KOMPONENTEN INITIALISIERUNG ---

        # Primärbild-Anzeige
        image_control = ft.Image(src="", visible=False, fit=ft.ImageFit.CONTAIN)
        image_properties_text = ft.Text(_("Wähle eine Datei aus der Liste."), size=14)
        image_container = ft.Container(content=image_control, width=300, height=250, alignment=ft.alignment.center,
                                       bgcolor=ft.Colors.BLACK45, )

        # Ersatzbild-Anzeige
        replacement_image_control = ft.Image(src_base64=None, visible=False, data=None, fit=ft.ImageFit.CONTAIN)
        replacement_image_container = ft.Container(content=replacement_image_control, width=300, height=250,
                                                   alignment=ft.alignment.center, bgcolor=ft.Colors.BLUE_GREY_100, )
        replacement_image_label = ft.Text(_("Ersatzbild noch nicht ausgewählt."), size=14)

        # Eingabefelder und Listen
        filter_input = ft.TextField(label=_("Dateifilter"), value="*.jpg", width=150, height=40, dense=True)
        selected_dir_text = ft.Text(_("Bitte ein Startverzeichnis auswählen."), size=14)
        file_list_view = ft.ListView(expand=True, spacing=1, auto_scroll=False)

        # Sprach-Dropdown
        available_locales = ts.list_locales()
        locale_dropdown = ft.Dropdown(
            label=_("Sprache"),
            options=[ft.dropdown.Option(loc) for loc in available_locales],
            value=ts.get_locale(),
            on_change=on_locale_change,
            width=150,
        )

        # Action-Buttons
        action_button = ft.ElevatedButton(_("Verzeichnis auswählen..."), icon=ft.Icons.FOLDER_OPEN, width=200)

        replace_button = ft.ElevatedButton(_("Bild ersetzen (ACHTUNG!)"), icon=ft.Icons.SAVE, bgcolor=ft.Colors.RED_700,
                                           color=ft.Colors.WHITE, on_click=replace_file, disabled=True, )

        replace_all_button = ft.ElevatedButton(_("ALLE ERSETZEN"), icon=ft.Icons.AUTORENEW, bgcolor=ft.Colors.RED_900,
                                               color=ft.Colors.WHITE, on_click=replace_all_files, disabled=True, )

        exit_button = ft.ElevatedButton(_("Beenden"), icon=ft.Icons.EXIT_TO_APP, bgcolor=ft.Colors.GREY_700,
                                        color=ft.Colors.WHITE, on_click=exit_app, )

        # FilePicker initialisieren
        directory_picker = ft.FilePicker(on_result=directory_picker_result)
        replacement_file_picker = ft.FilePicker(on_result=replacement_picker_result)
        page.overlay.extend([directory_picker, replacement_file_picker])
        dtitle = _("Wähle das Startverzeichnis")
        action_button.on_click = lambda _: directory_picker.get_directory_path(dialog_title=dtitle)

        # --- UI-LAYOUT AUFBAUEN ---
        dtitle2 = _("Wähle eine Ersatzdatei")
        page.add(  # Oberste Button-Row
            ft.Row([action_button, ft.VerticalDivider(), ft.Text(_("Filter:"), weight=ft.FontWeight.BOLD), filter_input,
                    ft.VerticalDivider(), ft.ElevatedButton(_("Ersatz-Datei auswählen"), icon=ft.Icons.CLOUD_UPLOAD,
                                                            on_click=lambda _: replacement_file_picker.pick_files(
                                                                allowed_extensions=["png", "jpg", "jpeg", "gif", "bmp"],
                                                                allow_multiple=False,
                                                                dialog_title=dtitle2, ), ),
                    ft.VerticalDivider(), replace_button,
                    replace_all_button, ft.VerticalDivider(), exit_button, ], alignment=ft.MainAxisAlignment.START, ),
            ft.Divider(),
            ft.Row([selected_dir_text, locale_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),  # Hauptbereich mit 3 Spalten
            ft.Row([  # Linke Spalte: Dateiliste
                ft.Column([ft.Text(_("Gefundene Dateien:"), weight=ft.FontWeight.BOLD),
                           ft.Container(content=file_list_view, border=ft.border.all(1, ft.Colors.BLACK45), width=350,
                                        height=450,
                                        padding=5, ), ], width=350, ), ft.VerticalDivider(),
                # Mittlere Spalte: Primärbild & Details
                ft.Column(
                    [ft.Text(_("Primärbild & Details:"), weight=ft.FontWeight.BOLD), image_container, ft.Divider(),
                     image_properties_text, ], width=350, ), ft.VerticalDivider(),  # Rechte Spalte: Ersatzbild
                ft.Column([ft.Text(_("Ersatzbild:"), weight=ft.FontWeight.BOLD), replacement_image_label,
                           replacement_image_container, ], width=350, ), ], expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START, ), )

    # Initialisiere UI-Komponenten Variablen
    image_control = None
    image_properties_text = None
    image_container = None
    replacement_image_control = None
    replacement_image_container = None
    replacement_image_label = None
    filter_input = None
    selected_dir_text = None
    file_list_view = None
    action_button = None
    replace_button = None
    replace_all_button = None
    exit_button = None
    directory_picker = None
    replacement_file_picker = None
    locale_dropdown = None

    # Baue UI initial auf
    build_ui()


if __name__ == "__main__":
    ft.app(target=main)
