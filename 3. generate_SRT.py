from google.cloud import speech
from google.cloud import storage
import difflib

storage_client = storage.Client.from_service_account_json("/Users/zero/STUDY/UGRP/Google Cloud/firebase/serviceAccountKey.json")
bucket_name = 'ugrp-server-73535.appspot.com'

def get_restaurant_names_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurant_names = file.read().splitlines()
    
    return restaurant_names

def read_audio_from_gcs(bucket_name, blob_name):
    #Google Cloud Storage에서 오디오 파일 내용 읽기
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    audio_content=blob.download_as_bytes()
    return audio_content


def transcribe_audio(audio_content):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # WAV 형식 사용
        sample_rate_hertz=16000,  # 오디오 파일의 샘플링 레이트 설정
        language_code="ko-KR",    # 한국어 설정
        enable_word_time_offsets=True,  # 단어 타임스탬프 활성화
        use_enhanced=True,  # 고급 모델 사용
        model="latest_long",  # 최신 롱 폼 모델 사용
    )

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        print("No transcription results. Please check the audio file and settings.")
    else:
        print("Transcription results obtained.")
    


    return response

def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    return f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{millis:03}"

def count_syllables(word):
    # 한국어 음절 수 계산 (기본적으로 한 글자가 한 음절)
    return len(word)

def create_srt(transcription_response):
    srt_content = []
    index = 1
    words_with_timestamps = []
    
    for result in transcription_response.results:
        for alternative in result.alternatives:
            for word_info in alternative.words:
                #print("word:: ", word_info.word, '\n')
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                word = word_info.word.replace('▁', ' ')  # ▁ 문자를 공백으로 대체

                words_with_timestamps.append([start_time, end_time, word])


    #더 정확하게 음성 인식을 하기 위한 프로세스
    #공백 기준으로 음절을 단어로 바꿔주자
    i = 0
    new_timestamps = []
    first_word = words_with_timestamps[0][2]
    words_with_timestamps[0][2] = first_word[1:]

    while i<len(words_with_timestamps):
        start_time = words_with_timestamps[i][0]
        new_word = words_with_timestamps[i][2]
        j=i+1
        while j<len(words_with_timestamps) and (words_with_timestamps[j][2].strip()):
            #' 된장찌개'와 같은 경우
            if(len(words_with_timestamps[j][2])>=2 and words_with_timestamps[j][2][0]== ' '): 
                #' ' 띄어쓰기 미리 처리하기
                end_time = words_with_timestamps[j-1][1]
                new_timestamps.append([start_time, end_time, new_word])

                start_time = words_with_timestamps[j][0]
                new_word = ""
                new_word = "".join([new_word, words_with_timestamps[j][2][1:]])

            else:new_word = "".join([new_word, words_with_timestamps[j][2]])

            j+=1


        if(j<len(words_with_timestamps)): end_time = words_with_timestamps[j][1]
        else: end_time = words_with_timestamps[j-1][1]

        new_timestamps.append([start_time, end_time, new_word])
        i=j+1


    i = 0
    new_timestamps[0][0] += 0.001


    #단어수 길이 조정 Core 파트
    while i < len(new_timestamps):
        start_time = new_timestamps[i][0]
        end_time = new_timestamps[i][1]
        words = new_timestamps[i][2]
        syllable_count = count_syllables(words)

        j = i + 1
        while j < len(new_timestamps) and syllable_count < 10:
            syllable_count += count_syllables(new_timestamps[j][2])
            if syllable_count <= 10:
                end_time = new_timestamps[j][1]
                words += ' ' + new_timestamps[j][2]
                j += 1
            else:
                break

        srt_content.append(f"{index}\n{format_time(start_time)} --> {format_time(end_time)}\n{words}\n")
        index += 1
        i = j

    if not srt_content:  # 디버깅: SRT 내용이 비어 있는 경우 경고
        print("Warning: SRT content is empty. No transcription results.")

    return "\n".join(srt_content)

