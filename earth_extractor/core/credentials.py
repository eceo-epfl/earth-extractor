import keyring
from rich.console import Console
from rich.table import Table
from pydantic import BaseSettings, root_validator
from typing import Dict
from earth_extractor.config import constants


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

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @root_validator(pre=True)
    def populate_credentials_from_keyring(
        cls,
        values: Dict[str, str]
    ) -> None:
        for key in values.keys():
            values[key] = keyring.get_credential(constants.KEYRING_ID, key)

        return values


credentials = Credentials()


def show_credential_list():
    ''' Lists the credential keys in a table to the console '''

    console = Console()
    table = Table(title="Credentials")
    table.add_column("Credential key", justify='left')
    table.add_column("Value set", justify='center')

    for cred_key in credentials.__fields__:
        if getattr(credentials, cred_key) is not None:
            indicator = "[green]Yes[/green]"
        else:
            indicator = "[red]No[/red]"
        table.add_row(cred_key, indicator)

    console.print(table)

def set_all_credentials():
    for cred_key in credentials.__fields__:
        print(keyring.get_credential("earth-extractor", cred_key))