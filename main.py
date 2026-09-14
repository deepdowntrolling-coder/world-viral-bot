
"""
WORLD VIRAL - MEGA MULTI PILLAR V4
Kaikki pilarit: USA-Iran, EU, Euro, Maahanmuutto, Venäjä-Ukraina, Saksa, Espanja, Englanti, Ruotsi, Ranska, Houthit, Saudi, Irak, Öljy, Kapinalliset
UUDET: UFO/Orbs, Lento-onnettomuudet, Kulta/Hopea, Krypto, Luonnonmullistukset, Onnettomuudet, Intia, Kiina, Japani, Australia
100% neutraali, virallisiin lähteisiin perustuva
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PILLAR_ENV = os.getenv("PILLAR", "auto")

PILLARS = {
    "usa_iran": {
        "keywords": ["iran","usa","tehran","pentagon","strait of hormuz","nuclear","hormuz"],
        "fallbacks": ["US Iran nuclear talks update today","Strait of Hormuz oil traffic today","Pentagon statement on Iran today","IAEA Iran report today","White House Iran statement today"],
        "pexels_map": {"nuclear":"nuclear plant","hormuz":"oil tanker","pentagon":"military","default":"world map"},
        "source": "Reuters / AP / Pentagon / IAEA"
    },
    "russia_ukraine": {
        "keywords": ["ukraine","russia","kyiv","moscow","zelensky","putin"],
        "fallbacks": ["Ukraine Russia peace talks update today","EU statement on Ukraine aid today","NATO statement Ukraine today","UN report Ukraine humanitarian today","Russia Ukraine grain deal today"],
        "pexels_map": {"default":"ukraine flag"},
        "source": "Reuters / AP / UN / EU Commission"
    },
    "eu_euro": {
        "keywords": ["eu","european","eurozone","ecb","brussels"],
        "fallbacks": ["EU new law proposal today","ECB interest rate decision today","EU Commission economy statement today","Eurozone inflation data today","EU parliament vote today"],
        "pexels_map": {"default":"european union flag"},
        "source": "EU Commission / ECB / Reuters"
    },
    "immigration": {
        "keywords": ["migration","migrant","border","asylum"],
        "fallbacks": ["EU Frontex border report today","UNHCR migration data today","EU asylum policy update today","Germany migration statistics today","Mediterranean rescue update today"],
        "pexels_map": {"default":"border fence"},
        "source": "UNHCR / Frontex / Reuters - official statistics only",
        "safe_prompt": "Use ONLY official statistics from UNHCR, Frontex, EU. No hate, neutral factual."
    },
    "germany": {
        "keywords": ["germany","berlin","scholz"],
        "fallbacks": ["Germany economy update today","German government statement today","Germany energy policy today","Berlin EU policy today"],
        "pexels_map": {"default":"berlin city"},
        "source": "Reuters / German Government"
    },
    "spain": {
        "keywords": ["spain","madrid","sanchez"],
        "fallbacks": ["Spain economy update today","Spanish government statement today","Spain EU policy today"],
        "pexels_map": {"default":"madrid city"},
        "source": "Reuters / Spanish Government"
    },
    "uk": {
        "keywords": ["uk ","britain","london","england"],
        "fallbacks": ["UK government statement today","Bank of England update today","London economy news today"],
        "pexels_map": {"default":"london city"},
        "source": "Reuters / UK Government"
    },
    "sweden": {
        "keywords": ["sweden","stockholm"],
        "fallbacks": ["Sweden economy update today","Swedish government statement today","Sweden NATO update today"],
        "pexels_map": {"default":"stockholm city"},
        "source": "Reuters / Swedish Government"
    },
    "france": {
        "keywords": ["france","paris","macron"],
        "fallbacks": ["France government statement today","France economy update today","Paris EU policy today"],
        "pexels_map": {"default":"paris city"},
        "source": "Reuters / French Government"
    },
    "houthis": {
        "keywords": ["houthi","yemen","red sea"],
        "fallbacks": ["Red Sea shipping security update today","UN statement Yemen today","US Navy Red Sea operation today","Yemen humanitarian report today"],
        "pexels_map": {"default":"cargo ship sea"},
        "source": "Reuters / US Navy / UN"
    },
    "saudi_iraq_oil": {
        "keywords": ["saudi","iraq","oil","opec","baghdad","riyadh"],
        "fallbacks": ["OPEC oil production decision today","Saudi Arabia economy today","Iraq government statement today","Oil price update today","OPEC+ meeting outcome today"],
        "pexels_map": {"oil":"oil refinery","default":"oil rig"},
        "source": "Reuters / OPEC / EIA"
    },
    "rebels": {
        "keywords": ["rebel","insurgent"],
        "fallbacks": ["UN report on armed conflict today","Security Council briefing today","Humanitarian situation update today"],
        "pexels_map": {"default":"un building"},
        "source": "UN / Reuters - no graphic",
        "safe_prompt": "Neutral UN statements only. No graphic violence."
    },
    "muslim_world": {
        "keywords": ["muslim","oic"],
        "fallbacks": ["OIC statement today","Saudi Arabia Hajj update today","UN cultural heritage Middle East today","Ramadan preparations today"],
        "pexels_map": {"default":"mosque"},
        "source": "Reuters / OIC / UN",
        "safe_prompt": "Cultural factual only, respectful."
    },
    # --- UUDET PILLARIT ---
    "ufo_orbs": {
        "keywords": ["ufo","uap","orb","unidentified"],
        "fallbacks": [
            "NASA UAP report update today",
            "Pentagon UAP office statement today",
            "US Congress UFO hearing update today",
            "NASA orb sighting analysis today",
            "Pentagon confirms UAP investigation today"
        ],
        "pexels_map": {"ufo":"night sky stars","orb":"light orb night","default":"night sky"},
        "source": "NASA / Pentagon AARO / Reuters - official statements only",
        "safe_prompt": "Use ONLY official NASA and Pentagon AARO statements. No conspiracy, no alien claims. Explain what was officially confirmed, what is under investigation. Neutral."
    },
    "aviation_accidents": {
        "keywords": ["plane crash","aviation","airplane","flight accident","air crash"],
        "fallbacks": [
            "FAA aviation safety report today",
            "NTSB investigation update today",
            "EASA aviation safety bulletin today",
            "Airline safety statement today",
            "Aviation accident preliminary report today"
        ],
        "pexels_map": {"default":"airplane runway"},
        "source": "FAA / NTSB / EASA / Reuters - preliminary reports",
        "safe_prompt": "Use only official FAA/NTSB/EASA preliminary statements. No graphic details, no speculation on cause, no victim names until officially released. Respectful."
    },
    "gold_silver": {
        "keywords": ["gold","silver","precious metal"],
        "fallbacks": [
            "Gold price update today - market analysis",
            "Silver price market update today",
            "Federal Reserve gold reserves report today",
            "Central banks gold buying report today",
            "Gold silver market outlook today"
        ],
        "pexels_map": {"gold":"gold bars","silver":"silver bars","default":"gold bars"},
        "source": "Reuters / Bloomberg / Fed / LBMA",
        "safe_prompt": "Market data only from Reuters/Bloomberg. No investment advice, just official price and central bank reports."
    },
    "crypto": {
        "keywords": ["bitcoin","crypto","ethereum","cryptocurrency","blockchain"],
        "fallbacks": [
            "Bitcoin price update today",
            "Ethereum market update today",
            "SEC crypto regulation update today",
            "Crypto market analysis today",
            "Federal Reserve on digital assets today"
        ],
        "pexels_map": {"bitcoin":"bitcoin coin","crypto":"cryptocurrency","default":"bitcoin"},
        "source": "Reuters / SEC / Bloomberg",
        "safe_prompt": "Market data only, no investment advice. Use official SEC statements."
    },
    "natural_disasters": {
        "keywords": ["earthquake","flood","hurricane","tornado","volcano","tsunami","wildfire","storm","landslide","cyclone","typhoon"],
        "fallbacks": [
            "USGS earthquake report today",
            "NOAA storm warning today",
            "Flood warning update today",
            "Volcano activity report today",
            "Hurricane tracking update today",
            "Wildfire situation report today",
            "Tsunami warning center update today",
            "Extreme weather alert today"
        ],
        "pexels_map": {"earthquake":"earthquake damage","flood":"flood water","hurricane":"hurricane","tornado":"tornado","volcano":"volcano eruption","wildfire":"wildfire","tsunami":"ocean wave","default":"storm clouds"},
        "source": "USGS / NOAA / NASA / Reuters",
        "safe_prompt": "Use ONLY official USGS/NOAA data. No graphic injury details. Focus on magnitude, location, official warnings."
    },
    "accidents": {
        "keywords": ["accident","crash","derailment","explosion","fire"],
        "fallbacks": [
            "Traffic accident report official today",
            "Industrial safety report today",
            "Emergency services response update today",
            "NTSB accident report today"
        ],
        "pexels_map": {"default":"emergency lights"},
        "source": "Reuters / NTSB / Local officials - no graphic",
        "safe_prompt": "No graphic injury, no names until official. Official statements only."
    },
    "india": {
        "keywords": ["india","delhi","modi","mumbai"],
        "fallbacks": ["India economy update today","Indian government statement today","India tech sector news today","Reserve Bank of India statement today"],
        "pexels_map": {"default":"taj mahal india"},
        "source": "Reuters / Indian Government / RBI"
    },
    "china": {
        "keywords": ["china","beijing","xi jinping","shanghai"],
        "fallbacks": ["China economy update today","Chinese government statement today","China tech market update today","PBOC statement today"],
        "pexels_map": {"default":"beijing city"},
        "source": "Reuters / Chinese Government"
    },
    "japan": {
        "keywords": ["japan","tokyo","japanese"],
        "fallbacks": ["Japan economy update today","Japanese government statement today","Bank of Japan decision today","Japan tech news today"],
        "pexels_map": {"default":"tokyo city"},
        "source": "Reuters / Japanese Government / BOJ"
    },
    "australia": {
        "keywords": ["australia","sydney","canberra"],
        "fallbacks": ["Australia economy update today","Australian government statement today","RBA interest rate decision today","Australia wildfire update today"],
        "pexels_map": {"default":"sydney opera house"},
        "source": "Reuters / Australian Government / RBA"
    }
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
    prompt = f"Topic: {topic}. Pillar: {pillar_key}. Task: Neutral news based ONLY on official sources: {base_source}. {safe_extra} What was officially confirmed today, context, next steps. No speculation, no hate, no graphic."
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
    if not OPENROUTER_API_KEY:
        return f"Breaking: {trending_topic}\n\nAccording to {source_line}, developments continue. Source: {source_line}."
    try:
        import requests
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        system_prompt = f"""You are World Viral, neutral global news covering {pillar_key}.
RULES:
- 110 words max for YouTube Shorts
- Neutral, factual, no bias, no hate, no stereotypes
- Use ONLY official sources: {source_line}
- No graphic violence, no conspiracy, no praising armed groups
- For aviation/disasters: official preliminary only, respectful
- For UFO/UAP: official NASA/Pentagon AARO only, no alien claims
- For gold/silver/crypto: market data only, no investment advice
- Structure: Hook, Fact1 official, Fact2 context, Fact3 next, Source
- English only
- End with Source: {source_line}"""
        payload = {"model": "google/gemini-flash-1.5-8b:free","messages": [{"role":"system","content":system_prompt},{"role":"user","content":official_prompt}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI error {e}")
        return f"Today: {trending_topic}. Official sources report update. Source: {source_line}."

async def make_voice(text, output_file="voice.mp3"):
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        await communicate.save(output_file)
        return output_file
    except:
        return None

def make_video_trending(script_text, voice_file, pexels_clip=None):
    try:
        from moviepy.editor import VideoFileClip, ColorClip, TextClip, CompositeVideoClip, AudioFileClip
        import textwrap
        duration = 35
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration).resize((1080,1920))
            except:
                bg = ColorClip(size=(1080,1920), color=(12,18,30), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(12,18,30), duration=duration)
        wrapped = textwrap.fill(script_text, width=34)
        try:
            txt_clip = TextClip(wrapped, fontsize=42, color='white', stroke_color='black', stroke_width=2, font='Arial-Bold', method='caption', size=(900,1350)).set_position('center').set_duration(duration)
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
            print(f"TextClip failed {e}")
            if voice_file and os.path.exists(voice_file):
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(voice_file)
                bg = bg.set_duration(audio.duration + 1).set_audio(audio)
            bg.write_videofile("world_viral_output.mp4", fps=24)
            return "world_viral_output.mp4"
    except Exception as e:
        print(f"Video error {e}")
        return None

async def main():
    print("WORLD VIRAL MEGA MULTI-PILLAR V4")
    trending_topic, pillar_key = get_trending_topic_multi()
    official_prompt, pillar, pexels_kw, source_line = get_official_prompt(trending_topic, pillar_key)
    print(f"Pillar: {pillar} | Topic: {trending_topic} | Pexels: {pexels_kw}")
    pexels_clip = get_pexels_video(pexels_kw)
    script = generate_script(official_prompt, trending_topic, pillar, source_line)
    print(f"Script:\n{script}")
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {trending_topic} | World Viral {pillar}\n\n{script}\n\n---\nPillar: {pillar}\nSource: {source_line}\n#worldviral #{pillar} #breaking #news #trending")
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

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
