from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"message": "TeraBox Direct API is Live!"}

@app.get("/download")
def get_video(url: str = Query(..., description="TeraBox URL")):
    # ১০০% সাকসেস রেট পাওয়ার জন্য হাই-কোয়ালিটি কনফিগ
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return JSONResponse({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "video_url": info.get('url'), # ডিরেক্ট ডাউনলোড লিংক
                "quality": info.get('resolution'),
                "size": f"{round(info.get('filesize_approx', 0) / (1024*1024), 2)} MB" if info.get('filesize_approx') else "Variable"
            })
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
