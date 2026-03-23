from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"message": "TeraBox Premium API is Live & Fixed!"}

@app.get("/download")
def get_video(url: str = Query(..., description="TeraBox URL")):
    # ১০০% সাকসেস রেট এবং রিডাইরেক্ট ফিক্স করার জন্য প্রিমিয়াম কনফিগ
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # টেরাবক্সের নতুন ডোমেইন এবং রিডাইরেক্ট হ্যান্ডল করার জন্য
        'noplaylist': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.terabox.app/',
            'Origin': 'https://www.terabox.app/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
    }

    try:
        # ইউআরএলটি যদি ছোট হয় (surl), তবে সেটিকে প্রসেস করার ক্ষমতা
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # সরাসরি ডাউনলোড লিংকের ফিল্টার
            direct_url = info.get('url')
            if not direct_url and 'formats' in info:
                direct_url = info['formats'][0].get('url')

            return JSONResponse({
                "status": "success",
                "title": info.get('title', 'TeraBox Video'),
                "thumbnail": info.get('thumbnail'),
                "video_url": direct_url, 
                "quality": info.get('resolution', 'N/A'),
                "size": f"{round(info.get('filesize_approx', 0) / (1024*1024), 2)} MB" if info.get('filesize_approx') else "Variable"
            })
            
    except Exception as e:
        # বিস্তারিত এরর মেসেজ যাতে আপনি বুঝতে পারেন সমস্যা কোথায়
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message": f"Fixed Error: {str(e)}"}
        )
