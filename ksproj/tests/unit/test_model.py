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

import freezegun
import pytest

import datetime
import uuid

from ksproj import config
from ksproj import exceptions
from ksproj import model


class TestInvitation(object):

    @pytest.fixture()
    def reset_db(self):
        # Note(knikolla): Need to clean the database
        config.CONF.database = 'sqlite://'
        model.db.drop_all()
        model.db.create_all()

    @pytest.fixture()
    def invitation(self, reset_db):
        i = model.Invitation(project=uuid.uuid4().hex,
                             email=uuid.uuid4().hex,
                             role=uuid.uuid4().hex,
                             token=uuid.uuid4().hex,
                             invited_by=uuid.uuid4().hex)
        model.add(i)
        return i

    def test_create(self, reset_db):
        project = uuid.uuid4().hex
        email = uuid.uuid4().hex
        role = uuid.uuid4().hex
        token = uuid.uuid4().hex
        invited_by = uuid.uuid4().hex

        with freezegun.freeze_time("2018-01-01"):
            invitation = model.Invitation(project,
                                          email,
                                          role,
                                          token,
                                          invited_by)

            assert len(model.Invitation.query.all()) == 0

            model.Invitation.add(invitation)

            query = model.Invitation.query.all()
            assert len(query) == 1

            assert (
                query[0].project == project and
                query[0].email == email and
                query[0].role == role and
                query[0].token == token and
                query[0].invited_by == invited_by and
                query[0].invited_on == datetime.datetime.now() and
                query[0].accepted_on is None and
                query[0].accepted_by is None
            )

            invitation2 = model.Invitation(project,
                                           email,
                                           role,
                                           token,
                                           invited_by)

            with pytest.raises(exceptions.DuplicateError):
                model.Invitation.add(invitation2)

    def test_set_accepted(self, invitation):
        assert len(model.Invitation.query.all()) == 1

        user = uuid.uuid4().hex
        with freezegun.freeze_time("2018-01-01"):
            invitation.set_accepted(user)
            assert (invitation.accepted_by == user and
                    invitation.accepted_on == datetime.datetime.now())

    def test_find_by_token(self, invitation):
        i = model.Invitation.find_by_token(invitation.token)
        assert i is not None
        assert i.token == invitation.token

        i = model.Invitation.find_by_token(uuid.uuid4().hex)
        assert i is None

    def test_list_by_project(self, invitation):
        i = model.Invitation.find_by_project_and_email(invitation.project,
                                                       invitation.email)
        assert i is not None
        assert i.token == invitation.token

        i = model.Invitation.find_by_project_and_email(uuid.uuid4().hex,
                                                       uuid.uuid4().hex)
        assert i is None
