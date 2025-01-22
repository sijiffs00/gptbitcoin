from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

try:
    transcript = YouTubeTranscriptApi.get_transcript("-59bKxwir5Q")
    # text만 뽑아서 하나의 문자열로 만들기
    full_text = ' '.join([line['text'] for line in transcript])
    print(full_text)
except TranscriptsDisabled:
    print("앗! 이 영상에는 자막이 없어요 😢")