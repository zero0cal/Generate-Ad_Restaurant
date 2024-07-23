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

def download_video_file(bucket_name, folder_path, local_download_path, restaurant_name, num_video):
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)

    #없으면 비디오 폴더 만들어주자.
    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)

    for index, blob in enumerate(blobs):
        custom_file_name=f"{restaurant_name}_{num_video}.mp4"
        local_file_path = os.path.join(local_download_path, custom_file_name)
        
        blob.download_to_filename(local_file_path)
        num_video+=1
        print(f'Downloaded {blob.name} to {local_file_path}')
    return num_video


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
            narration_gcs_path = f'{base_path}/{restaurant_name}/narration/{narration_file}'
            local_path = os.path.join(local_directory, os.path.basename(narration_file))
            download_blob(bucket_name, narration_gcs_path, local_path)


        #비디오 다운로드 로직
        video_base_path = "Restaurant LUMA Video DB/경상북도/대구/달성군"
        video_gcs_path = f"{video_base_path}/{restaurant_name}/2024-07-23"
        video_folder = [f"{video_gcs_path}/음식/", f"{video_gcs_path}/외관/"]
        local_video_path = f"/Users/zero/STUDY/UGRP/gummy_Video/Restaurant/{restaurant_name}/Video"
        
        num_video=1
        for video_folder_path in (video_folder):
            num_video = download_video_file(bucket_name, video_folder_path, local_video_path, restaurant_name, num_video)
            
if __name__ == '__main__':
    main()

