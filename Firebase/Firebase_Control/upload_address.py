import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import requests


cred = credentials.Certificate('/Users/zero/STUDY/UGRP/Video Pipeline/Firebase/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_lat_lng(address):
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET
    }
    params = {"query": address}

    try:
        response = requests.get(GEOCODING_API_URL, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            if 'addresses' in result and len(result['addresses']) > 0:
                lat = float(result['addresses'][0]['y'])
                lng = float(result['addresses'][0]['x'])
                return lat, lng
            else:
                return None, None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"Error geocoding address {address}: {e}")
        return None, None

def update_restaurant_lat_lng():
    # Firestore에서 도로명주소 가져오기
    restaurants_ref = db.collection('restaurants').document('대구광역시').collection('대구광역시').document('달성군').collection('식당')
    docs = restaurants_ref.stream()

    for doc in docs:
        data = doc.to_dict()
        address = data.get('도로명주소')
        
        if address:
            lat, lng = get_lat_lng(address)
            if lat and lng:
                print(f"Updating {doc.id} with lat: {lat}, lng: {lng}")
                # Firestore에 위도, 경도 업데이트
                doc.reference.update({
                    'latitude': lat,
                    'longitude': lng,
                    '위도':firestore.DELETE_FIELD,
                    '경도':firestore.DELETE_FIELD,
                })
            else:
                print(f"Could not geocode address: {address}")
        else:
            print(f"No address found for document {doc.id}")

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names


if __name__ == "__main__":
    """restaurant_names = get_restaurant_names_from_txt("/Users/zero/STUDY/UGRP/Video Pipeline/Google Cloud/restaurant_List.txt")
    
    for restaurant_name in restaurant_names:

        restaurant_doc_ref = db.collection('restaurants')\
                                .document("대구광역시")\
                                .collection("대구광역시")\
                                .document("달성군")\
                                .collection("동영상")\
                                .document(restaurant_name)"""
    
    update_restaurant_lat_lng()