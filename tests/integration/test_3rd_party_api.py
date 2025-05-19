import pytest

from app import client
from helper import get_account_by_id


@pytest.mark.parametrize("account_id", [1, 2])
def test_login(account_id):
    try:
        account = get_account_by_id(account_id)
        client.login(account.username, account.password)
    except Exception as e:
        assert False, f"Unexpected exception raised: {e}"
