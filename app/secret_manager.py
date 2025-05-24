import json

import boto3

from models.account import Account
from models.line_secret import LineSecret


class SecretManager:
    def __init__(self, region, is_dev=False):
        self.client = boto3.session.Session().client(
            service_name="secretsmanager", region_name=region
        )
        self.is_dev = is_dev

    def _get_secret(self, secret_name):
        response = self.client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]

    def get_line_secret(self) -> LineSecret:
        secret_name = "line_secret/dev" if self.is_dev else "line_secret"
        secret = self._get_secret(secret_name)
        json_str = json.loads(secret)
        return LineSecret(json_str["access_token"], json_str["group_id"])

    def get_account_by_id(self, account_id) -> Account:

        secret = self._get_secret(f"account/{account_id}")
        json_str = json.loads(secret)
        return Account(json_str["username"], json_str["password"])
