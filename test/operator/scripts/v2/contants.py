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

# backend_type
LOCAL = "local"
LOCAL_WITH_EXIST_PVC = "local-with-pvc"
S3 = "s3"

PVC_NAME = "integration-test-pvc"
MOUNT_PATH = "/bk/node_backup"

STORAGE_CLASS = "nfs-client"

BACKUP_REPO_SECRET = "backup-repo"
BACKUP_REPO_SECRET_KEY = "password"

MINIO_CREDENTIALS_SECRET = "minio-credentials"
MINIO_CREDENTIALS_SECRET_ACCESS_KEY = "username"
MINIO_CREDENTIALS_SECRET_ACCESS_VALUE = "minio"
MINIO_CREDENTIALS_SECRET_SECRET_KEY = "password"
MINIO_CREDENTIALS_SECRET_SECRET_VALUE = "minio123"

BUCKET_ENDPOINT = "minio.zhujq:9000"
BUCKET_NAME = "integration-bucket"

BLOCK_HEIGHT_FOR_FALLBACK = 5
BLOCK_HEIGHT_FOR_SNAPSHOT = 5

DEPLOY_METHOD_FOR_CLOUD_CONFIG = "cloud-config"

ACTION_STOP_AND_START = "StopAndStart"
ACTION_DIRECT = "Direct"
