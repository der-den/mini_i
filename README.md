# Inventardatenbank (mini_i)

Eine Webanwendung zur Verwaltung von Asservaten und Inventardaten.

## Funktionen

- Durchsuchen und Filtern der Inventardatenbank
- Detailansicht für einzelne Einträge mit Bearbeitungsmöglichkeit
- Scanner-Seite für Barcode-Scans
- Dropdown-Menüs für Place Status und Type
- Schreibschutz-Funktionalität für wichtige Felder
- Filterung nach Aktenzeichen

## Technologie

- Python mit Flask als Web-Framework
- SQLite-Datenbank
- Bootstrap für das Frontend
- JavaScript für interaktive Elemente

## Installation

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/der-den/mini_i.git
   cd mini_i
   ```

2. Erstellen Sie eine virtuelle Umgebung und installieren Sie die Abhängigkeiten:
   ```
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Starten Sie die Anwendung:
   ```
   python app.py
   ```

4. Öffnen Sie die Anwendung in Ihrem Browser unter `http://localhost:5000`
