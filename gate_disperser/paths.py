from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ADDRESSES_TXT_FILEPATH = BASE_DIR / 'addresses.txt'
SETTINGS_DIR = BASE_DIR / 'settings'
API_SETTINGS_JSON_FILEPATH = SETTINGS_DIR / 'api.json'
SCRIPT_SETTINGS_JSON_FILEPATH = SETTINGS_DIR / 'script.json'
AUTOCOMPLETE_DIR = BASE_DIR / 'autocomplete'
CURRENCIES_JSON_FILENAME = AUTOCOMPLETE_DIR / 'currencies.json'
