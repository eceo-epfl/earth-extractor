import keyring
from keyring.errors import KeyringError
import typer
import logging
import sys
from rich.console import Console
from rich.table import Table
from pydantic import BaseSettings, root_validator
from typing import Dict, Optional
from earth_extractor import core
import jwt
import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class Credentials(BaseSettings):
    # User tokens
    SCIHUB_USERNAME: Optional[str] = None
    SCIHUB_PASSWORD: Optional[str] = None

    # NASA (For Alaska Satellite Facility and NASA Common Metadata Repository)
    NASA_TOKEN: Optional[str] = None

    # Read from .env file
    class Config:
        env_file = ".env"  # Populate from .env file before requesting keyring

    @root_validator
    def populate_credentials_from_keyring(
        cls, values: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:
        """Populate the credentials from the keyring"""
        for key in values.keys():
            if values[key] is None:
                # If key is not None, then the key is already set (from .env).
                # So now request the keyring for the value
                try:
                    values[key] = keyring.get_password(
                        core.config.constants.KEYRING_ID, key
                    )
                except KeyringError as e:
                    logger.warning(
                        f"Keyring error when getting key '{key}': {e}"
                    )
                    values[key] = None
        if "pytest" in sys.modules:  # Populate fake credentials for unit tests
            return {
                "SCIHUB_USERNAME": "test",
                "SCIHUB_PASSWORD": "test",
                "NASA_TOKEN": jwt.encode(  # JSON Web token
                    {
                        "some": "test",
                        "iat": datetime.datetime.utcnow(),
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(days=1),
                    },
                    "secret",
                    algorithm="HS256",
                ),
            }

        return values


def show_credential_list(show_secret=False) -> None:
    """Lists the credential keys in a table to the console

    Parameters
    ----------
    show_secret : bool
        If True, the secret values are shown in the table. If False, the
        secret values are hidden. Default is False.

    Returns
    -------
    None
    """

    console = Console()
    credentials = get_credentials()
    table = Table(title="Credentials")
    table.add_column("Credential key", justify="left")

    if show_secret:
        table.add_column("Value", justify="left")
    else:
        table.add_column("Value is set", justify="center")

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


def set_one_credential(
    key,
    hide_prompt=core.config.constants.HIDE_PASSWORD_PROMPT,
) -> None:
    """Set a single credential key in the keyring

    Parameters
    ----------
    key : str
        The key to set
    hide_prompt : bool
        If True, the prompt is hidden. If False, the prompt is shown.

    """

    if key not in get_credentials().__fields__:
        raise ValueError(f"Key '{key}' does not exist")

    secret = getattr(get_credentials(), key)

    new_secret = typer.prompt(
        key, default="" if secret is None else secret, hide_input=hide_prompt
    )

    if new_secret == "":
        # Don't store '' in the keyring in case there are any, just delete
        if secret == "":
            keyring.delete_password(core.config.constants.KEYRING_ID, key)
    else:
        keyring.set_password(core.config.constants.KEYRING_ID, key, new_secret)


def set_all_credentials() -> None:
    """Set all credential keys in the keyring"""

    for cred_key in get_credentials().__fields__:
        set_one_credential(cred_key)


def delete_credential(key) -> None:
    if key not in get_credentials().__fields__:
        raise ValueError(f"Key '{key}' does not exist")

    keyring.delete_password(core.config.constants.KEYRING_ID, key)


@lru_cache
def get_credentials() -> Credentials:
    return Credentials()
