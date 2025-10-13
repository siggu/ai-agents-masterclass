import yt_dlp

url = "https://www.youtube.com/watch?v=nkxjBzJguWs"

ydl_opts = {
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "./temp.%(ext)s",
    "merge_output_format": "mp4",
    "postprocessors": [
        {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }
    ],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    title = info.get("title", "Unknown")
    print(f"'{title}' 다운로드 완료")
