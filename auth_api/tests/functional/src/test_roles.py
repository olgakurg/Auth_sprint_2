import uuid

import pytest
from pydantic import BaseModel


class PermissionsCreate(BaseModel):
    name: str


N_RECORDS = 5

pytestmark = pytest.mark.asyncio


class TestRole:
    permissions_id: str = ''
    roles_id: str = ''

    @pytest.mark.parametrize(
        'params, expected_answer',
        [
            (
                    {'name': 'new'},
                    {'status': 201, 'type': str}
            ),
            (
                    {},
                    {'status': 422, 'type': dict}
            )
        ]
    )
    async def test_create_permissions(self, params, expected_answer, api_request):

        response = await api_request(table='permissions', params=params, method='post')

        status = response['status']
        body = response['body']
        if type(body) is str:
            self.__class__.permissions_id = body

        assert status == expected_answer['status']
        assert type(body) == expected_answer['type']

    @pytest.mark.parametrize(
        'params, expected_answer',
        [
            (
                    'ok',
                    {'status': 200, 'key': 'name'}
            ),
            (
                    'noUUID',
                    {'status': 422, 'key': 'detail'}
            ),
            (
                    'incorrect',
                    {'status': 404, 'key': 'detail'}
            ),
            (
                    'absent',
                    {'status': 405, 'key': 'detail'}
            )
        ]
    )
    async def test_get_permissions(self, params, expected_answer, api_request):
        if params == 'ok':
            permissions_id = self.__class__.permissions_id
        elif params == 'noUUID':
            permissions_id = '111'
        elif params == 'incorrect':
            permissions_id = uuid.uuid4()
        else:
            permissions_id = ''

        response = await api_request(table='permissions', id=permissions_id, method='get')

        status = response['status']
        body = response['body']

        assert status == expected_answer['status']
        assert expected_answer['key'] in body

    @pytest.mark.parametrize(
        'name, params, expected_answer',
        [
            (
                    'ok',
                    {'name': 'Admin', 'description': 'all permissions'},
                    {'status': 201, 'type': str}
            ),
            (
                    'absent',
                    {},
                    {'status': 422, 'type': dict}
            )
        ]
    )
    async def test_create_role(self, name, params, expected_answer, api_request):
        if name == 'ok':
            permissions_id = self.__class__.permissions_id
            params['permissions'] = [f"{permissions_id}"]

        response = await api_request(table='roles', params=params, method='post')

        status = response['status']
        body = response['body']
        if type(body) is str:
            self.__class__.roles_id = body

        assert status == expected_answer['status']
        assert type(body) == expected_answer['type']