def read_text_from_gcs(bucket_name, blob_name):
    """Google Cloud Storage에서 정답 텍스트 파일 내용 읽기"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    text_content = blob.download_as_text(encoding='utf-8')
    return text_content

# 문장을 음절 단위로 나누기.
def split_to_syllables(text):
    return list(text)

def correct_line_syllables(line, correct_syllables, offset):
    words = line.split()
    corrected_line = []
    
    for word in words:
        word_cleaned = word.replace(" ", "")
        word_syllables = split_to_syllables(word_cleaned)
        corrected_syllables = []

        for idx, syllable in enumerate(word_syllables):
            #index가 가까운 음절과 우선적으로 유사도 판별
            rel_idx = min(idx + offset, len(correct_syllables) - 1)
            rel_syllable = correct_syllables[rel_idx]
            matches = difflib.get_close_matches(syllable, [rel_syllable], n=1, cutoff=0.5)
            if matches:
                corrected_syllables.append(matches[0])
            else:
                #음절이 비슷한 경우가 없을 때, 정답본의 음절로 대치
                """ Expected Error Case: Numeric Value일 경우, 발음과 정답본의 차이가 극심 ---> elevenlabs와 speech2text model의 진척 상황을 보고 판별"""
                corrected_syllables.append(rel_syllable)

        corrected_word = ''.join(corrected_syllables)
        corrected_line.append(corrected_word)
        offset += len(word_syllables)

    return ' '.join(corrected_line), offset

#correct_srt_file에 들어갈 byte 반환
def correct_srt_file(srt_content, correct_syllables):
    corrected_srt_lines = []
    offset = 0  #offset 기반으로 정답본과 SRT 파일의 index 파악

    for line in srt_content.split('\n'):
        if '-->' in line or line.isdigit() or line.strip() == '':
            corrected_srt_lines.append(line)
        else:
            # 음절 기반으로 수정된 문장과 offset을 update 
            corrected_line, offset = correct_line_syllables(line, correct_syllables, offset)
            corrected_srt_lines.append(corrected_line)

    return '\n'.join(corrected_srt_lines)


def save_srt_to_gcs(srt_content, bucket_name, srt_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(srt_blob_name)
    blob.upload_from_string(srt_content, content_type='text/plain')
    print(f"SRT file uploaded to GCS at: gs://{bucket_name}/{srt_blob_name}")

# 경로 설정
restaurant_names_path = "/Users/zero/STUDY/UGRP/Google Cloud/elevenLabs_Restaurant.txt"

# 변환 및 SRT 파일 생성
restaurant_names = get_restaurant_names_from_txt(restaurant_names_path)


def main():
    # 경로 설정
    base_path = 'Restaurant Photo DB/경상북도/대구/달성군'
    restaurant_names_path = "/Users/zero/STUDY/UGRP/Google Cloud/elevenLabs_Restaurant.txt"
    restaurant_names = get_restaurant_names_from_txt(restaurant_names_path)
    success = []

    for i, restaurant_name in enumerate(restaurant_names):
        
        try:
            audio_file_path = f'{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.mp3'
            audio_content = read_audio_from_gcs(bucket_name, audio_file_path)
            response = transcribe_audio(audio_content)
        
            srt_file_path = f'{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.srt'
            srt_content = create_srt(response)

            #srt_content 후처리
            text_file_path = f"{base_path}/{restaurant_name}/narration/{restaurant_name}_promo_reel.txt"
            correct_sentence = read_text_from_gcs(bucket_name, text_file_path)

            correct_sentence_cleaned = correct_sentence.replace(" ","").replace(",","").replace("!", "").replace(".", "")
            correct_syllables = split_to_syllables(correct_sentence_cleaned)
            corrected_srt_content = correct_srt_file(srt_content, correct_syllables)
        
            save_srt_to_gcs(corrected_srt_content, bucket_name, srt_file_path)

            success.append(restaurant_name)

        except Exception as e:
            print(f"Failed to process {restaurant_name}: {e}")


    file_path = "/Users/zero/STUDY/UGRP/Google Cloud/success_srt_list.txt"
    with open(file_path, 'w') as file: 
        file.write(f"{len(success)}\n")
        for text in success:
            file.write(f"{text}\n")
   
       

if __name__ == '__main__':
    main()
    

