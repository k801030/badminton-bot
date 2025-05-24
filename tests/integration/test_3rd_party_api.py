import pytest

from app import court_client, sm


@pytest.mark.parametrize("account_id", [1, 2])
def test_login(account_id):
    try:
        account = sm.get_account_by_id(account_id)
        court_client.login(account.username, account.password)
    except Exception as e:
        assert False, f"Unexpected exception raised: {e}"
