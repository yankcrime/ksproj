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

CONF = config.CONF

MEMBER_ROLE = {'name': CONF.member_role_name, 'id': uuid.uuid4().hex}
ADMIN_ROLE = {'name': CONF.admin_role_name, 'id': uuid.uuid4().hex}

PROJECT1 = {'name': 'fake_project_1', 'id': uuid.uuid4().hex}
PROJECT2 = {'name': 'fake_project_2', 'id': uuid.uuid4().hex}
PROJECT3 = {'name': 'fake_project_3', 'id': uuid.uuid4().hex}

PROJECTS = [PROJECT1, PROJECT2, PROJECT3]

MEMBER_USER = {'name': 'fake_user_1', 'id': uuid.uuid4().hex}
ADMIN_USER = {'name': 'fake_user_2', 'id': uuid.uuid4().hex}
INVALID_USER = {'name': 'fake_user_3', 'id': uuid.uuid4().hex}

ADMIN_TOKEN = uuid.uuid4().hex
MEMBER_TOKEN = uuid.uuid4().hex
INVALID_TOKEN = uuid.uuid4().hex

EMAIL = 'test@example.com'
