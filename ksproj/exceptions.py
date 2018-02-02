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


class InternalException(Exception):
    STATUS_CODE = None
    MESSAGE = None


class Forbidden(InternalException):
    STATUS_CODE = 403
    MESSAGE = 'Unauthorized to perform the requested action.'


class NotFound(InternalException):
    STATUS_CODE = 404
    MESSAGE = 'Not Found.'


class DuplicateError(InternalException):
    STATUS_CODE = 400
    MESSAGE = 'Invitation already exists for project and user.'
