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

FROM alpine:3.7

EXPOSE 9999
WORKDIR /usr/src/app

RUN apk add --no-cache \
        python3 \
        python3-dev \
        uwsgi \
        uwsgi-python3 \
        musl-dev \
        linux-headers \
        gcc

COPY . .

RUN pip3 install -U pip \
    pip3 install --no-cache-dir -r requirements.txt

CMD [ "uwsgi", "--socket", "0.0.0.0:9999", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi", "ksproj.api:application" ]
