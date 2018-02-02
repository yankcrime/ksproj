# Copyright (c) 2017 Kristi Nikolla
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

from keystoneauth1 import exceptions as ks_esceptions
from keystoneauth1 import identity as ks_identity
from keystoneauth1 import session as ks_session
from keystoneclient import client as ks_client

from ksproj import config
from ksproj import exceptions
from ksproj import utils

CONF = config.CONF


_IDENTITY = None


def client():
    global _IDENTITY
    if not _IDENTITY:
        _IDENTITY = Identity()
    return _IDENTITY


class Forbidden(Exception):
    pass


class Identity(object):
    def __init__(self):
        self.session = self._get_session()
        self.identity = ks_client.Client(session=self.session)

    @classmethod
    def _get_session(cls):
        auth = ks_identity.v3.Password(
            auth_url=CONF.auth.auth_url,
            username=CONF.auth.username,
            user_id=CONF.auth.user_id,
            password=CONF.auth.password,
            user_domain_name=CONF.auth.user_domain_name,
            user_domain_id=CONF.auth.user_domain_id,
            project_name=CONF.auth.project_name,
            project_id=CONF.auth.project_id,
            project_domain_name=CONF.auth.project_domain_name,
            project_domain_id=CONF.auth.project_domain_id,
        )
        return ks_session.Session(auth)

    def get_user_from_token(self, token):
        try:
            user_info = self.identity.tokens.validate(token)['user']
        except ks_esceptions.http.NotFound:
            raise exceptions.Forbidden
        return {'name': user_info['name'], 'id': user_info['id']}

    def get_role(self, role):
        try:
            if utils.is_uuid(role):
                role = self.identity.users.get(role)
            else:
                role = self.identity.roles.find(name=role)
        except Exception:  # FIXME
            raise exceptions.NotFound
        return {'name': role.name, 'id': role.id}

    def get_user(self, user):
        try:
            if utils.is_uuid(user):
                user = self.identity.users.get(user)
            else:
                user = self.identity.users.find(name=user)
        except Exception:  # FIXME
            raise exceptions.NotFound
        return {'name': user.name, 'id': user.id}

    def get_project(self, project):
        try:
            if utils.is_uuid(project):
                p = self.identity.projects.get(project)
            else:
                p = self.identity.projects.find(name=project)
        except Exception:  # FIXME
            raise exceptions.NotFound
        return {'name': p.name, 'id': p.id}

    def get_roles(self, project=None, user=None):
        roles = self.identity.role_assignments.list(project=project,
                                                    user=user,
                                                    include_names=True)
        return [{'name': r.role['name'], 'id': r.role['id']} for r in roles]

    def add_user_to_project(self, project, user, role):
        self.identity.roles.grant(project=project,
                                  user=user,
                                  role=role)
