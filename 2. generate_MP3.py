import os
import uuid
from dotenv import load_dotenv
from google.cloud import storage
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# .env 파일에서 환경 변수 로드
load_dotenv()

# ElevenLabs API 설정
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Google Cloud Storage 클라이언트 초기화 (서비스 계정 키 파일 사용)
storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def get_restaurant_names_from_gcs(bucket_name, prefix):
    """Google Cloud Storage에서 지정된 경로의 하위 폴더 이름을 가져옴"""
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix, delimiter='/')
    restaurant_names = set()

    for page in blobs.pages:
        restaurant_names.update(page.prefixes)

    # 경로에서 식당 이름만 추출
    return [name.split('/')[-2] for name in restaurant_names if name.endswith('/') and name != prefix]


def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names

def read_text_from_gcs(bucket_name, blob_name):
    """Google Cloud Storage에서 텍스트 파일 내용 읽기"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    text_content = blob.download_as_text(encoding='utf-8')
    return text_content

def upload_audio_to_gcs(bucket_name, destination_blob_name, audio_content):
    """Google Cloud Storage에 오디오 파일 내용 업로드"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(audio_content, content_type='audio/mpeg')
    print(f"Uploaded audio content to bucket {bucket_name} as {destination_blob_name}.")

def text_to_speech_file(text: str, restaurant_name) -> bytes:
    """텍스트를 음성으로 변환하여 바이트 배열로 반환"""
    response = client.text_to_speech.convert(
        voice_id='d8C3IjQocptPVwhAEhxm',  #UI REAL
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.30,
            similarity_boost=0.8,
            style=0.55,
            use_speaker_boost=True,
        ),
    )

    # 오디오를 바이트 배열로 저장
    audio_content = b""
    for chunk in response:
        if chunk:
            audio_content += chunk

    print(f"{restaurant_name}: Audio content was generated successfully!")
    return audio_content

def process_restaurant(restaurant_name):
    base_path = 'Restaurant Photo DB/경상북도/대구/달성군'
    gcs_txt_file_path = f'{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.txt'

    # GCS에서 텍스트 파일 내용 읽기
    text_content = read_text_from_gcs(bucket_name, gcs_txt_file_path)

    # 텍스트를 음성으로 변환하여 바이트 배열로 저장
    audio_content = text_to_speech_file(text_content, restaurant_name)

    # 생성된 mp3 파일을 GCS에 업로드
    gcs_mp3_file_path = gcs_txt_file_path.replace('.txt', '.mp3')
    upload_audio_to_gcs(bucket_name, gcs_mp3_file_path, audio_content)
    print(f"MP3 파일이 성공적으로 저장되었습니다: {gcs_mp3_file_path}")

def main():


    """Google GCS 모든 디렉터리 접근"""
    #restaurant_names = get_restaurant_names_from_gcs(bucket_name, base_path)
    
    restaurant_names_path = "/Users/zero/STUDY/UGRP/Google Cloud/restaurant_List.txt"
    restaurant_names = get_restaurant_names_from_txt(restaurant_names_path)
    text_restaurant=[]
    for i, restaurant_name in enumerate(restaurant_names):
        text_restaurant.append(restaurant_name)
        
        try:
            process_restaurant(restaurant_name)
        except Exception as e:
            print(f"Failed to process {restaurant_name}: {e}")


    file_path = "/Users/zero/STUDY/UGRP/Google Cloud/elevenLabs_Restaurant.txt"

    with open(file_path, 'w') as file: 
        for text in text_restaurant:
            file.write(f"{text}\n")

if __name__ == '__main__':
    main()
