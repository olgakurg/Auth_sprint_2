import pytest


@pytest.mark.asyncio
async def test_root(api_request):
    response = await api_request(table='users')
    status = response['status']
    assert status == 200
