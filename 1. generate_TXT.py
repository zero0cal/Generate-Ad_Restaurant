import firebase_admin
from firebase_admin import credentials, firestore
import openai
import os
from dotenv import load_dotenv
from google.cloud import storage

#.env파일에서 API 키 로드
load_dotenv()

#OpenAI API 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

#Firebase 초기화
cred = credentials.Certificate("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


#Google Cloud Storage 클라이언트 초기화
storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def get_restaurant_names(base_path):
    #base_path 하위의 모든 식당 폴더 이름을 가져오자.
    restaurant_ref = db.collection(base_path)
    restaurants = restaurant_ref.stream()
    print("restaurant::   ", restaurants)
    restaurant_names = [restaurant.id for restaurant in restaurants]
    return restaurant_names

def get_reviews(restaurant_path):
    reviews_ref = db.collection(restaurant_path)
    reviews = reviews_ref.limit(30).stream()

    reviews_list = [review.to_dict() for review in reviews]
    reviews_text = " ".join([value for review in reviews_list for value in review.values() if value.strip() ])

    #if value.strip()로직은 공백 문자가 join 안 되게금
    return reviews_text

def create_promo_reel(restaurant_name, reviews):
    #리뷰 텍스트 합치기

    #각 리뷰에서 'text'키가 있는지  확인하고, 'text'키가 존재하는 곳에서만 'text'필드의 값을 추출
    prompt = f"{restaurant_name}의 리뷰는 \n{reviews}\n. 안녕하세요와 같은 소개 인사는 빼고, 음식을 정말 먹고싶게끔 하는 디테일한 표현을 넣어서, 공백 포함 125 음절로 생성해야해! 한국어로 작성해야해. 한국인 30대가 거부감이 드는 추임새는 사용하지마."


    response = openai.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": "한국 가게의 음식 광고 나레이션을 만들거야. 한국인 여성 20대가 보기에 거부감이 없게끔 나레이션 대본을 생성해"},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 110,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature = 0
    )
    print("response:    ", response.choices[0].message.content.strip())

    return response.choices[0].message.content.strip()

def upload_to_gcs(bucket_name, destination_blob_name, content): 
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(content, content_type='text/plain')
    print(f"File uploaded to {destination_blob_name} in bucket {bucket_name}")


def main():
    base_path = 'restaurants/경상북도/대구/달성군/식당'
    restaurant_names = get_restaurant_names(base_path)

    for i, restaurant_name in enumerate(restaurant_names):

        restaurant_path = f"{base_path}/{restaurant_name}/리뷰"
        reviews = get_reviews(restaurant_path)
        
        #리뷰 잘 나오는거 확인
        #print("reviews:  ", reviews, '\n')

        if reviews:
            promo_reel = create_promo_reel(restaurant_name, reviews)
            destination_blob_name  = f"Restaurant Photo DB/경상북도/대구/달성군/{restaurant_name}/narration/{restaurant_name}_promo_reel.txt"
            upload_to_gcs(bucket_name, destination_blob_name, promo_reel.encode('utf-8'))
        else:
            print(f"No reviews found for {restaurant_name}")

        

#다른 모듈에서도 간편하게 사용할 수 있게끔
if __name__ == '__main__':
    main()