import subprocess
import shutil
from playwright.sync_api import sync_playwright


# ===== 只需要改这里 =====
PAGE_URL = "https://5v55.com/vodplay/9744-1-13.html"
OUTPUT_FILE = "video.mp4"
WAIT_SECONDS = 60
# =========================


def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("没有找到ffmpeg。先安装ffmpeg，并确保命令行里能直接运行ffmpeg。")


def convert_m3u8_to_mp4(m3u8_url: str, page_url: str, output_file: str, cookie_header: str = ""):
    headers = f"Referer: {page_url}\r\n"

    if cookie_header:
        headers += f"Cookie: {cookie_header}\r\n"

    cmd = [
        "ffmpeg",
        "-y",
        "-user_agent", "Mozilla/5.0",
        "-headers", headers,
        "-i", m3u8_url,
        "-c", "copy",
        "-movflags", "+faststart",
        output_file,
    ]

    print("开始转换：")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)
    print(f"完成：{output_file}")


def main():
    check_ffmpeg()

    found_m3u8 = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            user_agent="Mozilla/5.0",
            ignore_https_errors=True,
        )

        page = context.new_page()

        def on_request(request):
            url = request.url
            if ".m3u8" in url:
                print("发现 m3u8：", url)
                found_m3u8.append(url)

        page.on("request", on_request)

        print("正在打开网页...")
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)

        print("弹出的浏览器里点击播放，等待抓取 m3u8...")

        for _ in range(WAIT_SECONDS):
            if found_m3u8:
                break
            page.wait_for_timeout(1000)

        cookies = context.cookies()
        cookie_header = "; ".join(
            f"{cookie['name']}={cookie['value']}" for cookie in cookies
        )

        browser.close()

    if not found_m3u8:
        print("没有抓到 m3u8。确认已经点击播放，或者延长 WAIT_SECONDS。")
        return

    m3u8_url = found_m3u8[-1]
    print("最终使用m3u8：", m3u8_url)

    convert_m3u8_to_mp4(
        m3u8_url=m3u8_url,
        page_url=PAGE_URL,
        output_file=OUTPUT_FILE,
        cookie_header=cookie_header,
    )


if __name__ == "__main__":
    main()
