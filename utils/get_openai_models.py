import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

class OpenAIModelsClient:
    """
    Client zum Abrufen verfügbarer Modelle von der OpenAI API
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den Client mit API-Key

        Args:
            api_key: OpenAI API-Schlüssel. Falls None, wird aus Umgebungsvariablen gelesen.
        """
        # Lade Umgebungsvariablen aus .env Datei
        load_dotenv()

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API-Key ist erforderlich. Setzen Sie OPENAI_API_KEY in .env oder übergeben Sie ihn direkt.")

        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_models(self) -> Dict[str, Any]:
        """
        Ruft die Liste verfügbarer Modelle ab

        Returns:
            Dictionary mit Modellinformationen
        """
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der Modelle: {e}")
            return {}

    def list_model_names(self) -> List[str]:
        """
        Gibt eine Liste der verfügbaren Modellnamen zurück

        Returns:
            Liste der Modellnamen
        """
        models_data = self.get_models()
        if 'data' in models_data:
            return [model.get('id', 'Unbekannt') for model in models_data['data']]
        return []

    def filter_models_by_type(self, model_type: str = None) -> List[Dict[str, Any]]:
        """
        Filtert Modelle nach Typ (z.B. 'gpt-4', 'gpt-3.5', 'dall-e', 'whisper', 'tts')

        Args:
            model_type: Typ oder Teilstring des Modellnamens zum Filtern

        Returns:
            Liste gefilterter Modelle
        """
        models_data = self.get_models()
        if not models_data or 'data' not in models_data:
            return []

        if not model_type:
            return models_data['data']

        return [
            model for model in models_data['data']
            if model_type.lower() in model.get('id', '').lower()
        ]

    def get_chat_models(self) -> List[Dict[str, Any]]:
        """
        Gibt nur Chat-Modelle zurück (GPT-Modelle)

        Returns:
            Liste der Chat-Modelle
        """
        chat_keywords = ['gpt-4', 'gpt-3.5', 'gpt-3', 'chatgpt']
        models_data = self.get_models()

        if not models_data or 'data' not in models_data:
            return []

        chat_models = []
        for model in models_data['data']:
            model_id = model.get('id', '').lower()
            if any(keyword in model_id for keyword in chat_keywords):
                chat_models.append(model)

        return chat_models

    def display_models_info(self) -> None:
        """
        Zeigt detaillierte Informationen über verfügbare Modelle an
        """
        models_data = self.get_models()

        if not models_data:
            print("Keine Modelle gefunden oder Fehler beim Abrufen.")
            return

        print("=== OpenAI Verfügbare Modelle ===\n")

        if 'data' in models_data:
            # Sortiere Modelle alphabetisch
            sorted_models = sorted(models_data['data'], key=lambda x: x.get('id', ''))

            for i, model in enumerate(sorted_models, 1):
                print(f"{i:3d}. Modell ID: {model.get('id', 'Unbekannt')}")
                print(f"     Objekt-Typ: {model.get('object', 'Unbekannt')}")
                print(f"     Erstellt: {self._format_timestamp(model.get('created', 0))}")
                print(f"     Besitzer: {model.get('owned_by', 'Unbekannt')}")

                # Weitere verfügbare Felder anzeigen
                for key, value in model.items():
                    if key not in ['id', 'object', 'created', 'owned_by']:
                        print(f"     {key.capitalize()}: {value}")
                print()

        # Zusammenfassung
        total_models = len(models_data.get('data', []))
        print(f"Gesamt: {total_models} Modelle verfügbar")

        # Chat-Modelle hervorheben
        chat_models = self.get_chat_models()
        print(f"Davon {len(chat_models)} Chat-Modelle (GPT)")

    def display_chat_models_only(self) -> None:
        """
        Zeigt nur Chat-Modelle (GPT-Modelle) an
        """
        chat_models = self.get_chat_models()

        if not chat_models:
            print("Keine Chat-Modelle gefunden.")
            return

        print("=== OpenAI Chat-Modelle (GPT) ===\n")

        for i, model in enumerate(chat_models, 1):
            print(f"{i:2d}. {model.get('id', 'Unbekannt')}")
            print(f"    Besitzer: {model.get('owned_by', 'Unbekannt')}")
            print(f"    Erstellt: {self._format_timestamp(model.get('created', 0))}")
            print()

    def _format_timestamp(self, timestamp: int) -> str:
        """
        Formatiert Unix-Timestamp zu lesbarem Datum

        Args:
            timestamp: Unix-Timestamp

        Returns:
            Formatiertes Datum
        """
        if timestamp == 0:
            return "Unbekannt"

        try:
            from datetime import datetime
            return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")
        except:
            return f"Timestamp: {timestamp}"

    def save_models_to_file(self, filename: str = "openai_models.json") -> bool:
        """
        Speichert Modellinformationen in einer JSON-Datei

        Args:
            filename: Name der Ausgabedatei

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            models_data = self.get_models()
            if models_data:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(models_data, f, indent=2, ensure_ascii=False)
                print(f"Modellinformationen gespeichert in: {filename}")
                return True
            else:
                print("Keine Daten zum Speichern verfügbar.")
                return False
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

    def search_models(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Sucht nach Modellen basierend auf einem Suchbegriff

        Args:
            search_term: Suchbegriff für Modellnamen

        Returns:
            Liste passender Modelle
        """
        models_data = self.get_models()
        if not models_data or 'data' not in models_data:
            return []

        search_term = search_term.lower()
        matching_models = [
            model for model in models_data['data']
            if search_term in model.get('id', '').lower()
        ]

        return matching_models

