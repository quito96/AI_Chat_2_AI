#!/bin/bash
# start_app.sh - Startet die Streamlit AI Discussion App

echo "🚀 Starte AI Multi-Model Discussion System..."
echo "📍 Die App wird unter http://localhost:8588 verfügbar sein"
echo ""

# Prüfe ob uv installiert ist
if ! command -v uv &> /dev/null; then
    echo "❌ uv ist nicht installiert. Bitte installieren Sie uv zuerst:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Prüfe ob .env Datei existiert
if [ ! -f ".env" ]; then
    echo "⚠️  Warnung: .env Datei nicht gefunden!"
    echo "Bitte erstellen Sie eine .env Datei mit Ihren API-Keys:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "ANTHROPIC_API_KEY=your_key_here"
    echo ""
fi

# Starte die App
echo "🔄 Synchronisiere Abhängigkeiten..."
uv sync --quiet

echo "🎨 Starte Streamlit App..."
uv run streamlit run app.py

echo ""
echo "👋 App wurde beendet. Auf Wiedersehen!"

