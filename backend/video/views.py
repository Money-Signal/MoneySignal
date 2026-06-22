from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from googleapiclient.discovery import build # 상단으로 올리는 것이 좋습니다
import html

@api_view(['GET'])
def search_videos(request):
    try:
        query = request.GET.get('q', '재테크')
        api_key = settings.YOUTUBE_API_KEY
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        api_request = youtube.search().list(
            q=query, 
            part='snippet', 
            type='video', 
            maxResults=12
        )
        response = api_request.execute()
        
        # 🚨 [수정된 부분] 여기서 데이터를 우리가 필요한 모양으로 새로 만듭니다!
        parsed_videos = []
        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            
            video_data = {
                'id': item.get('id', {}).get('videoId'),
                'title': html.unescape(snippet.get('title', '')),
                'channelTitle': snippet.get('channelTitle', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
            }
            parsed_videos.append(video_data)
        
        # 가공된 리스트를 반환합니다.
        return JsonResponse({'videos': parsed_videos}, status=200)

    except Exception as e:
        print(f"!!! 에러 발생: {str(e)} !!!")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def video_detail(request, video_id):
    try:
        api_key = settings.YOUTUBE_API_KEY
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 상세 정보를 가져오는 호출
        request_api = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        )
        response = request_api.execute()
        
        if not response.get('items'):
            return JsonResponse({'error': '영상을 찾을 수 없습니다.'}, status=404)
            
        item = response['items'][0]
        snippet = item['snippet']
        
        # 프론트에서 쓸 수 있게 데이터 정리
        video_data = {
            'id': video_id,
            'title': snippet.get('title'),
            'channelTitle': snippet.get('channelTitle'),
            'description': snippet.get('description'),
            'publishedAt': snippet.get('publishedAt'),
            'viewCount': item.get('statistics', {}).get('viewCount')
        }
        
        return JsonResponse({'video': video_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
def get_related_videos(request, video_id):
    api_key = settings.YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        # 1. 원본 영상에서 채널ID, 태그, 제목 가져오기
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return JsonResponse({'error': '영상을 찾을 수 없습니다.'}, status=404)

        snippet = video_response['items'][0]['snippet']
        channel_id = snippet['channelId']
        tags = snippet.get('tags', [])
        title = snippet.get('title', '')

        # 2. 태그가 있으면 태그로, 없으면 제목 키워드로 검색
        query = ' '.join(tags[:3]) if tags else title

        search_response = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=5,
            relevanceLanguage='ko'
        ).execute()

        related_videos = []
        for item in search_response.get('items', []):
            if item['id']['videoId'] == video_id:  # 원본 영상 제외
                continue
            related_videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'channelTitle': item['snippet']['channelTitle']
            })

        return JsonResponse({'related': related_videos[:4]}, status=200)

    except Exception as e:
        print(f"추천 영상 에러: {e}")
        return JsonResponse({'error': str(e)}, status=500)
