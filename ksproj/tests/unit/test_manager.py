# Copyright (c) 2018 Kristi Nikolla
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

import mock
import pytest


from ksproj import config
from ksproj import exceptions
from ksproj import manager
from ksproj import model
from ksproj.tests.unit import fakes


def get_project(self, project):
    for p in fakes.PROJECTS:
        if project in [p['name'], p['id']]:
            return p
    raise exceptions.NotFound


def get_roles(self, project=None, user=None):
    if project == fakes.PROJECT1['id']:
        if user == fakes.ADMIN_USER['id']:
            return [fakes.ADMIN_ROLE]
        if user == fakes.MEMBER_USER['id']:
            return [fakes.MEMBER_ROLE]
    return []


def client_init(*args, **kwargs):
    return


@mock.patch('ksproj.identity.ks_client.Client', client_init)
@mock.patch('ksproj.identity.Identity.get_project', get_project)
@mock.patch('ksproj.identity.Identity.get_roles', get_roles)
class TestManager(object):

    @staticmethod
    def _create_manager(user_token, reset_db=True):
        if reset_db:
            # Note(knikolla): Need to clean the database
            config.CONF.database = 'sqlite://'
            model.db.drop_all()
            model.db.create_all()

        def m(self, user_token):
            if user_token == fakes.ADMIN_TOKEN:
                return fakes.ADMIN_USER
            elif user_token == fakes.MEMBER_TOKEN:
                return fakes.MEMBER_USER
            else:
                raise exceptions.Forbidden

        with mock.patch('ksproj.identity.Identity.get_user_from_token', m):
            return manager.Manager(user_token)

    def test_create_manager(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        assert m.user == fakes.ADMIN_USER

        m = self._create_manager(fakes.MEMBER_TOKEN)
        assert m.user == fakes.MEMBER_USER

        with pytest.raises(exceptions.Forbidden):
            self._create_manager(uuid.uuid4().hex)

    def test_get_project(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        # Note(knikolla): First without validation
        assert m.get_project(
            fakes.PROJECT1['name'], validate=False
        ) == fakes.PROJECT1
        with pytest.raises(exceptions.NotFound):
            m.get_project(uuid.uuid4(), validate=False)

        # Note(knikolla): Then with validation
        with (mock.patch('ksproj.identity.Identity.get_roles',
                         return_value=[fakes.ADMIN_ROLE])):
            assert m.get_project(fakes.PROJECT1['name'])

            # Note(knikolla): Not existing project raises 403
            with pytest.raises(exceptions.Forbidden):
                m.get_project(uuid.uuid4().hex)

        with (mock.patch('ksproj.identity.Identity.get_roles',
                         return_value=[])):
            with pytest.raises(exceptions.Forbidden):
                m.get_project(uuid.uuid4().hex)

    def test_new_invite(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        m.invite(fakes.PROJECT1['name'], fakes.EMAIL)
        i = m.get_invitation(fakes.PROJECT1['name'], fakes.EMAIL)
        assert i['project'] == fakes.PROJECT1['id']
        assert i['email'] == fakes.EMAIL
        assert i['invited_by'] == m.user['id']

    def test_new_invitation_forbidden(self):
        m = self._create_manager(fakes.MEMBER_TOKEN)
        with pytest.raises(exceptions.Forbidden):
            m.invite(fakes.PROJECT1['name'], fakes.EMAIL)

        m = self._create_manager(fakes.ADMIN_TOKEN)
        with pytest.raises(exceptions.Forbidden):
            m.invite(fakes.PROJECT2['name'], fakes.EMAIL)

    def test_bulk_invite(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        emails = [uuid.uuid4().hex, uuid.uuid4().hex,
                  fakes.EMAIL, fakes.EMAIL]
        m.bulk_invite(fakes.PROJECT1['name'], emails)

        invitations = m.list_invitations(fakes.PROJECT1['name'])
        assert len(invitations) == 3  # Note(knikolla): There is one duplicate
        assert invitations[0]['email'] in emails
        assert invitations[1]['email'] in emails
        assert invitations[2]['email'] in emails

    def test_get_inexistent_invite(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        with pytest.raises(exceptions.NotFound):
            m.get_invitation(fakes.PROJECT1['name'], fakes.EMAIL)

    def test_duplicate_invite(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        m.invite(fakes.PROJECT1['name'], fakes.EMAIL)
        with pytest.raises(exceptions.DuplicateError):
            m.invite(fakes.PROJECT1['name'], fakes.EMAIL)

    def test_list_invitations(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        assert m.list_invitations(fakes.PROJECT1['name']) == []

        m.invite(fakes.PROJECT1['name'], uuid.uuid4().hex)
        m.invite(fakes.PROJECT1['name'], uuid.uuid4().hex)
        assert len(m.list_invitations(fakes.PROJECT1['name'])) == 2

        m = self._create_manager(fakes.MEMBER_TOKEN)
        with pytest.raises(exceptions.Forbidden):
            m.list_invitations(fakes.PROJECT1['name'])

    def test_delete_invitation(self):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        m.invite(fakes.PROJECT1['name'], fakes.EMAIL)
        m.get_invitation(fakes.PROJECT1['name'], fakes.EMAIL)

        other_m = self._create_manager(fakes.MEMBER_TOKEN, reset_db=False)
        with pytest.raises(exceptions.Forbidden):
            other_m.delete_invitation(fakes.PROJECT1['name'], fakes.EMAIL)

        m.delete_invitation(fakes.PROJECT1['name'], fakes.EMAIL)
        with pytest.raises(exceptions.NotFound):
            m.get_invitation(fakes.PROJECT1['name'], fakes.EMAIL)

    @mock.patch('ksproj.identity.Identity.get_role',
                return_value=fakes.MEMBER_ROLE)
    @mock.patch('ksproj.identity.Identity.add_user_to_project')
    def test_accept_invitation(self, mocked, *args):
        m = self._create_manager(fakes.ADMIN_TOKEN)
        token = m.invite(fakes.PROJECT1['name'], fakes.EMAIL)['token']

        user_m = self._create_manager(fakes.MEMBER_TOKEN, reset_db=False)
        user_m.accept(token)

        i = m.get_invitation(fakes.PROJECT1['name'], fakes.EMAIL)
        assert i['accepted_by'] == fakes.MEMBER_USER['id']
        assert i['status'] == 'ACCEPTED'

        mocked.assert_called_once_with(project=fakes.PROJECT1['id'],
                                       user=fakes.MEMBER_USER['id'],
                                       role=fakes.MEMBER_ROLE['id'])

        # Note(knikolla): Test reaccepting will not work
        with pytest.raises(exceptions.NotFound):
            user_m.accept(token)

    def test_accept_not_existing_invitation(self):
        m = self._create_manager(fakes.MEMBER_TOKEN)
        with pytest.raises(exceptions.NotFound):
            m.accept(uuid.uuid4().hex)
