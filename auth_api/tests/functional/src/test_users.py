import pytest
from faker import Faker

from tests.functional.testdata.data import test_token

fake = Faker()


@pytest.mark.asyncio
async def test_signin(api_request):
    params = {'login': fake.word(), 'password': "password", 'name': fake.name()}
    new_user = await api_request(table='users', id='signup', params=params, method="post")
    response = await api_request(table='users', id='signin', params=params, method="post")
    status = response['status']
    assert status == 200


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_signup(api_request):
    params = {'login': fake.word(), 'password': "password", 'name': fake.name()}
    response = await api_request(table='users', id='signup', params=params, method="post")
    status = response['status']
    assert status == 201


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_refresh(api_request):
    """По тестовой паре токенов проверяем успешную выдачу новых"""
    headers = {"Authorization": f"Bearer {test_token['refresh']}"}
    response = await api_request(table='users', id='refresh', headers=headers, params=test_token, method="post")
    status = response['status']
    assert status == 200