def main():
    """
    Hauptfunktion zum Ausführen des Programms
    """
    try:
        print("OpenAI Modelle Abfrage Tool")
        print("=" * 40)

        # Client initialisieren
        client = OpenAIModelsClient()

        while True:
            print("\nWählen Sie eine Option:")
            print("1. Alle Modelle anzeigen")
            print("2. Nur Chat-Modelle anzeigen (GPT)")
            print("3. Nach Modell suchen")
            print("4. Modelle nach Typ filtern")
            print("5. Daten in JSON-Datei speichern")
            print("6. Beenden")

            choice = input("\nIhre Auswahl (1-6): ").strip()

            if choice == '1':
                client.display_models_info()

            elif choice == '2':
                client.display_chat_models_only()

            elif choice == '3':
                search_term = input("Suchbegriff eingeben: ").strip()
                if search_term:
                    matching_models = client.search_models(search_term)
                    if matching_models:
                        print(f"\nGefundene Modelle für '{search_term}':")
                        for model in matching_models:
                            print(f"  - {model.get('id', 'Unbekannt')}")
                    else:
                        print(f"Keine Modelle gefunden für '{search_term}'")

            elif choice == '4':
                model_type = input("Modelltyp eingeben (z.B. 'gpt-4', 'whisper', 'dall-e'): ").strip()
                if model_type:
                    filtered_models = client.filter_models_by_type(model_type)
                    if filtered_models:
                        print(f"\nModelle vom Typ '{model_type}':")
                        for model in filtered_models:
                            print(f"  - {model.get('id', 'Unbekannt')}")
                    else:
                        print(f"Keine Modelle vom Typ '{model_type}' gefunden")

            elif choice == '5':
                filename = input("Dateiname (Enter für 'openai_models.json'): ").strip()
                if not filename:
                    filename = "openai_models.json"
                client.save_models_to_file(filename)

            elif choice == '6':
                print("Programm beendet.")
                break

            else:
                print("Ungültige Auswahl. Bitte wählen Sie 1-6.")

    except ValueError as e:
        print(f"Konfigurationsfehler: {e}")
        print("\nHinweise:")
        print("1. Erstellen Sie eine .env Datei mit OPENAI_API_KEY=ihr_api_key")
        print("2. Oder setzen Sie die Umgebungsvariable OPENAI_API_KEY")
        print("3. Holen Sie sich einen API-Key von https://platform.openai.com/api-keys")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    main()