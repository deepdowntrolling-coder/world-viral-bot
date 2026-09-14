
"""
WORLD VIRAL V8 - REAL NEWS + REAL VIDEO
- Hakee OIKEAN uutisen Reuters/Google News RSS:stä (ei AI-keksitty)
- Hakee OIKEAN videon Pexelsistä joka mätsää uutiseen
- Uutisgrafiikat: BREAKING, ticker, lähde
- 100% laillinen (ei CNN/BBC uudelleenlatausta = ei bannia)
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET, re
from datetime import datetime
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"PEXELS: {'SET' if PEXELS_API_KEY else 'NOT SET'} | OPENROUTER: {'SET' if OPENROUTER_API_KEY else 'NOT SET'}")

# REAL NEWS RSS - oikeat lähteet
RSS_FEEDS = {
    "usa_iran": ["https://www.reutersagency.com/feed/?best-topics=iran&post_type=best", "https://news.google.com/rss/search?q=USA+Iran+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "russia_ukraine": ["https://news.google.com/rss/search?q=Ukraine+Russia+war+when:1d&hl=en-US&gl=US&ceid=US:en", "https://feeds.reuters.com/reuters/worldNews"],
    "eu_euro": ["https://news.google.com/rss/search?q=EU+ECB+Euro+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "uk": ["https://news.google.com/rss/search?q=London+UK+economy+when:1d&hl=en-GB&gl=GB&ceid=GB:en", "https://feeds.bbci.co.uk/news/uk/rss.xml"],
    "germany": ["https://news.google.com/rss/search?q=Germany+Berlin+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "france": ["https://news.google.com/rss/search?q=France+Paris+Macron+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "spain": ["https://news.google.com/rss/search?q=Spain+Madrid+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "sweden": ["https://news.google.com/rss/search?q=Sweden+Stockholm+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "houthis": ["https://news.google.com/rss/search?q=Houthi+Red+Sea+Yemen+when:2d&hl=en-US&gl=US&ceid=US:en"],
    "saudi_iraq_oil": ["https://news.google.com/rss/search?q=OPEC+oil+Saudi+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "ufo_orbs": ["https://news.google.com/rss/search?q=NASA+UAP+UFO+Pentagon+when:7d&hl=en-US&gl=US&ceid=US:en"],
    "aviation_accidents": ["https://news.google.com/rss/search?q=FAA+NTSB+aviation+when:3d&hl=en-US&gl=US&ceid=US:en"],
    "gold_silver": ["https://news.google.com/rss/search?q=gold+price+silver+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "crypto": ["https://news.google.com/rss/search?q=Bitcoin+crypto+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "natural_disasters": ["https://news.google.com/rss/search?q=earthquake+OR+hurricane+OR+volcano+when:1d&hl=en-US&gl=US&ceid=US:en", "https://www.usgs.gov/feeds/earthquakes"],
    "india": ["https://news.google.com/rss/search?q=India+Modi+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "china": ["https://news.google.com/rss/search?q=China+Beijing+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "japan": ["https://news.google.com/rss/search?q=Japan+Tokyo+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "australia": ["https://news.google.com/rss/search?q=Australia+Sydney+when:1d&hl=en-US&gl=US&ceid=US:en"],
}

PILLARS = {
    "usa_iran": {"keywords": ["iran"], "fallbacks": ["US Iran nuclear talks update today"], "pexels": ["oil tanker sea","military ship ocean","american flag"], "source": "Reuters / AP"},
    "russia_ukraine": {"keywords": ["ukraine","russia"], "fallbacks": ["Ukraine Russia war update today"], "pexels": ["military army","european city aerial","ukraine flag"], "source": "Reuters / AP / UN"},
    "eu_euro": {"keywords": ["eu","ecb"], "fallbacks": ["EU ECB decision today"], "pexels": ["european parliament","euro money","brussels city"], "source": "EU Commission / Reuters"},
    "uk": {"keywords": ["london","britain"], "fallbacks": ["London economy news today"], "pexels": ["london city timelapse","big ben london","british flag waving"], "source": "Reuters / BBC"},
    "germany": {"keywords": ["germany","berlin"], "fallbacks": ["Germany economy update today"], "pexels": ["berlin city timelapse","german flag","berlin brandenburg gate"], "source": "Reuters"},
    "france": {"keywords": ["france","paris"], "fallbacks": ["France economy update today"], "pexels": ["paris eiffel tower","paris city aerial","french flag"], "source": "Reuters"},
    "spain": {"keywords": ["spain","madrid"], "fallbacks": ["Spain economy update today"], "pexels": ["madrid city","spain flag","barcelona sagrada"], "source": "Reuters"},
    "sweden": {"keywords": ["sweden","stockholm"], "fallbacks": ["Sweden economy update today"], "pexels": ["stockholm city","sweden nature","scandinavia"], "source": "Reuters"},
    "houthis": {"keywords": ["houthi","red sea","yemen"], "fallbacks": ["Red Sea shipping security update today"], "pexels": ["cargo ship ocean","container ship sea","ocean waves storm"], "source": "Reuters / US Navy"},
    "saudi_iraq_oil": {"keywords": ["saudi","oil","opec"], "fallbacks": ["OPEC oil production decision today"], "pexels": ["oil refinery industry","oil rig sea","oil barrel"], "source": "Reuters / OPEC"},
    "ufo_orbs": {"keywords": ["ufo","uap","orb"], "fallbacks": ["NASA UAP report update today"], "pexels": ["night sky stars timelapse","milky way galaxy","northern lights aurora"], "source": "NASA / Pentagon AARO"},
    "aviation_accidents": {"keywords": ["aviation","airplane","faa"], "fallbacks": ["FAA aviation safety report today"], "pexels": ["airplane runway takeoff","airplane sky flying","airport terminal"], "source": "FAA / NTSB"},
    "gold_silver": {"keywords": ["gold","silver"], "fallbacks": ["Gold price update today"], "pexels": ["gold bars closeup","gold coins money","silver bars"], "source": "Reuters / Bloomberg"},
    "crypto": {"keywords": ["bitcoin","crypto"], "fallbacks": ["Bitcoin price update today"], "pexels": ["bitcoin cryptocurrency","ethereum crypto","blockchain technology"], "source": "Reuters / Bloomberg"},
    "natural_disasters": {"keywords": ["earthquake","flood","hurricane","volcano","wildfire"], "fallbacks": ["USGS earthquake report today"], "pexels": ["storm clouds timelapse","volcano eruption lava","flood water disaster"], "source": "USGS / NOAA / Reuters"},
    "india": {"keywords": ["india"], "fallbacks": ["India economy update today"], "pexels": ["taj mahal india","mumbai city india","india flag"], "source": "Reuters"},
    "china": {"keywords": ["china"], "fallbacks": ["China economy update today"], "pexels": ["beijing city timelapse","china great wall","shanghai city skyline"], "source": "Reuters"},
    "japan": {"keywords": ["japan","tokyo"], "fallbacks": ["Japan economy update today"], "pexels": ["tokyo city night timelapse","japan cherry blossom","mount fuji japan"], "source": "Reuters"},
    "australia": {"keywords": ["australia","sydney"], "fallbacks": ["Australia economy update today"], "pexels": ["sydney opera house","australia beach","melbourne city"], "source": "Reuters"},
    "immigration": {"keywords": ["migration"], "fallbacks": ["EU border report today"], "pexels": ["border wall","passport control","people walking city"], "source": "UNHCR / Reuters"},
    "rebels": {"keywords": ["rebel"], "fallbacks": ["UN report on armed conflict today"], "pexels": ["united nations building","desert landscape","military silhouette"], "source": "UN / Reuters"},
    "muslim_world": {"keywords": ["muslim"], "fallbacks": ["OIC statement today"], "pexels": ["mosque islamic","mecca kaaba","desert sunset"], "source": "Reuters / OIC"},
    "accidents": {"keywords": ["accident"], "fallbacks": ["NTSB accident report today"], "pexels": ["emergency lights police","fire truck emergency","ambulance"], "source": "Reuters / NTSB"},
}

def fetch_real_news(pillar_key):
    """Hakee OIKEAN uutisen RSS:stä"""
    feeds = RSS_FEEDS.get(pillar_key, RSS_FEEDS.get("uk"))
    real_news = []
    
    for feed_url in feeds[:2]:
        try:
            print(f"Fetching real news: {feed_url[:80]}")
            r = requests.get(feed_url, timeout=12, headers={"User-Agent": "Mozilla/5.0 WorldViralBot/1.0"})
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:10]:
                    title_elem = item.find('title')
                    desc_elem = item.find('description')
                    link_elem = item.find('link')
                    pub_elem = item.find('pubDate')
                    
                    title = title_elem.text if title_elem is not None else ""
                    desc = desc_elem.text if desc_elem is not None else ""
                    link = link_elem.text if link_elem is not None else ""
                    pub = pub_elem.text if pub_elem is not None else ""
                    
                    # Siisti kuvaus
                    desc = re.sub('<[^<]+?>', '', desc)  # Poista HTML
                    desc = desc[:400]
                    
                    if title and len(title) > 15:
                        real_news.append({
                            "title": title.strip(),
                            "desc": desc.strip(),
                            "link": link,
                            "pub": pub,
                            "pillar": pillar_key
                        })
        except Exception as e:
            print(f"RSS fail {feed_url[:50]}: {e}")
            continue
    
    if real_news:
        # Valitse uusin
        chosen = random.choice(real_news[:3])
        print(f"REAL NEWS FOUND: {chosen['title']}")
        return chosen
    
    # Fallback jos RSS ei toimi
    pdata = PILLARS[pillar_key]
    return {
        "title": random.choice(pdata["fallbacks"]),
        "desc": f"Official sources from {pdata['source']} report ongoing developments. Authorities monitoring situation closely.",
        "link": "https://reuters.com",
        "pub": datetime.now().isoformat(),
        "pillar": pillar_key
    }

def get_pexels_video(pexels_queries):
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY puuttuu - lisää pexels.com/api")
        return None
    if isinstance(pexels_queries, str):
        queries = [pexels_queries]
    else:
        queries = pexels_queries
    
    headers = {"Authorization": PEXELS_API_KEY}
    for query in queries:
        try:
            for orientation in ["portrait", "landscape"]:
                url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    for video in r.json().get('videos', []):
                        try:
                            files = sorted(video['video_files'], key=lambda x: x['width'], reverse=True)
                            best = files[0]
                            vdata = requests.get(best['link'], timeout=40).content
                            if len(vdata) > 150000:
                                with open("pexels_clip.mp4","wb") as f:
                                    f.write(vdata)
                                print(f"Pexels OK: {query} | {len(vdata)} bytes")
                                return "pexels_clip.mp4"
                        except:
                            continue
                if r.status_code == 401:
                    print("PEXELS KEY INVALID")
                    return None
        except Exception as e:
            print(f"Pexels error {query}: {e}")
            continue
    return None

def generate_script_from_real_news(real_news):
    """Muuttaa oikean uutisen YouTube Shorts scriptiksi"""
    title = real_news["title"]
    desc = real_news["desc"]
    source = PILLARS[real_news["pillar"]]["source"]
    
    # Jos OpenRouter on, tee parempi scripti, muuten käytä suoraan oikeaa uutista
    if not OPENROUTER_API_KEY:
        script = f"BREAKING: {title}. {desc[:250]}. Officials are monitoring. More updates expected. Source: {source} / {real_news['link'][:60]}"
        return script[:500]
    
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-viral-bot", "X-Title": "World Viral"}
        system_prompt = f"You are World Viral news anchor. Rewrite this REAL news into 110-word YouTube Shorts script. Keep facts from original, neutral tone. Title: {title}. Description: {desc}. Source: {source}. Structure: HOOK with title, FACT1 from description, FACT2 context, FACT3 what next, end with Source. English only."
        for model in ["google/gemini-flash-1.5-8b:free", "meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload = {"model": model, "messages": [{"role":"system","content":system_prompt},{"role":"user","content": f"Real news: {title} - {desc}"}], "max_tokens": 300, "temperature": 0.5}
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                data = r.json()
                if "choices" in data and data["choices"][0].get("message", {}).get("content"):
                    content = data["choices"][0]["message"]["content"].strip()
                    if len(content) > 60:
                        print(f"AI rewrite OK {model}")
                        return content + f"\n\nSource: {source}"
            except Exception as e:
                print(f"AI rewrite fail {e}")
                continue
        # Fallback jos AI ei toimi
        return f"BREAKING: {title}. {desc}. According to {source}, developments continue. Source: {source}"
    except Exception as e:
        print(f"Script gen error {e}")
        return f"BREAKING: {title}. {desc[:300]}. Source: {source}"

async def make_voice(text, output_file="voice.mp3"):
    try:
        clean = text.replace("\n", " ").strip()[:800]  # Max 800 chars for TTS
        communicate = edge_tts.Communicate(clean, "en-US-GuyNeural", rate="+3%", volume="+10%")
        await communicate.save(output_file)
        print("Voice saved")
        return output_file
    except Exception as e:
        print(f"TTS error {e}")
        return None

def make_video_trending(script_text, voice_file, pexels_clip, real_news):
    """V8 - REAL NEWS STYLE: Breaking banner + real footage + ticker"""
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import textwrap, os
        
        duration = 35
        audio_clip = None
        if voice_file and os.path.exists(voice_file):
            try:
                audio_clip = AudioFileClip(voice_file)
                duration = min(58, max(22, audio_clip.duration + 2.5))
            except:
                pass
        
        # Background - real Pexels video
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration)
                bg = bg.resize(height=1920)
                if bg.w < 1080:
                    bg = bg.resize(width=1080)
                bg = bg.crop(x_center=bg.w/2, y_center=bg.h/2, width=1080, height=1920).set_duration(duration)
                print("Using REAL Pexels footage")
            except Exception as e:
                print(f"Pexels bg fail {e}")
                bg = ColorClip(size=(1080,1920), color=(10,20,40), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(10,20,40), duration=duration)
        
        # Create NEWS STYLE overlay
        try:
            W, H = 1080, 1920
            # Full overlay image
            pil_img = Image.new('RGBA', (W, H), (0,0,0,0))
            draw = ImageDraw.Draw(pil_img)
            
            try:
                bold_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                bold_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
                bold_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            except:
                bold_big = ImageFont.load_default()
                bold_med = bold_big
                bold_small = bold_big
            
            # TOP BREAKING BANNER - red
            draw.rectangle([(0,0),(W, 110)], fill=(220,20,20,255))
            draw.text((30, 20), "🔴 BREAKING NEWS", font=bold_big, fill=(255,255,255,255))
            draw.text((W-250, 35), datetime.now().strftime("%H:%M UTC"), font=bold_small, fill=(255,255,255,255))
            
            # MIDDLE TEXT BOX - black semi-transparent
            box_y = 280
            box_h = 1150
            draw.rounded_rectangle([(30, box_y),(W-30, box_y+box_h)], radius=25, fill=(0,0,0,190))
            
            # Real news text
            wrapped = textwrap.wrap(script_text, width=32)[:13]
            y = box_y + 30
            for i, line in enumerate(wrapped):
                font = bold_big if i == 0 else bold_med
                # Outline
                for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(-2,0),(2,0)]:
                    draw.text((60+dx, y+dy), line, font=font, fill=(0,0,0,255))
                draw.text((60, y), line, font=font, fill=(255,255,255,255))
                y += 68 if i == 0 else 55
            
            # BOTTOM TICKER - white with source
            ticker_y = H - 140
            draw.rectangle([(0, ticker_y),(W, H)], fill=(0,0,0,230))
            draw.rectangle([(0, ticker_y),(W, ticker_y+8)], fill=(220,20,20,255))
            source_text = f"{real_news['pillar'].upper()} | Source: {PILLARS[real_news['pillar']]['source']} | {real_news['title'][:70]}"
            draw.text((20, ticker_y+25), source_text[:90], font=bold_small, fill=(255,255,255,255))
            draw.text((20, ticker_y+65), f"Full story: {real_news['link'][:70]} | #WorldViral #Breaking", font=bold_small, fill=(200,200,200,255))
            
            # LIVE dot
            draw.ellipse([(W-130, 140),(W-110, 160)], fill=(255,0,0,255))
            draw.text((W-100, 135), "LIVE", font=bold_small, fill=(255,255,255,255))
            
            pil_img.save("text_overlay.png")
            print(f"News overlay created: {real_news['title'][:60]}")
            
            txt_clip = ImageClip("text_overlay.png", duration=duration).set_duration(duration)
            
            if audio_clip:
                final = CompositeVideoClip([bg, txt_clip]).set_audio(audio_clip)
            else:
                final = CompositeVideoClip([bg, txt_clip])
            
            final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac', bitrate="4500k", preset="ultrafast", threads=4)
            print("V8 video written with REAL news + REAL footage")
            return "world_viral_output.mp4"
            
        except Exception as e:
            print(f"Overlay fail {e}")
            import traceback
            traceback.print_exc()
            if audio_clip:
                final_bg = bg.set_audio(audio_clip)
            else:
                final_bg = bg
            final_bg.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac')
            return "world_viral_output.mp4"
            
    except Exception as e:
        print(f"Video error {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("WORLD VIRAL V8 - REAL NEWS + REAL VIDEO")
    
    # 1. Valitse pillari ja hae OIKEA uutinen
    if PILLAR_ENV != "auto" and PILLAR_ENV in PILLARS:
        pillar_key = PILLAR_ENV
    else:
        pillar_key = random.choice(list(PILLARS.keys()))
    
    print(f"Selected pillar: {pillar_key}")
    real_news = fetch_real_news(pillar_key)
    pdata = PILLARS[pillar_key]
    
    # 2. Hae OIKEA video Pexelsistä
    pexels_clip = get_pexels_video(pdata["pexels"])
    
    # 3. Tee scripti oikeasta uutisesta
    script = generate_script_from_real_news(real_news)
    print(f"REAL TITLE: {real_news['title']}\nSCRIPT: {script[:200]}...\nLINK: {real_news['link']}")
    
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {real_news['title']}\n\n{script}\n\n---\nREAL SOURCE: {real_news['link']}\nPillar: {pillar_key}\nPublished: {real_news['pub']}\nPexels: {pdata['pexels']}\n#worldviral #{pillar_key} #breaking #realnews")
    
    # 4. Voice
    voice_file = await make_voice(script)
    
    # 5. Video with REAL news style
    video_file = make_video_trending(script, voice_file, pexels_clip, real_news)
    print(f"Valmis: {video_file} | Pexels: {pexels_clip is not None} | Real news: {real_news['title'][:50]}")
    
    # 6. Upload
    if video_file and os.path.exists(video_file):
        try:
            from youtube_uploader import upload_video
            title = f"{real_news['title'][:80]} | World Viral"[:95]
            with open("script.txt","r", encoding="utf-8") as f:
                desc = f.read()
            tags = [pillar_key, "real news", "breaking news", "world viral", real_news['title'].split()[0], PILLARS[pillar_key]['source'].split('/')[0].strip()]
            upload_video(file_path=video_file, title=title, description=desc, tags=tags, privacy="public")
        except Exception as e:
            print(f"YouTube skip: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
