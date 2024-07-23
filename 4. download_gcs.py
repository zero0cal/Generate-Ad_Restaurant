from google.cloud import storage
import os


storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names

def download_blob(bucket_name, source_blob_name, destination_file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded storage object {source_blob_name} from bucket {bucket_name} to local file {destination_file_name}.")

#gcs 위치에 접근해서 folder 리스트 가져오기
def list_folder_in_gcs_path(bucket_name, gcs_path): 
    bucket = storage_client.bucket(bucket_name, gcs_path)
    blobs = bucket.list_blobs(prefix=gcs_path)
    return blobs

def download_files_from_gcs(bucket_name, gcs_path, local_dir):
    blobs = list_folder_in_gcs_path(bucket_name, gcs_path)
    os.makedirs(local_dir, exist_ok=True)


/////////여기서부터 리스트 받아와서 시작
    for blob in blobs:
        file_path = os.path.join()


#restaurant 리스트 받아오기(mp3 생성한 순)
restaurant_names = get_restaurant_names_from_txt("/Users/zero/STUDY/UGRP/Google Cloud/elevenLabs_Restaurant.txt")

def main():
    #GCS 기본 경로 지정
    base_path = 'Restaurant Photo DB/경상북도/대구/달성군'

    restaurant_names = get_restaurant_names_from_txt("/Users/zero/STUDY/UGRP/Google Cloud/elevenLabs_Restaurant.txt")
    
    for i, restaurant_name in enumerate(restaurant_names):

        if i == 2:
            break


        narration_files = [f"{restaurant_name}_promo_reel.mp3", f"{restaurant_name}_promo_reel.srt"]

        #Source가 저장될 로컬 경로 
        local_directory = f"/Users/zero/STUDY/UGRP/gummy_Video/Restaurant/{restaurant_name}/Source"
        
        #로컬 디렉토리가 존재하지 않으면 생성
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        #파일 다운로드
        for narration_file in narration_files:
            gcs_path = f'{base_path}/{restaurant_name}/narration/{narration_file}'
            local_path = os.path.join(local_directory, os.path.basename(narration_file))
            download_blob(bucket_name, gcs_path, local_path)


        video_files = [f"{restaurant_name}_음식_1.mp4", f"{restaurant_name}_음식_2.mp4", f"{restaurant_name}_음식_3.mp4", f"{restaurant_name}_음식_.mp4"]
        




if __name__ == '__main__':
    main()

