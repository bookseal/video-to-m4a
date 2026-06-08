# video-to-m4a

최근 동영상 파일을 골라 같은 이름의 `.m4a` 오디오로 변환하는 간단한 CLI 도구.

## 동작

1. 현재 디렉터리에서 동영상 파일(mp4, mov, mkv, avi, webm, m4v, flv, wmv)을 찾아
   **최신 수정순**으로 최대 10개를 크기와 함께 나열한다.
2. 번호를 선택하면 해당 동영상의 오디오를 추출한다.
3. 출력 파일명은 `원본이름_YYYYMMDD_HHMMSS.m4a` 형식으로,
   동영상의 **생성 시각**이 붙는다.

## 요구사항

- Python 3.7+
- [ffmpeg](https://ffmpeg.org/)

```sh
brew install ffmpeg
```

## 사용법

동영상이 있는 폴더에서 실행한다.

```sh
cd <동영상 폴더>
python3 video_to_m4a.py
```

```
최근 동영상 파일:

  [1] my_clip.mov  (24.3MB)
  [2] lecture.mp4  (512.0MB)

변환할 번호를 선택하세요 (1-2, 취소: Enter): 1

변환 중: my_clip.mov → my_clip_20260608_230503.m4a

완료: my_clip_20260608_230503.m4a
```

## 변환 방식

ffmpeg로 비디오 스트림을 제거(`-vn`)하고 오디오를 AAC 192k로 재인코딩한다.
원본 오디오 코덱과 무관하게 항상 동작한다.

## License

MIT
