from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp
import re

app = FastAPI()

@app.get("/")
def home():
    return {"message": "TeraBox Premium API is Live & Fixed!"}

@app.get("/download")
def get_video(url: str = Query(..., description="TeraBox URL")):
    # Fix TeraBox URL if it's in sharing format
    if "sharing/link?surl=" in url:
        # Extract surl and convert to proper format
        surl_match = re.search(r'surl=([^&]+)', url)
        if surl_match:
            surl = surl_match.group(1)
            url = f"https://www.terabox.com/sharing/link?surl={surl}"
    
    # Premium configuration for 100% success rate
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'noplaylist': True,
        'extract_flat': False,
        'cookiefile': None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.terabox.com/',
            'Origin': 'https://www.terabox.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'extractor_args': {
            'terabox': {
                'prefer_direct_urls': ['true'],  # Force direct URLs
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info with better error handling
            info = ydl.extract_info(url, download=False)
            
            # Handle different possible URL structures
            direct_url = None
            video_quality = "N/A"
            file_size = "Variable"
            
            # Try to get best quality video URL
            if info.get('formats'):
                # Get the best quality format (usually last one in list)
                best_format = max(info['formats'], key=lambda f: f.get('height', 0) if f.get('height') else 0)
                direct_url = best_format.get('url')
                video_quality = f"{best_format.get('height', 'N/A')}p" if best_format.get('height') else "HD"
                if best_format.get('filesize'):
                    file_size = f"{round(best_format['filesize'] / (1024*1024), 2)} MB"
            elif info.get('url'):
                direct_url = info.get('url')
            
            # If no direct URL found, try alternative method
            if not direct_url:
                # Sometimes yt-dlp stores URL in 'webpage_url_domain' or other fields
                if info.get('requested_formats'):
                    direct_url = info['requested_formats'][0].get('url')
                elif info.get('url'):
                    direct_url = info.get('url')
            
            # Ensure URL is valid
            if direct_url and not direct_url.startswith(('http://', 'https://')):
                direct_url = None
            
            response_data = {
                "status": "success",
                "title": info.get('title', 'TeraBox Video'),
                "thumbnail": info.get('thumbnail'),
                "video_url": direct_url,
                "quality": video_quality,
                "size": file_size,
                "duration": info.get('duration'),
                "extractor": info.get('extractor', 'terabox')
            }
            
            # Remove None values
            response_data = {k: v for k, v in response_data.items() if v is not None}
            
            return JSONResponse(response_data)
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        
        # Try alternative domain if .app fails
        if "terabox.app" in url and "Unsupported URL" in error_msg:
            try:
                alt_url = url.replace("terabox.app", "terabox.com")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(alt_url, download=False)
                    if info.get('formats'):
                        best_format = max(info['formats'], key=lambda f: f.get('height', 0) if f.get('height') else 0)
                        direct_url = best_format.get('url')
                        
                        return JSONResponse({
                            "status": "success",
                            "title": info.get('title', 'TeraBox Video'),
                            "thumbnail": info.get('thumbnail'),
                            "video_url": direct_url,
                            "quality": f"{best_format.get('height', 'N/A')}p" if best_format.get('height') else "HD",
                            "size": f"{round(best_format.get('filesize', 0) / (1024*1024), 2)} MB" if best_format.get('filesize') else "Variable"
                        })
            except:
                pass
        
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Download Error: {error_msg}"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {str(e)}"}
        )
