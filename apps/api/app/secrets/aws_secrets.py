from __future__ import annotations

from typing import Protocol


class SecretsManagerClient(Protocol):
    def get_secret_value(self, *, SecretId: str) -> dict[str, str]: ...

    def put_secret_value(self, *, SecretId: str, SecretString: str) -> dict[str, str]: ...

    def create_secret(self, *, Name: str, SecretString: str) -> dict[str, str]: ...


class AwsSecretsService:
    """AWS Secrets Manager integration using secret_ref ARNs."""

    def __init__(self, client: SecretsManagerClient | None = None) -> None:
        self._client = client

    def _get_client(self) -> SecretsManagerClient:
        if self._client is not None:
            return self._client
        import boto3

        return boto3.client("secretsmanager")

    def get_secret(self, secret_ref: str) -> str:
        response = self._get_client().get_secret_value(SecretId=secret_ref)
        return response["SecretString"]

    def store_secret(self, secret_ref: str, secret_value: str) -> str:
        client = self._get_client()
        store = getattr(client, "store", None)
        if store is not None:
            if secret_ref in store:
                client.put_secret_value(SecretId=secret_ref, SecretString=secret_value)
            else:
                client.create_secret(Name=secret_ref, SecretString=secret_value)
            return secret_ref

        try:
            client.put_secret_value(SecretId=secret_ref, SecretString=secret_value)
        except Exception:
            client.create_secret(Name=secret_ref, SecretString=secret_value)
        return secret_ref

    @staticmethod
    def build_secret_ref(*, application_id: str, channel: str, suffix: str = "credentials") -> str:
        return f"notifications-hub/{application_id}/{channel}/{suffix}"
