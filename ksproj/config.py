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

from os import path

from oslo_config import cfg

CONF = cfg.CONF

default_opts = [
    cfg.StrOpt('database',
               default='sqlite://',
               help='Database connection string'),

    cfg.StrOpt('admin_role_name',
               default='project_admin',
               help='Name for admin role. This role will be required for'
                    ' users who want to invite other users to their'
                    ' project.'),

    cfg.StrOpt('member_role_name',
               default='_member_',
               help='Name for member role. This role will be assigned to'
                    ' users when they accept a project invitation.'),

]
CONF.register_opts(default_opts)

auth_group = cfg.OptGroup(name='auth',
                          title='Auth Config Group')
auth_opts = [
    cfg.StrOpt('auth_url',
               default='http://localhost/identity/v3',
               help='Identity endpoint. (v3)'),

    cfg.StrOpt('username',
               default='admin',
               help='Username for admin user.'),

    cfg.StrOpt('user_domain_name',
               default='Default',
               help='Domain name for admin user.'),

    cfg.StrOpt('user_domain_id',
               default=None,
               help='Domain ID for admin user.'),

    cfg.StrOpt('user_id',
               default=None,
               help='User ID for admin user.'),

    cfg.StrOpt('password',
               default=None,
               help='Password for admin user.'),

    cfg.StrOpt('project_name',
               default='admin',
               help='Admin project name.'),

    cfg.StrOpt('project_domain_name',
               default='Default',
               help='Domain name for admin project.'),

    cfg.StrOpt('project_domain_id',
               default=None,
               help='Domain ID for admin project.'),

    cfg.StrOpt('project_id',
               default=None,
               help='ID of the admin project')
]
CONF.register_group(auth_group)
CONF.register_opts(auth_opts, auth_group)

email_group = cfg.OptGroup(name='email',
                          title='Email Config Group')
email_opts = [
    cfg.StrOpt('smtp',
               default='http://localhost',
               help='SMTP Server to send emails'),

    cfg.StrOpt('author',
               default='',
               help='Author to send emails'),

    cfg.StrOpt('password',
               default='',
               help='Password for author user'),
]
CONF.register_group(email_group)
CONF.register_opts(email_opts, email_group)


def load_config():
    conf_files = [f for f in ['ksproj.conf',
                              'etc/ksproj.conf',
                              '/etc/ksproj.conf'] if path.isfile(f)]
    if conf_files is not []:
        CONF(default_config_files=conf_files)


def list_opts():
    return [(None, default_opts),
            (auth_group, auth_opts),
            (email_group, email_opts)]
