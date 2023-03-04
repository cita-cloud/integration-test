#!/usr/bin/env python
#
# Copyright Rivtower Technologies LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FULL_BACKUP = "full-backup"
STATE_BACKUP = "state-backup"

LOCAL = "local"
LOCAL_WITH_EXIST_PVC = "local-with-pvc"
S3 = "s3"

BACKUP_REPO_SECRET = "backup-repo"
BACKUP_REPO_SECRET_KEY = "password"

MINIO_CREDENTIALS_SECRET = "minio-credentials"
MINIO_CREDENTIALS_SECRET_ACCESS_KEY = "username"
MINIO_CREDENTIALS_SECRET_SECRET_KEY = "password"

BUCKET_ENDPOINT = "http://192.168.10.122:30289"
BUCKET_FOR_RAFT = "raft-bucket"
BUCKET_FOR_OVERLORD = "overlord-bucket"