import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase 서비스 계정 키 파일 경로
cred = credentials.Certificate('/Users/zero/STUDY/UGRP/Video Pipeline/Firebase/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_master_address():
    # Firestore에서 사장님의 "도로명 주소" 가져오기
    db = firestore.client()
    user_ref = db.collection('users').document(master.uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise Exception("사장님의 접근이 아닙니다.")

    data = user_doc.to_dict()

    # 데이터가 null이거나 필요한 필드가 없는 경우 예외 처리
    if data is None or 'address' not in data or 'master_restaurant' not in data:
        raise Exception("사장님의 접근이 아닙니다.")

    # 필요한 필드를 가져옴
    address = data.get('address', '')
    restaurant_name = data.get('master_restaurant', '')

    return {'address': address, 'restaurant_name': restaurant_name}

def from_data(master_info):
    try:
        restaurant_name = master_info.get('restaurant_name')
        address_parts = master_info.get('address', '').split(' ')
        region = address_parts[0] if len(address_parts) > 0 else ""
        city = address_parts[1] if len(address_parts) > 1 else ""

        db = firestore.client()

        # 동영상 컬렉션에서 해당 식당의 비디오 문서 가져오기
        video_snapshots = db.collection('restaurants').document(region).collection(region).document(city).collection("동영상").where('restaurantName', '==', restaurant_name).get()

        restaurant_doc_ref = db.collection('restaurants').document(region).collection(region).document(city).collection("식당").document(restaurant_name)  # Restaurant Document Reference

        video_doc_refs = [doc.reference for doc in video_snapshots]

        restaurant_doc_ref.update({
            'activeVideo_List': video_doc_refs,
        })

        print("Video document references updated successfully.")
    except Exception as e:
        print(f"Error: {e}")


def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names


restaurant_names = get_restaurant_names_from_txt("/Users/zero/STUDY/UGRP/Video Pipeline/Google Cloud/restaurant_List.txt")


for i,restaurant_name in enumerate(restaurant_names):
    if i==30:
        break
    restaurant_doc_ref = db.collection('restaurants')\
                            .document("대구광역시")\
                            .collection("대구광역시")\
                            .document("달성군")\
                            .collection("식당")\
                            .document(restaurant_name)\
                            .get()\
                            .to_dict()
    
    info = {"address": restaurant_doc_ref.get("도로명주소"), "restaurant_name": restaurant_doc_ref.get("음식점명")}
    
# current_user_id를 실제 사용자의 UID로 설정하세요

    from_data(info)