
"""
WORLD VIRAL - MEGA MULTI PILLAR V5 FIX
Fixes: ImageMagick, googleapiclient, AI choices error
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PILLAR_ENV = os.getenv("PILLAR", "auto")

PILLARS = {
    "usa_iran": {"keywords": ["iran","usa","tehran","pentagon","hormuz","nuclear"], "fallbacks": ["US Iran nuclear talks update today","Strait of Hormuz oil traffic today","Pentagon statement on Iran today","IAEA Iran report today","White House Iran statement today"], "pexels_map": {"default":"world map"}, "source": "Reuters / AP / Pentagon / IAEA"},
    "russia_ukraine": {"keywords": ["ukraine","russia","kyiv","moscow","zelensky","putin"], "fallbacks": ["Ukraine Russia peace talks update today","EU statement on Ukraine aid today","NATO statement Ukraine today","UN report Ukraine today","Russia Ukraine grain deal today"], "pexels_map": {"default":"ukraine flag"}, "source": "Reuters / AP / UN"},
    "eu_euro": {"keywords": ["eu","european","eurozone","ecb","brussels"], "fallbacks": ["EU new law proposal today","ECB interest rate decision today","EU Commission economy statement today","Eurozone inflation data today","EU parliament vote today"], "pexels_map": {"default":"european union flag"}, "source": "EU Commission / ECB / Reuters"},
    "immigration": {"keywords": ["migration","migrant","border","asylum"], "fallbacks": ["EU Frontex border report today","UNHCR migration data today","EU asylum policy update today","Germany migration statistics today","Mediterranean rescue update today"], "pexels_map": {"default":"border fence"}, "source": "UNHCR / Frontex / Reuters", "safe_prompt": "Use ONLY official statistics. No hate."},
    "germany": {"keywords": ["germany","berlin"], "fallbacks": ["Germany economy update today","German government statement today","Germany energy policy today"], "pexels_map": {"default":"berlin city"}, "source": "Reuters / German Government"},
    "spain": {"keywords": ["spain","madrid"], "fallbacks": ["Spain economy update today","Spanish government statement today"], "pexels_map": {"default":"madrid city"}, "source": "Reuters"},
    "uk": {"keywords": ["uk ","britain","london","england"], "fallbacks": ["UK government statement today","Bank of England update today","London economy news today"], "pexels_map": {"default":"london city"}, "source": "Reuters / UK Government"},
    "sweden": {"keywords": ["sweden","stockholm"], "fallbacks": ["Sweden economy update today","Swedish government statement today"], "pexels_map": {"default":"stockholm city"}, "source": "Reuters"},
    "france": {"keywords": ["france","paris","macron"], "fallbacks": ["France government statement today","France economy update today"], "pexels_map": {"default":"paris city"}, "source": "Reuters"},
    "houthis": {"keywords": ["houthi","yemen","red sea"], "fallbacks": ["Red Sea shipping security update today","UN statement Yemen today","US Navy Red Sea operation today"], "pexels_map": {"default":"cargo ship sea"}, "source": "Reuters / US Navy / UN"},
    "saudi_iraq_oil": {"keywords": ["saudi","iraq","oil","opec"], "fallbacks": ["OPEC oil production decision today","Saudi Arabia economy today","Oil price update today","OPEC+ meeting today"], "pexels_map": {"default":"oil rig"}, "source": "Reuters / OPEC / EIA"},
    "rebels": {"keywords": ["rebel","insurgent"], "fallbacks": ["UN report on armed conflict today","Security Council briefing today"], "pexels_map": {"default":"un building"}, "source": "UN / Reuters", "safe_prompt": "Neutral UN only."},
    "muslim_world": {"keywords": ["muslim","oic"], "fallbacks": ["OIC statement today","Saudi Arabia Hajj update today"], "pexels_map": {"default":"mosque"}, "source": "Reuters / OIC / UN", "safe_prompt": "Cultural factual only."},
    "ufo_orbs": {"keywords": ["ufo","uap","orb","unidentified"], "fallbacks": ["NASA UAP report update today","Pentagon UAP office statement today","US Congress UFO hearing update today","NASA orb sighting analysis today"], "pexels_map": {"default":"night sky"}, "source": "NASA / Pentagon AARO / Reuters", "safe_prompt": "Official NASA/Pentagon only. No conspiracy."},
    "aviation_accidents": {"keywords": ["plane crash","aviation","airplane","flight accident"], "fallbacks": ["FAA aviation safety report today","NTSB investigation update today","EASA safety bulletin today","Aviation accident preliminary report today"], "pexels_map": {"default":"airplane runway"}, "source": "FAA / NTSB / EASA / Reuters", "safe_prompt": "Official preliminary only. Respectful."},
    "gold_silver": {"keywords": ["gold","silver"], "fallbacks": ["Gold price update today","Silver price market update today","Federal Reserve gold reserves report today","Central banks gold buying report today"], "pexels_map": {"default":"gold bars"}, "source": "Reuters / Bloomberg / Fed", "safe_prompt": "Market data only."},
    "crypto": {"keywords": ["bitcoin","crypto","ethereum"], "fallbacks": ["Bitcoin price update today","Ethereum market update today","SEC crypto regulation update today","Crypto market analysis today"], "pexels_map": {"default":"bitcoin"}, "source": "Reuters / SEC / Bloomberg", "safe_prompt": "Market data only."},
    "natural_disasters": {"keywords": ["earthquake","flood","hurricane","tornado","volcano","tsunami","wildfire","storm","landslide","cyclone"], "fallbacks": ["USGS earthquake report today","NOAA storm warning today","Flood warning update today","Volcano activity report today","Hurricane tracking update today","Wildfire situation report today","Tsunami warning center update today","Extreme weather alert today"], "pexels_map": {"default":"storm clouds"}, "source": "USGS / NOAA / NASA / Reuters", "safe_prompt": "Official USGS/NOAA only."},
    "accidents": {"keywords": ["accident","crash","derailment"], "fallbacks": ["Traffic accident report official today","Industrial safety report today","NTSB accident report today"], "pexels_map": {"default":"emergency lights"}, "source": "Reuters / NTSB", "safe_prompt": "No graphic."},
    "india": {"keywords": ["india","delhi","modi"], "fallbacks": ["India economy update today","Indian government statement today","India tech sector news today"], "pexels_map": {"default":"taj mahal india"}, "source": "Reuters / Indian Government"},
    "china": {"keywords": ["china","beijing","xi jinping"], "fallbacks": ["China economy update today","Chinese government statement today","China tech market update today"], "pexels_map": {"default":"beijing city"}, "source": "Reuters"},
    "japan": {"keywords": ["japan","tokyo"], "fallbacks": ["Japan economy update today","Japanese government statement today","Bank of Japan decision today"], "pexels_map": {"default":"tokyo city"}, "source": "Reuters / Japanese Government"},
    "australia": {"keywords": ["australia","sydney"], "fallbacks": ["Australia economy update today","Australian government statement today","RBA interest rate decision today"], "pexels_map": {"default":"sydney opera house"}, "source": "Reuters / Australian Government"},
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
    prompt = f"Topic: {topic}. Pillar: {pillar_key}. Neutral news based ONLY on official sources: {base_source}. {safe_extra} What was officially confirmed today, context, next steps. No speculation, no hate, no graphic."
    tl = topic.lower()
    pexels_kw = pdata["pexels_map"]["default"]
    for k,v in pdata["pexels_map"].items():
        if k != "default" and k in tl:
            pexels_kw = v
            break
    return prompt, pillar_key, pexels_kw, base_source

def get_pexels_video(query):
    if not PEXELS_API_KEY:
        return None
    try:
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and r.json().get('videos'):
            video = r.json()['videos'][0]
            best = video['video_files'][0]
            for vf in video['video_files']:
                if vf['width'] == 1080 and vf['height'] == 1920:
                    best = vf
                    break
            data = requests.get(best['link'], timeout=30).content
            with open("pexels_clip.mp4","wb") as f:
                f.write(data)
            return "pexels_clip.mp4"
        return None
    except Exception as e:
        print(f"Pexels error {e}")
        return None

def generate_script(official_prompt, trending_topic, pillar_key, source_line):
    # Fallback script always works
    fallback = f"Today: {trending_topic}. According to {source_line}, officials report ongoing developments. Monitoring continues. Experts are analyzing the situation. Official updates expected soon. Source: {source_line}."
    if not OPENROUTER_API_KEY:
        print("No OPENROUTER key, using fallback")
        return fallback
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-viral-bot", "X-Title": "World Viral Bot"}
        system_prompt = f"You are World Viral neutral news. Pillar {pillar_key}. 110 words max. Neutral factual. Official sources {source_line} only. No graphic, no hate, no conspiracy. English. Structure: Hook, Fact1, Fact2, Fact3, Source. End with Source: {source_line}"
        # Try multiple models
        for model in ["google/gemini-flash-1.5-8b:free", "google/gemini-flash-1.5:free", "meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload = {"model": model, "messages": [{"role":"system","content":system_prompt},{"role":"user","content":official_prompt}], "max_tokens": 300}
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        print(f"AI success with {model}")
                        return content
                print(f"Model {model} failed: {data}")
            except Exception as e:
                print(f"Model {model} error {e}")
                continue
        print("All AI models failed, using fallback")
        return fallback
    except Exception as e:
        print(f"AI error {e}")
        return fallback

async def make_voice(text, output_file="voice.mp3"):
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print(f"TTS error {e}")
        return None

def make_video_trending(script_text, voice_file, pexels_clip=None):
    # FIXED: Ei käytä ImageMagickia enää, käyttää PIL-only menetelmää
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import textwrap, os
        duration = 35
        
        # Background
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration).resize((1080,1920))
            except:
                bg = ColorClip(size=(1080,1920), color=(12,18,30), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(12,18,30), duration=duration)
        
        # Create text image with PIL (no ImageMagick needed)
        try:
            wrapped = textwrap.fill(script_text, width=36)
            # Create image with text
            img_w, img_h = 900, 1300
            pil_img = Image.new('RGBA', (img_w, img_h), (0,0,0,0))
            draw = ImageDraw.Draw(pil_img)
            # Try to use a font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
            except:
                font = ImageFont.load_default()
            
            # Draw text with stroke
            y = 20
            for line in wrapped.split('\n'):
                # Stroke
                for dx in [-2,0,2]:
                    for dy in [-2,0,2]:
                        draw.text((20+dx, y+dy), line, font=font, fill=(0,0,0,255))
                draw.text((20, y), line, font=font, fill=(255,255,255,255))
                y += 50
                if y > img_h - 50:
                    break
            
            pil_img.save("text_overlay.png")
            txt_clip = ImageClip("text_overlay.png", duration=duration).set_position('center')
            
            audio = AudioFileClip(voice_file) if voice_file and os.path.exists(voice_file) else None
            if audio:
                duration = min(duration, audio.duration + 1.5)
                bg = bg.set_duration(duration)
                txt_clip = txt_clip.set_duration(duration)
                final = CompositeVideoClip([bg, txt_clip]).set_audio(audio)
            else:
                final = CompositeVideoClip([bg, txt_clip])
            
            final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac')
            return "world_viral_output.mp4"
        except Exception as e:
            print(f"PIL Text failed {e}, using bg only")
            if voice_file and os.path.exists(voice_file):
                audio = AudioFileClip(voice_file)
                bg = bg.set_duration(min(duration, audio.duration + 1)).set_audio(audio)
            bg.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac')
            return "world_viral_output.mp4"
            
    except Exception as e:
        print(f"Video error {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("WORLD VIRAL MEGA V5 FIX")
    trending_topic, pillar_key = get_trending_topic_multi()
    official_prompt, pillar, pexels_kw, source_line = get_official_prompt(trending_topic, pillar_key)
    print(f"Pillar: {pillar} | Topic: {trending_topic} | Pexels: {pexels_kw}")
    pexels_clip = get_pexels_video(pexels_kw)
    script = generate_script(official_prompt, trending_topic, pillar, source_line)
    print(f"Script:\n{script}")
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {trending_topic} | World Viral {pillar}\n\n{script}\n\n---\nPillar: {pillar}\nSource: {source_line}\n#worldviral #{pillar} #breaking #news")
    voice_file = await make_voice(script)
    video_file = make_video_trending(script, voice_file, pexels_clip)
    print(f"Valmis: {video_file}")
    if video_file and os.path.exists(video_file):
        try:
            from youtube_uploader import upload_video
            title = f"{trending_topic} - {pillar.replace('_',' ').title()} Update | World Viral"[:95]
            with open("script.txt","r", encoding="utf-8") as f:
                desc = f.read()
            upload_video(file_path=video_file, title=title, description=desc, tags=[pillar, trending_topic, "world viral", "breaking"], privacy="public")
        except Exception as e:
            print(f"YouTube skip: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
