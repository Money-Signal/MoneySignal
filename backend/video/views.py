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