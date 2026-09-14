
"""
WORLD VIRAL - MEGA MULTI PILLAR V7 - PEXELS FIX
Pexels nyt 100% toiminnassa - laaja haku + varavideot
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"PEXELS KEY: {'SET' if PEXELS_API_KEY else 'NOT SET - using gradient'}")

# PEXELS - VARMA HAKU - jokaiselle pilarille 3 hakusanaa jotka varmasti löytyy
PILLARS = {
    "usa_iran": {"keywords": ["iran","usa","tehran","pentagon","hormuz","nuclear"], "fallbacks": ["US Iran nuclear talks update today","Strait of Hormuz oil traffic today","Pentagon statement on Iran today"], "pexels": ["oil tanker sea","military ship ocean","american flag waving"], "source": "Reuters / AP / Pentagon / IAEA"},
    "russia_ukraine": {"keywords": ["ukraine","russia","kyiv","moscow","zelensky","putin"], "fallbacks": ["Ukraine Russia peace talks update today","EU statement on Ukraine aid today","NATO statement Ukraine today"], "pexels": ["military army","european city aerial","war memorial"], "source": "Reuters / AP / UN"},
    "eu_euro": {"keywords": ["eu","european","eurozone","ecb","brussels"], "fallbacks": ["EU new law proposal today","ECB interest rate decision today","Eurozone inflation data today"], "pexels": ["european parliament","euro money","brussels city"], "source": "EU Commission / ECB / Reuters"},
    "immigration": {"keywords": ["migration","migrant","border","asylum"], "fallbacks": ["EU Frontex border report today","UNHCR migration data today","EU asylum policy update today"], "pexels": ["border wall","passport control","people walking city"], "source": "UNHCR / Frontex / Reuters"},
    "germany": {"keywords": ["germany","berlin"], "fallbacks": ["Germany economy update today","German government statement today"], "pexels": ["berlin city timelapse","german flag","europe city"], "source": "Reuters"},
    "spain": {"keywords": ["spain","madrid"], "fallbacks": ["Spain economy update today","Spanish government statement today"], "pexels": ["madrid city","spain flag","barcelona city"], "source": "Reuters"},
    "uk": {"keywords": ["uk ","britain","london","england"], "fallbacks": ["UK government statement today","Bank of England update today","London economy news today"], "pexels": ["london city timelapse","big ben london","british flag"], "source": "Reuters / UK Government"},
    "sweden": {"keywords": ["sweden","stockholm"], "fallbacks": ["Sweden economy update today","Swedish government statement today"], "pexels": ["stockholm city","sweden nature","scandinavia city"], "source": "Reuters"},
    "france": {"keywords": ["france","paris","macron"], "fallbacks": ["France government statement today","France economy update today"], "pexels": ["paris eiffel tower","france city","french flag"], "source": "Reuters"},
    "houthis": {"keywords": ["houthi","yemen","red sea"], "fallbacks": ["Red Sea shipping security update today","UN statement Yemen today"], "pexels": ["cargo ship ocean","container ship sea","ocean waves"], "source": "Reuters / US Navy / UN"},
    "saudi_iraq_oil": {"keywords": ["saudi","iraq","oil","opec"], "fallbacks": ["OPEC oil production decision today","Oil price update today","Saudi Arabia economy today"], "pexels": ["oil refinery industry","oil rig sea","oil barrel"], "source": "Reuters / OPEC / EIA"},
    "rebels": {"keywords": ["rebel","insurgent"], "fallbacks": ["UN report on armed conflict today","Security Council briefing today"], "pexels": ["united nations building","military silhouette","desert landscape"], "source": "UN / Reuters"},
    "muslim_world": {"keywords": ["muslim","oic"], "fallbacks": ["OIC statement today","Saudi Arabia Hajj update today"], "pexels": ["mosque islamic","mecca kaaba","desert sunset"], "source": "Reuters / OIC / UN"},
    "ufo_orbs": {"keywords": ["ufo","uap","orb","unidentified"], "fallbacks": ["NASA UAP report update today","Pentagon UAP office statement today","US Congress UFO hearing update today"], "pexels": ["night sky stars timelapse","milky way night","northern lights aurora"], "source": "NASA / Pentagon AARO / Reuters"},
    "aviation_accidents": {"keywords": ["plane crash","aviation","airplane","flight accident"], "fallbacks": ["FAA aviation safety report today","NTSB investigation update today","EASA safety bulletin today"], "pexels": ["airplane runway takeoff","airplane sky flying","airport terminal"], "source": "FAA / NTSB / EASA / Reuters"},
    "gold_silver": {"keywords": ["gold","silver"], "fallbacks": ["Gold price update today","Silver price market update today","Federal Reserve gold reserves report today"], "pexels": ["gold bars closeup","gold coins money","silver bars"], "source": "Reuters / Bloomberg / Fed"},
    "crypto": {"keywords": ["bitcoin","crypto","ethereum"], "fallbacks": ["Bitcoin price update today","Ethereum market update today","SEC crypto regulation update today"], "pexels": ["bitcoin cryptocurrency","ethereum crypto","blockchain technology"], "source": "Reuters / SEC / Bloomberg"},
    "natural_disasters": {"keywords": ["earthquake","flood","hurricane","tornado","volcano","tsunami","wildfire","storm","landslide","cyclone"], "fallbacks": ["USGS earthquake report today","NOAA storm warning today","Flood warning update today","Volcano activity report today","Hurricane tracking update today","Wildfire situation report today"], "pexels": ["storm clouds timelapse","earthquake damage","volcano eruption lava"], "source": "USGS / NOAA / NASA / Reuters"},
    "accidents": {"keywords": ["accident","crash","derailment"], "fallbacks": ["Traffic accident report official today","NTSB accident report today"], "pexels": ["emergency lights police","fire truck emergency","ambulance emergency"], "source": "Reuters / NTSB"},
    "india": {"keywords": ["india","delhi","modi"], "fallbacks": ["India economy update today","Indian government statement today"], "pexels": ["taj mahal india","mumbai city india","india flag"], "source": "Reuters"},
    "china": {"keywords": ["china","beijing","xi jinping"], "fallbacks": ["China economy update today","Chinese government statement today"], "pexels": ["beijing city timelapse","china great wall","shanghai city skyline"], "source": "Reuters"},
    "japan": {"keywords": ["japan","tokyo"], "fallbacks": ["Japan economy update today","Japanese government statement today"], "pexels": ["tokyo city night timelapse","japan cherry blossom","mount fuji japan"], "source": "Reuters"},
    "australia": {"keywords": ["australia","sydney"], "fallbacks": ["Australia economy update today","Australian government statement today"], "pexels": ["sydney opera house","australia beach","melbourne city"], "source": "Reuters"},
}

def get_trending_topic_multi():
    trending = []
    try:
        url = "https://trends.google.com/trending/rss?geo=US"
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:30]:
                t = item.find('title').text if item.find('title') is not None else ""
                trending.append(t)
    except:
        pass
    if PILLAR_ENV != "auto" and PILLAR_ENV in PILLARS:
        chosen_pillar = PILLAR_ENV
    else:
        chosen_pillar = random.choice(list(PILLARS.keys()))
    pdata = PILLARS[chosen_pillar]
    for title in trending:
        tl = title.lower()
        if any(k in tl for k in pdata["keywords"]):
            return title, chosen_pillar
    return random.choice(pdata["fallbacks"]), chosen_pillar

def get_official_prompt(topic, pillar_key):
    pdata = PILLARS[pillar_key]
    base_source = pdata["source"]
    safe_extra = pdata.get("safe_prompt", "")
    prompt = f"Topic: {topic}. Pillar: {pillar_key}. Neutral news based ONLY on official sources: {base_source}. {safe_extra} What was officially confirmed today, context, next steps. No speculation."
    return prompt, pillar_key, pdata["pexels"][0], base_source

def get_pexels_video(pexels_queries):
    """
    PEXELS V7 - Kokeilee 3 eri hakua, ottaa ensimmäisen joka toimii, myös landscape ja crop
    """
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY puuttuu - mene pexels.com/api hae ilmainen key ja lisää GitHub Secrets")
        return None
    
    # pexels_queries voi olla lista tai string
    if isinstance(pexels_queries, str):
        queries = [pexels_queries, "city timelapse", "news background"]
    else:
        queries = pexels_queries
    
    headers = {"Authorization": PEXELS_API_KEY}
    
    for query in queries:
        try:
            print(f"Pexels haku: {query}")
            # Ensin portrait, sitten landscape jos ei löydy
            for orientation in ["portrait", "landscape"]:
                url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
                r = requests.get(url, headers=headers, timeout=15)
                print(f"  -> status {r.status_code} orientation {orientation}")
                if r.status_code == 200:
                    data = r.json()
                    videos = data.get('videos', [])
                    print(f"  -> löytyi {len(videos)} videota")
                    for video in videos:
                        try:
                            # Ota paras laatu
                            files = sorted(video['video_files'], key=lambda x: x['width'], reverse=True)
                            best = files[0]
                            # Lataa
                            vdata = requests.get(best['link'], timeout=40).content
                            if len(vdata) > 150000:  # Vähintään 150KB
                                with open("pexels_clip.mp4","wb") as f:
                                    f.write(vdata)
                                print(f"  Pexels video ladattu: {query} | {len(vdata)} bytes | {best['width']}x{best['height']}")
                                return "pexels_clip.mp4"
                        except Exception as e:
                            print(f"    video fail {e}")
                            continue
                if r.status_code == 401:
                    print("PEXELS KEY VIRHEELLINEN - tarkista key!")
                    return None
        except Exception as e:
            print(f"Pexels haku virhe {query}: {e}")
            continue
    
    print("Pexels ei löytänyt videoita, käytetään gradienttia")
    return None

def generate_script(official_prompt, trending_topic, pillar_key, source_line):
    fallback = f"BREAKING: {trending_topic}. According to {source_line}, officials confirm new developments today. First, official sources report ongoing monitoring. Second, the situation remains under close observation. Third, further updates expected within hours. Source: {source_line}."
    if not OPENROUTER_API_KEY:
        return fallback
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-viral-bot", "X-Title": "World Viral Bot"}
        system_prompt = f"You are World Viral neutral news anchor. Pillar {pillar_key}. Write EXACTLY 120 words. Hook first sentence. 3 facts from official sources {source_line} only. No hate, no graphic, no conspiracy. English. End with Source: {source_line}"
        for model in ["google/gemini-flash-1.5-8b:free", "google/gemini-flash-1.5:free", "meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload = {"model": model, "messages": [{"role":"system","content":system_prompt},{"role":"user","content":official_prompt}], "max_tokens": 350, "temperature": 0.7}
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0 and data["choices"][0].get("message", {}).get("content"):
                    content = data["choices"][0]["message"]["content"].strip()
                    if len(content) > 50:
                        print(f"AI success {model}")
                        return content
            except Exception as e:
                print(f"Model {model} error {e}")
                continue
        return fallback
    except Exception as e:
        print(f"AI error {e}")
        return fallback

async def make_voice(text, output_file="voice.mp3"):
    try:
        clean = text.replace("\n", " ").strip()
        communicate = edge_tts.Communicate(clean, "en-US-GuyNeural", rate="+5%", volume="+10%")
        await communicate.save(output_file)
        print(f"Voice saved")
        return output_file
    except Exception as e:
        print(f"TTS error {e}")
        return None

def make_video_trending(script_text, voice_file, pexels_clip=None):
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import textwrap, os
        
        duration = 35
        audio_clip = None
        if voice_file and os.path.exists(voice_file):
            try:
                audio_clip = AudioFileClip(voice_file)
                duration = min(60, max(22, audio_clip.duration + 2.0))
            except:
                pass
        
        # Background
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration)
                bg = bg.resize(height=1920)
                if bg.w < 1080:
                    bg = bg.resize(width=1080)
                bg = bg.crop(x_center=bg.w/2, y_center=bg.h/2, width=1080, height=1920)
                bg = bg.set_duration(duration)
                # Tummenna taustaa että teksti näkyy
                bg = bg.fx(lambda gf, t: gf(t) * 0.6) if hasattr(bg, 'fx') else bg
                print("Using Pexels background with dark overlay")
            except Exception as e:
                print(f"Pexels bg failed {e}")
                bg = ColorClip(size=(1080,1920), color=(15,25,45), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(15,25,45), duration=duration)
        
        # Text overlay - PROFESSIONAL
        try:
            wrapped_lines = textwrap.wrap(script_text, width=30)[:14]
            W, H = 1000, 1450
            pil_img = Image.new('RGBA', (W, H), (0,0,0,0))
            draw = ImageDraw.Draw(pil_img)
            draw.rounded_rectangle([(0,0),(W,H)], radius=30, fill=(0,0,0,185))
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
                body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            except:
                title_font = ImageFont.load_default()
                body_font = title_font
            y = 35
            for i, line in enumerate(wrapped_lines):
                font = title_font if i == 0 else body_font
                for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(-3,0),(3,0),(0,-3),(0,3)]:
                    draw.text((35+dx, y+dy), line, font=font, fill=(0,0,0,255))
                draw.text((35, y), line, font=font, fill=(255,255,255,255))
                y += 62 if i == 0 else 58
                if y > H - 70:
                    break
            draw.rounded_rectangle([(0, H-70),(W, H)], radius=20, fill=(220,20,20,220))
            draw.text((35, H-55), f"Source: Reuters / Official", font=body_font, fill=(255,255,255,255))
            pil_img.save("text_overlay.png")
            txt_clip = ImageClip("text_overlay.png", duration=duration).set_position(('center', 180)).set_duration(duration)
            if audio_clip:
                final = CompositeVideoClip([bg, txt_clip]).set_audio(audio_clip)
            else:
                final = CompositeVideoClip([bg, txt_clip])
            final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac', bitrate="4000k", preset="ultrafast", threads=4)
            return "world_viral_output.mp4"
        except Exception as e:
            print(f"PIL fail {e}")
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
    print("WORLD VIRAL MEGA V7 PEXELS FIX")
    trending_topic, pillar_key = get_trending_topic_multi()
    pdata = PILLARS[pillar_key]
    official_prompt, pillar, pexels_query, source_line = get_official_prompt(trending_topic, pillar_key)
    print(f"Pillar: {pillar} | Topic: {trending_topic} | Pexels queries: {pdata['pexels']}")
    pexels_clip = get_pexels_video(pdata['pexels'])
    script = generate_script(official_prompt, trending_topic, pillar, source_line)
    print(f"Script: {script[:150]}...\n")
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {trending_topic} | World Viral {pillar}\n\n{script}\n\n---\nPillar: {pillar}\nSource: {source_line}\n#worldviral #{pillar} #breaking")
    voice_file = await make_voice(script)
    video_file = make_video_trending(script, voice_file, pexels_clip)
    print(f"Valmis: {video_file} | Pexels used: {pexels_clip is not None}")
    if video_file and os.path.exists(video_file):
        try:
            from youtube_uploader import upload_video
            title = f"{trending_topic} - {pillar.replace('_',' ').title()} Update | World Viral"[:95]
            with open("script.txt","r", encoding="utf-8") as f:
                desc = f.read()
            tags = [pillar, trending_topic, "world viral", "breaking news", "trending"]
            upload_video(file_path=video_file, title=title, description=desc, tags=tags, privacy="public")
        except Exception as e:
            print(f"YouTube skip: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
