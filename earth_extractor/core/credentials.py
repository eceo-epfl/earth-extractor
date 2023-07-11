import keyring
import typer
import logging
from rich.console import Console
from rich.table import Table
from pydantic import BaseSettings, root_validator
from typing import Dict
from earth_extractor import core

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class Credentials(BaseSettings):
    # User tokens
    SCIHUB_USERNAME: str | None = None
    SCIHUB_PASSWORD: str | None = None

    # NASA API (For Alaska Satellite Facility)
    NASA_USERNAME: str | None = None
    NASA_PASSWORD: str | None = None

    # Sinergise Sentinel Hub
    SINERGISE_CLIENT_ID: str | None = None
    SINERGISE_CLIENT_SECRET: str | None = None

    @root_validator
    def populate_credentials_from_keyring(
        cls,
        values: Dict[str, str | None]
    ) -> Dict[str, str | None]:
        ''' Populate the credentials from the keyring '''
        for key in values.keys():
            values[key] = keyring.get_password(
                core.config.constants.KEYRING_ID, key
            )

        return values


def show_credential_list(
    show_secret=False
) -> None:
    ''' Lists the credential keys in a table to the console

    Parameters
    ----------
    show_secret : bool
        If True, the secret values are shown in the table. If False, the
        secret values are hidden. Default is False.

    Returns
    -------
    None
    '''

    console = Console()
    credentials = get_credentials()
    table = Table(title="Credentials")
    table.add_column("Credential key", justify='left')

    if show_secret:
        table.add_column("Value", justify='left')
    else:
        table.add_column("Value is set", justify='center')

    for cred_key in credentials.__fields__:
        if show_secret:
            value = getattr(credentials, cred_key)
        else:
            if getattr(credentials, cred_key) is not None:
                value = "[green]Yes[/green]"
            else:
                value = "[red]No[/red]"
        table.add_row(cred_key, value)

    console.print(table)


def set_one_credential(key):
    ''' Set a single credential key in the keyring '''

    if key not in get_credentials().__fields__:
        raise ValueError(f"Key '{key}' does not exist")

    secret = keyring.get_password(core.config.constants.KEYRING_ID, key)
    new_secret = typer.prompt(
        key,
        default='' if secret is None else secret,
    )

    if new_secret == '':
        # Don't store '' in the keyring in case there are any, just delete
        if secret == '':
            keyring.delete_password(core.config.constants.KEYRING_ID, key)
    else:
        keyring.set_password(core.config.constants.KEYRING_ID, key, new_secret)


def set_all_credentials():
    ''' Set all credential keys in the keyring '''

    for cred_key in get_credentials().__fields__:
        set_one_credential(cred_key)


def delete_credential(key):
    if key not in get_credentials().__fields__:
        raise ValueError(f"Key '{key}' does not exist")

    keyring.delete_password(core.config.constants.KEYRING_ID, key)


def get_credentials():
    return Credentials()
