import json
from typing import Dict, List, Any

import pandas as pd
import requests


class DataManager:
    """Verwaltet das Laden und Parsen von JSON-Daten aus einer API oder aus einer Datei."""

    def __init__(self):
        self.raw_data: Dict[str, Any] = {}
        self.data: List[Dict[str, Any]] = []

    def load_from_api(self, access_key: str, symbol: str, **params) -> bool:
        """
        Lädt Daten von der Marketstack-API.

        :param access_key: API-Zugriffsschlüssel.
        :param symbol: Börsensymbol (z. B. "AAPL").
        :param params: Zusätzliche optionale Parameter (z. B. sort, date_from, date_to, limit, offset).
        :return: True, wenn das Laden erfolgreich war.
        """
        base_url = "http://api.marketstack.com/v1/eod"
        query_params = {"access_key": access_key, "symbols": symbol}
        query_params.update(params)
        try:
            response = requests.get(base_url, params=query_params)
            response.raise_for_status()
            self.raw_data = response.json()
            self.data = self.raw_data.get("data", [])
        except Exception as e:
            raise ValueError(f"Fehler beim Laden der API-Daten: {e}")
        return True

    def load_from_file(self, file_path: str) -> bool:
        """
        Lädt Daten aus einer JSON-Datei oder CSV-Datei.

        :param file_path: Pfad zur JSON-Datei oder CSV-Datei.
        :return: True, wenn das Laden erfolgreich war.
        """
        if file_path.endswith(".csv"):
            self.data = pd.read_csv(file_path).to_dict(orient='records')
        elif file_path.endswith(".json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Ungültiger Dateityp. Es werden nur JSON- und CSV-Dateien unterstützt.")
        return True

    def get_available_keys(self) -> List[str]:
        """
        Gibt eine Liste der Keys aus dem ersten Datensatz zurück.

        :return: Liste von Strings (Keys)
        """
        return list(self.data[0].keys()) if self.data and isinstance(self.data, list) else []

    def get_column_data(self, key: str) -> List[Any]:
        """
        Extrahiert die Daten einer bestimmten Spalte (Key) aus den Datensätzen.

        :param key: Der Schlüssel, dessen Daten extrahiert werden sollen.
        :return: Liste der Werte für den angegebenen Key.
        """
        return [item.get(key) for item in self.data]
