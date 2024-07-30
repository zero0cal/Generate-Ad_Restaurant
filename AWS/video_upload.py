import os
import boto3
from botocore.exceptions import NoCredentialsError, EndpointConnectionError, ClientError

# S3 버킷 이름 설정
bucket_name = 'original-video-db'
# 로컬 디렉토리 설정
base_directory = '/Users/zero/STUDY/UGRP/gummy_Video/final_Video'

def folder_exists(bucket_name, folder_name):
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    for obj in response.get('Contents', []):
        if obj['Key'].startswith(folder_name):
            return True
    return False

def create_folder(bucket_name, folder_name):
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    try:
        s3.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
        print(f'Folder "{folder_name}" created successfully in bucket "{bucket_name}".')
    except FileNotFoundError:
        print(f"The file was not found: {folder_name}")
    except NoCredentialsError:
        print("Credentials not available")
    except EndpointConnectionError as e:
        print(f"Could not connect to the endpoint URL: {e}")ㅇㄹ
    except ClientError as e:
        print(f"Client error: {e}")

def upload_file_to_s3(local_file, bucket_name, s3_file):
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    try:
        s3.upload_file(local_file, bucket_name, s3_file)
        print(f'File "{local_file}" uploaded successfully to "{s3_file}" in bucket "{bucket_name}".')
    except FileNotFoundError:
        print(f"The file was not found: {local_file}")
    except NoCredentialsError:
        print("Credentials not available")
    except EndpointConnectionError as e:
        print(f"Could not connect to the endpoint URL: {e}")
    except ClientError as e:
        print(f"Client error: {e}")

def process_directory(base_directory, bucket_name):
    for restaurant_name in os.listdir(base_directory):
        restaurant_path = os.path.join(base_directory, restaurant_name)
        if os.path.isdir(restaurant_path):  # 해당 경로가 디렉토리인지 확인
            folder_name = f'대구광역시/달성군/{restaurant_name}'
            if not folder_exists(bucket_name, folder_name):
                create_folder(bucket_name, folder_name)
            for root, dirs, files in os.walk(restaurant_path):
                for file in files:
                    if file.endswith('.mp4'):
                        local_file = os.path.join(root, file)
                        s3_file = f'{folder_name}/{file}'
                        upload_file_to_s3(local_file, bucket_name, s3_file)

# 로컬 디렉토리 내의 모든 가게명 폴더를 처리
process_directory(base_directory, bucket_name)
