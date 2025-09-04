import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

class AnthropicModelsClient:
    """
    Client zum Abrufen verfügbarer Modelle von der Anthropic API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den Client mit API-Key
        
        Args:
            api_key: Anthropic API-Schlüssel. Falls None, wird aus Umgebungsvariablen gelesen.
        """
        # Lade Umgebungsvariablen aus .env Datei
        load_dotenv()
        
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API-Key ist erforderlich. Setzen Sie ANTHROPIC_API_KEY in .env oder übergeben Sie ihn direkt.")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
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
    
    def display_models_info(self) -> None:
        """
        Zeigt detaillierte Informationen über verfügbare Modelle an
        """
        models_data = self.get_models()
        
        if not models_data:
            print("Keine Modelle gefunden oder Fehler beim Abrufen.")
            return
        
        print("=== Anthropic Verfügbare Modelle ===\n")
        
        if 'data' in models_data:
            for i, model in enumerate(models_data['data'], 1):
                print(f"{i}. Modell ID: {model.get('id', 'Unbekannt')}")
                print(f"   Typ: {model.get('type', 'Unbekannt')}")
                
                # Weitere verfügbare Felder anzeigen
                for key, value in model.items():
                    if key not in ['id', 'type']:
                        print(f"   {key.capitalize()}: {value}")
                print()
        
        # Metadaten anzeigen
        if 'first_id' in models_data:
            print(f"Erste ID: {models_data['first_id']}")
        if 'last_id' in models_data:
            print(f"Letzte ID: {models_data['last_id']}")
    
    def save_models_to_file(self, filename: str = "anthropic_models.json") -> bool:
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

def main():
    """
    Hauptfunktion zum Ausführen des Programms
    """
    try:
        print("Anthropic Modelle Abfrage Tool")
        print("=" * 40)
        
        # Client initialisieren
        client = AnthropicModelsClient()
        
        # Modelle abrufen und anzeigen
        client.display_models_info()
        
        # Modellnamen auflisten
        model_names = client.list_model_names()
        if model_names:
            print(f"\nVerfügbare Modellnamen ({len(model_names)}):")
            for name in model_names:
                print(f"  - {name}")
        
        # Optional: In Datei speichern
        save_choice = input("\nMöchten Sie die Daten in einer JSON-Datei speichern? (j/n): ")
        if save_choice.lower() in ['j', 'ja', 'y', 'yes']:
            client.save_models_to_file()
        
    except ValueError as e:
        print(f"Konfigurationsfehler: {e}")
        print("\nHinweise:")
        print("1. Erstellen Sie eine .env Datei mit ANTHROPIC_API_KEY=ihr_api_key")
        print("2. Oder setzen Sie die Umgebungsvariable ANTHROPIC_API_KEY")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    main()