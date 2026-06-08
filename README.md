# video-to-m4a

A small CLI tool that picks a recent video file and converts it to an `.m4a` audio file.

## What it does

1. Scans the current directory for video files
   (mp4, mov, mkv, avi, webm, m4v, flv, wmv) and lists up to 10,
   newest modified first, with their sizes.
2. You pick a number, and it extracts the audio from that video.
3. The output name starts with a fixed timestamp prefix from the video's
   **creation time**: `YYYYMMDD_HHMM_` (for example `2020260608_1405_`).
   You can then type the rest of the name, or press Enter to keep the
   original file name.

## Requirements

- Python 3.7+
- [ffmpeg](https://ffmpeg.org/)

```sh
brew install ffmpeg
```

## Usage

Run it from the folder that contains your videos.

```sh
cd <folder with videos>
python3 video_to_m4a.py
```

Example session:

```
Recent video files:

  [1] my_clip.mov  (24.3MB)
  [2] lecture.mp4  (512.0MB)

Select a number to convert (1-2, Enter to cancel): 1

Output name example: 20260608_1405_my_clip.m4a
Type a name after '20260608_1405_' (Enter to keep 'my_clip'): interview

Converting: my_clip.mov -> 20260608_1405_interview.m4a

Done: 20260608_1405_interview.m4a
```

Pressing Enter at the name prompt would produce `20260608_1405_my_clip.m4a`.

## How the conversion works

ffmpeg drops the video stream (`-vn`) and re-encodes the audio to AAC at
192 kbps. This works regardless of the source's original audio codec.

## License

MIT
