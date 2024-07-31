import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('/Users/zero/STUDY/UGRP/Video Pipeline/Firebase/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore (Assuming Firebase Admin SDK is already initialized)
db = firestore.client()

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names

def parse_and_update_document(restaurant_name):
    # Fetch the document from the "식당" collection
    restaurant_doc_ref = db.collection('restaurants')\
                           .document("대구광역시")\
                           .collection("대구광역시")\
                           .document("달성군")\
                           .collection("식당")\
                           .document(restaurant_name)
    
    restaurant_doc = restaurant_doc_ref.get()
    if not restaurant_doc.exists:
        print(f"Document {restaurant_name} does not exist in the 식당 collection.")
        return

    data = restaurant_doc.to_dict()

    # Parse the fields
    if data.get('관리') != "O":
        print(f"Pass: {data.get('음식점명')} 관리 값이 O가 아닙니다.")
        return

    restaurant_name = data.get('음식점명')
    restaurant_address = data.get('도로명주소')
    information = data.get('매장정보')
    info_list = information.split(',') if information else []
    restaurant_telephone = data.get('일반전화')

    opening_hour = data.get("영업시간")
    formatted_opening_hours_map = {}
    if opening_hour:
        business_hours_map = json.loads(opening_hour)
        for key, value in business_hours_map.items():
            values = value.split('\n')
            formatted_opening_hours_map[key] = values
    else:
        print(f'"{restaurant_name}"에 영업시간 정보가 존재하지 않습니다.')

    menus = json.loads(data.get("메뉴", "[]"))
    food_category = data.get('카테고리')
    food_category_list = food_category.split(',') if food_category else []

    # Update the document in the "동영상" collection
    video_doc_ref = db.collection('restaurants')\
                      .document("대구광역시")\
                      .collection("대구광역시")\
                      .document("달성군")\
                      .collection("동영상")\
                      .document(restaurant_name)

    video_doc_ref.update({
        '음식점명': restaurant_name,
        '도로명주소': restaurant_address,
        '매장정보': info_list,
        '일반전화': restaurant_telephone,
        '영업시간': formatted_opening_hours_map,
        '메뉴': menus,
        '카테고리': food_category_list
    })

    print(f"Document {restaurant_name} in 동영상 collection updated successfully.")

    # Fetch reviews from the "리뷰" collection
    reviews_query_snapshot = restaurant_doc_ref.collection("리뷰").get()

    for review_document in reviews_query_snapshot:
        review_data = review_document.to_dict()
        
        # Add each review to the "reviews" collection in the "동영상" document
        video_doc_ref.collection("reviews").add(review_data)

    print(f"Reviews for {restaurant_name} added successfully to the 동영상 collection.")


restaurant_names = get_restaurant_names_from_txt("/Users/zero/STUDY/UGRP/Video Pipeline/Google Cloud/restaurant_List.txt")
for restaurant_name in restaurant_names:
    parse_and_update_document(restaurant_name)
