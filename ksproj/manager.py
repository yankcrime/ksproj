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

from ksproj import config
from ksproj import exceptions
from ksproj import identity
from ksproj import mail
from ksproj import model

CONF = config.CONF


class Manager(object):
    def __init__(self, user_token):
        self.user = identity.client().get_user_from_token(user_token)

    def _new_invitation(self, project, email):
        return model.Invitation(
            project=project,
            email=email,
            role='Member',
            token=uuid.uuid4().hex,
            invited_by=self.user['id']
        )

    def get_project(self, project, validate=True):
        try:
            project = identity.client().get_project(project)
        except exceptions.NotFound:
            # Note(knikolla): We must not expose whether a project exists
            # or not, if requiring project admin permissions.
            if validate:
                raise exceptions.Forbidden
            raise

        if validate:
            roles = identity.client().get_roles(project=project['id'],
                                                user=self.user['id'])
            if CONF.admin_role_name not in [r['name'] for r in roles]:
                raise exceptions.Forbidden
        return project

    def invite(self, project, email, send_email=False):
        project = self.get_project(project, validate=True)
        i = self._new_invitation(project['id'], email)
        model.Invitation.add(i)
        if send_email:
            mail.send(email, i.token, project['name'])
        return i.to_dict()

    def bulk_invite(self, project, emails, send_email=False):
        project = self.get_project(project, validate=True)
        for email in emails:
            i = self._new_invitation(project['id'], email)
            try:
                model.Invitation.add(i)
            except exceptions.DuplicateError:
                i = model.Invitation.find_by_project_and_email(project['id'],
                                                               email)
            if send_email:
                mail.send(email, i.token, project['name'])

    def get_invitation(self, project, email):
        project = self.get_project(project, validate=True)
        i = model.Invitation.find_by_project_and_email(project['id'], email)
        if not i:
            raise exceptions.NotFound
        return i.to_dict()

    def list_invitations(self, project):
        project = self.get_project(project, validate=True)
        invitations = model.Invitation.list_by_project(project['id'])
        return [i.to_dict() for i in invitations]

    def delete_invitation(self, project, email):
        project = self.get_project(project, validate=True)
        i = model.Invitation.find_by_project_and_email(project['id'], email)
        if not i:
            raise exceptions.NotFound
        model.delete(i)

    def accept(self, invitation_token):
        i = model.Invitation.find_by_token(invitation_token)
        if not i:
            raise exceptions.NotFound
        if i.accepted_by:
            raise exceptions.NotFound

        member_role = identity.client().get_role(CONF.member_role_name)
        identity.client().add_user_to_project(project=i.project,
                                              user=self.user['id'],
                                              role=member_role['id'])
        i.set_accepted(self.user['id'])
