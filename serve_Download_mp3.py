from google.cloud import storage

storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def read_audio_from_gcs(bucket_name, blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    audio_content = blob.download_as_bytes()
    return audio_content

def save_audio_to_local(file_path, audio_content):
    with open(file_path, 'wb') as file:
        file.write(audio_content)

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names

def main():
    base_path = 'Restaurant Photo DB/경상북도/대구/달성군'

    restaurant_names_path = "/Users/zero/STUDY/UGRP/Google Cloud/restaurant_List.txt"

    restaurant_names = get_restaurant_names_from_txt(restaurant_names_path)

    for restaurant_name in restaurant_names:
        audio_file_path = f'{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.mp3'
        audio_content = read_audio_from_gcs(bucket_name, audio_file_path)



        local_file_path = f'/Users/zero/STUDY/UGRP/Google Cloud/ExtendScript Error/{restaurant_name}_promo_reel.mp3'
        save_audio_to_local(local_file_path, audio_content)
        print(f"Downloaded Successful from {audio_file_path} to {local_file_path}")


if __name__ == "__main__":
    main()