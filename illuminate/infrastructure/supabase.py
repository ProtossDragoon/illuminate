import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class TranscriptRepository:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table = 'video'

    def add_transcript(self, video_id: str, transcript: str):
        data = {
            'video_id': video_id,
            'transcript': transcript,
        }
        response = self.supabase.table(self.table).insert(data).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f'트랜스크립트 추가 중 오류 발생: {response.error}')
        return response.data[0] if response.data else {}

    def get_transcript(self, video_id: str):
        response = self.supabase.table(self.table).select('*').eq('video_id', video_id).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f'트랜스크립트 조회 중 오류 발생: {response.error}')
        return response.data[0]['transcript'] if response.data else None

    def update_transcript(self, video_id: str, transcript: str):
        data = {
            'transcript': transcript,
        }
        response = self.supabase.table(self.table).update(data).eq('video_id', video_id).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f'트랜스크립트 업데이트 중 오류 발생: {response.error}')

    def delete_transcript(self, video_id: str):
        response = self.supabase.table(self.table).delete().eq('video_id', video_id).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f'트랜스크립트 삭제 중 오류 발생: {response.error}')

    def get_all_transcripts(self):
        response = self.supabase.table(self.table).select('*').execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(f'트랜스크립트 목록 조회 중 오류 발생: {response.error}')


def main():
    repo = TranscriptRepository()

    video_id = 'youtube_123456789'
    transcript = '이것은 샘플 트랜스크립트입니다. 실제 영상의 내용이 들어갑니다.'

    try:
        print('트랜스크립트 추가 중...')
        result = repo.add_transcript(video_id, transcript)
        print(f'트랜스크립트가 추가되었습니다: {result}')

        print('\n트랜스크립트 조회 중...')
        transcript_data = repo.get_transcript(video_id)
        if transcript_data:
            print(f'조회된 트랜스크립트: {transcript_data}')
        else:
            print('트랜스크립트를 찾을 수 없습니다.')

        print('\n트랜스크립트 업데이트 중...')
        updated_transcript = transcript + ' 이 부분은 업데이트된 내용입니다.'
        repo.update_transcript(video_id, updated_transcript)
        print('트랜스크립트가 업데이트되었습니다.')

        print('\n모든 트랜스크립트 조회 중...')
        all_transcripts = repo.get_all_transcripts()
        print(f'총 {len(all_transcripts)}개의 트랜스크립트가 있습니다.')

    except Exception as e:
        print(f'오류 발생: {e}')


if __name__ == '__main__':
    main()
