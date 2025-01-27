from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled


# 지금 한글자막을 가져오고있는 영상은 '워뇨띠 매매법' 영상임.

try:
    # 'ko'를 넣어서 한국어 자막을 가져오도록 설정했어!
    transcript = YouTubeTranscriptApi.get_transcript("EiDXQmOQ6_o", languages=['ko'])
    # text만 뽑아서 하나의 문자열로 만들기
    full_text = ' '.join([line['text'] for line in transcript])
    print(full_text)
except TranscriptsDisabled:
    print("앗! 이 영상에는 자막이 없어요 😢")