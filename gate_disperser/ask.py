import json

from questionary import Validator, ValidationError
from questionary import text, autocomplete, select
import gate_api

from .settings import APISettings, ScriptSettings
from .paths import AUTOCOMPLETE_DIR, CURRENCIES_JSON_FILENAME, API_SETTINGS_JSON_FILEPATH, SCRIPT_SETTINGS_JSON_FILEPATH
from .config import HOST


AUTOCOMPLETE_DIR.mkdir(exist_ok=True)

gate_api_config = gate_api.Configuration(host=HOST)
gate_api_client = gate_api.ApiClient(gate_api_config)
spot_api = gate_api.SpotApi(gate_api_client)
wallet_api = gate_api.WalletApi(gate_api_client)


class FloatValidator(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a valid float number",
                cursor_position=len(document.text),
            )


class FloatOrBlankLineValidator(Validator):
    def validate(self, document):
        try:
            if document.text:
                float(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a valid float number",
                cursor_position=len(document.text),
            )


def ask_api_settings() -> APISettings:
    if not API_SETTINGS_JSON_FILEPATH.exists():
        key = text('Enter API key:').ask()
        secret = text('Enter API secret:').ask()
    else:
        with open(API_SETTINGS_JSON_FILEPATH, 'r') as settings_file:
            api_settings_dict = json.load(settings_file)
            key = api_settings_dict['key']
            secret = api_settings_dict['secret']
        new_key = text(f'Current API key: {key}\n'
                       f'Enter new API key or enter the blank line to skip:').ask()
        new_secret = text(f'Current API secret: {secret}\n'
                          f'Enter new API secret or enter the blank line to skip:').ask()
        key = new_key or key
        secret = new_secret or secret
    api_settings = APISettings(key=key, secret=secret)
    api_settings.save()
    return api_settings


def ask_script_settings() -> ScriptSettings:
    if CURRENCIES_JSON_FILENAME.exists():
        with open(CURRENCIES_JSON_FILENAME, 'r') as file:
            currencies = json.load(file)
    else:
        currencies = [currency.currency for currency in spot_api.list_currencies()
                      if not currency.withdraw_disabled]
        with open(CURRENCIES_JSON_FILENAME, 'w') as file:
            json.dump(currencies, file)

    class CurrencyValidator(Validator):
        def validate(self, document):
            if document.text not in currencies:
                raise ValidationError(
                    message="Unknown currency",
                    cursor_position=len(document.text),
                )

    script_settings_dict = None
    if SCRIPT_SETTINGS_JSON_FILEPATH.exists():
        with open(SCRIPT_SETTINGS_JSON_FILEPATH, 'r') as settings_file:
            script_settings_dict = json.load(settings_file)

    if script_settings_dict:
        currency_message = f'Current currency: {script_settings_dict["currency"]}\n' \
                           f'Enter another currency or enter the blank line to skip:'
    else:
        currency_message = 'Enter currency:'
    currency = autocomplete(currency_message, choices=currencies, validate=CurrencyValidator).ask()
    if script_settings_dict and not currency:
        currency = script_settings_dict["currency"]

    chains = [chain.chain for chain in wallet_api.list_currency_chains(currency)]

    chain = select('Select Chain', choices=chains).ask()

    if script_settings_dict:
        min_amount = text(f'Current min amount: {script_settings_dict["min_amount"]}\n'
                          f'Enter another min amount or enter the blank line to skip:',
                          validate=FloatOrBlankLineValidator).ask()

        max_amount = text(f'Current max amount: {script_settings_dict["max_amount"]}\n'
                          f'Enter another max amount or enter the blank line to skip:',
                          validate=FloatOrBlankLineValidator).ask()
        if not min_amount:
            min_amount = float(script_settings_dict["min_amount"])
        if not max_amount:
            max_amount = float(script_settings_dict["max_amount"])
    else:
        min_amount = float(text('Min amount:', validate=FloatValidator).ask())
        max_amount = float(text('Max amount:', validate=FloatValidator).ask())

    script_settings = ScriptSettings(currency=currency, chain=chain, min_amount=min_amount, max_amount=max_amount)
    script_settings.save()
    return script_settings
