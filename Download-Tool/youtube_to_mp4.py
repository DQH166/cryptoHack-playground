Скачать полное видео с YouTube：yt-dlp + ffmpeg
from pathlib import Path
import yt_dlp


# ===== Просто измените это =====
VIDEO_URL = "https://www.youtube.com/watch?v=l1Ek60xk97k&list=RDmxjw0yi9Vqc&index=2"
OUTPUT_DIR = "downloads"
# ===================


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    ydl_opts = {
        # 优先下载 mp4 视频 + m4a 音频，然后合成 mp4
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",

        # 最终合并成 mp4
        "merge_output_format": "mp4",

        # 输出文件名
        "outtmpl": f"{OUTPUT_DIR}/%(title).80s [%(id)s].%(ext)s",

        # 只下载当前视频，不下载播放列表
        "noplaylist": True,

        # Windows 文件名兼容
        "windowsfilenames": True,

        # 显示进度
        "progress_hooks": [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"下载中：{percent}  速度：{speed}  剩余：{eta}")

    elif d["status"] == "finished":
        print("下载完成，开始合成 MP4...")


if __name__ == "__main__":
    main()
