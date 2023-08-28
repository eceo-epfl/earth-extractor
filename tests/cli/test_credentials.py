from typer.testing import CliRunner
from earth_extractor.app import app
from earth_extractor.core.credentials import Credentials

runner = CliRunner()


def test_credential_output():
    result = runner.invoke(app, ["credentials", "--show-secrets"])

    assert result.exit_code == 0
    assert "Credential key" in result.stdout
    assert "Value" in result.stdout

    # Get fields from credentials
    credentials = Credentials()
    cred_fields = credentials.__fields__

    for field in cred_fields:
        assert field in result.stdout, f"Field {field} not found in output"


def test_credential_output_show_secrets():
    result = runner.invoke(app, ["credentials", "--show-secrets"])

    # Get fields from credentials
    credentials = Credentials()
    cred_fields = credentials.__fields__

    for field in cred_fields:
        assert field in result.stdout, f"Field {field} not found in output"

    # Check the values in credentials are in the output
    for field in cred_fields:
        if field == "NASA_TOKEN":
            # Only use a subset of the token as it is a long string
            assert (
                getattr(credentials, field)[:10] in result.stdout
            ), f"Value of field {field} not found in output"
        else:
            assert (
                getattr(credentials, field) in result.stdout
            ), f"Value of field {field} not found in output"


def test_credential_output_set():
    result = runner.invoke(app, ["credentials", "--set"])

    # Get fields from credentials
    credentials = Credentials()
    cred_fields = credentials.__fields__
    print(result.stdout)
    for field in cred_fields:
        assert field in result.stdout, f"Field {field} not found in output"

    # Expected output is the prompt of:
    # {key} [{existing value}]: {user input}
    # So let's split the keys and check that the value is the one that is
    # set. We can expect that pytest hit enter on all the values so they should
    # all be there
    lines = result.stdout.split("\n")
    for line in lines:
        if line != "" and ":" in line:
            key_and_value = line.split(": ")[0]  # Remove colon, trailing space
            key, value = key_and_value.split(" [")  # Split by the space
            value = value[:-1]  # Remove trailing bracket
            if key != "NASA_TOKEN":  # As test autogenerates, don't test
                assert (
                    getattr(credentials, key) == value
                ), f"Value of field {key} not set correctly"
