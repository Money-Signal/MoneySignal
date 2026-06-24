import html
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from googleapiclient.discovery import build

YOUTUBE_PAGE_MAP = {}

@api_view(['GET'])
@permission_classes([AllowAny]) # 혹시 몰라 비로그인 유저도 접근 가능하도록 권한 명시
def search_videos(request):
    global YOUTUBE_PAGE_MAP
    
    try:
        query = request.GET.get('q', '재테크')
        
        # 🎯 [신규] 프론트엔드에서 숫자로 된 페이지 번호를 받습니다. (기본값 1)
        try:
            current_page = int(request.GET.get('page', 1))
        except ValueError:
            current_page = 1
            
        # 🎯 [신규] 프론트엔드에서 원하는 정렬 기준을 받습니다. (기본값은 유튜브 기본 추천순인 'relevance')
        sort_by = request.GET.get('sort_by', 'relevance') 
        
        api_key = settings.YOUTUBE_API_KEY
        max_results = 6 # 한 페이지당 6개 (반응형 3열 배치를 위해 6개 고정)
        
        # 🎯 [신규] 1페이지가 아니면 보관함에서 정렬_페이지 규격에 맞는 토큰 열쇠를 꺼냅니다.
        page_token = "" if current_page == 1 else YOUTUBE_PAGE_MAP.get(f"{sort_by}_{current_page}", "")
        
        # 유튜브 API 빌드
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 🎯 [수정] maxResults를 6으로 맞추고, order와 pageToken을 동적으로 바인딩합니다.
        api_request = youtube.search().list(
            q=query, 
            part='snippet', 
            type='video', 
            maxResults=max_results,
            order=sort_by,          # 👈 relevance / viewCount / date 가 동적으로 주입됩니다.
            pageToken=page_token if page_token else None # 👈 토큰이 있을 때만 탑승
        )
        response = api_request.execute()
        print(f"[DEBUG] 요청 페이지: {current_page}, 실제 받은 영상 수: {len(response.get('items', []))}")
        
        # 전체 결과 수 계산
        total_results = response.get('pageInfo', {}).get('totalResults', 0)
        
        # 🎯 [신규] 아무리 결과가 많아도 우리 서비스는 최대 5페이지(총 30개 영상)로 엄격히 잠금!
        total_pages = min((total_results // max_results) + 1, 5) 
        
        # 🎯 [신규] 유튜브가 다음 페이지용 열쇠를 줬다면, 다음 숫자의 몫으로 보관함에 킵해둡니다.
        next_page_token = response.get('nextPageToken', '')
        if next_page_token:
            YOUTUBE_PAGE_MAP[f"{sort_by}_{current_page + 1}"] = next_page_token
        
        # 데이터 가공 영역 (기본 구조 유지)
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
        
        # 🎯 [수정] 프론트엔드가 페이지네이션을 그릴 수 있도록 현재 페이지와 총 페이지 수를 함께 반환합니다.
        return JsonResponse({
            'videos': parsed_videos,
            'currentPage': current_page,
            'totalPages': total_pages
        }, status=200)

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
            maxResults=10,
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

        return JsonResponse({'related': related_videos[:6]}, status=200)

    except Exception as e:
        print(f"추천 영상 에러: {e}")
        return JsonResponse({'error': str(e)}, status=500)
