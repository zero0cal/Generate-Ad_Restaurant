from google.cloud import storage

storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()

    return restaurant_names


def save_srt_to_gcs(txt_content, bucket_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(txt_content, content_type='text/plain')
    print(f"txt file uploaded to GCS at: gs://{bucket_name}/{destination_blob_name}")


def upload_audio_to_gcs(audio_content, bucket_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(audio_content, content_type = 'audio/mgeg')
    print(f"Uploaded audio content to bucket {bucket_name} as {destination_blob_name}.")


def read_local_text_file(file_path):
    with open(file_path, 'r', encoding = 'utf-8') as file:
        return file.read()
    

def read_local_audio_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()
    


def main():
    base_path = 'Restaurant Photo DB/경상북도/대구/달성군'


    restaurant_list_path = "/Users/zero/STUDY/UGRP/Google Cloud/restaurant_List.txt"
    restaurant_names = get_restaurant_names_from_txt(restaurant_list_path)


    for restaurant_name in restaurant_names:
        txt_path =f"/Users/zero/STUDY/UGRP/Google Cloud/ExtendScript Error/{restaurant_name}_promo_reel.txt"
        audio_path = f"/Users/zero/STUDY/UGRP/Google Cloud/ExtendScript Error/{restaurant_name}_promo_reel.mp3"

        txt_content = read_local_text_file(txt_path)
        audio_content = read_local_audio_file(audio_path)

        txt_gcs_path = f"{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.txt"
        audio_gcs_path = f"{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.mp3"

        save_srt_to_gcs(txt_content, bucket_name, txt_gcs_path)
        upload_audio_to_gcs(audio_content, bucket_name, audio_gcs_path)

if __name__=='__main__':
    main()
        