"""
WORLD VIRAL - TRENDI BOTTI V2
100% Free & Laillinen - Ei varasta videoita, tekee oman version trendista
"""
import os, random, requests, asyncio, re, xml.etree.ElementTree as ET
from datetime import datetime
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PILLAR = os.getenv("PILLAR", "auto")

def get_trending_from_google_trends(geo="US"):
    try:
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        trends = []
        for item in root.findall('.//item')[:10]:
            t = item.find('title').text if item.find('title') is not None else ""
            trends.append(t)
        return trends
    except:
        return []

def get_trending_fallback():
    return ["earthquake today","solar storm","flood europe","SpaceX launch","AI robot","oil price","EU new law","volcano eruption","hurricane update","bitcoin price","NASA discovery"]

def get_combined_trending_topic():
    trends = get_trending_from_google_trends("US")
    if not trends:
        trends = get_trending_fallback()
    print(f"Trendaavat nyt: {trends[:5]}")
    valid = ["earthquake","flood","storm","quake","volcano","hurricane","tornado","nasa","spacex","rocket","ai","robot","cern","oil","bitcoin","euro","eu","price","market"]
    relevant = [t for t in trends for kw in valid if kw.lower() in t.lower()]
    if relevant:
        return random.choice(relevant)
    return random.choice(get_trending_fallback())

def get_earth_data():
    try:
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1&orderby=time", timeout=10)
        data = r.json()
        props = data['features'][0]['properties']
        return f"Magnitude {props['mag']} earthquake hit {props['place']} at {datetime.fromtimestamp(props['time']/1000).strftime('%H:%M UTC')}"
    except:
        return "Significant seismic activity in Pacific Ring of Fire today"

def get_official_source_for_trend(trend):
    tl = trend.lower()
    if any(x in tl for x in ["earthquake","quake"]):
        return get_earth_data(), "earth", "earthquake"
    elif any(x in tl for x in ["flood","storm","hurricane","tornado","volcano"]):
        return f"Extreme weather: {trend} reported by NOAA today", "earth", "storm"
    elif any(x in tl for x in ["nasa","spacex","rocket","moon"]):
        return f"Space update: {trend} - NASA/SpaceX today", "tech", "space"
    elif any(x in tl for x in ["ai","robot","cern"]):
        return f"Future tech: {trend} - new development today", "tech", "technology"
    else:
        return f"Money: {trend} - market impact today", "money", "business"

def get_pexels_video(query):
    if not PEXELS_API_KEY:
        return None
    try:
        mapping = {"earthquake":"earthquake damage city","flood":"flood water","storm":"storm clouds","hurricane":"hurricane storm","tornado":"tornado storm","nasa":"space earth","spacex":"rocket launch","ai":"robot technology","robot":"robot technology","oil":"oil industry","bitcoin":"bitcoin crypto","volcano":"volcano eruption"}
        search_query = query
        for k,v in mapping.items():
            if k in query.lower():
                search_query = v
                break
        url = f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait"
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

def generate_script(prompt_topic, trending_topic):
    if not OPENROUTER_API_KEY:
        return f"Breaking: {trending_topic}\n\nAccording to official sources, {prompt_topic}\n\nOfficials are monitoring.\n\nSource: USGS / NASA / NOAA."
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        system_prompt = "You are World Viral, neutral news. Write 110 words max for YouTube Shorts. Hook, Fact1,2,3, Source. No graphic, no hate. English only."
        payload = {"model": "google/gemini-flash-1.5-8b:free","messages": [{"role":"system","content":system_prompt},{"role":"user","content":f"Trending: {trending_topic}\nOfficial: {prompt_topic}"}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()['choices'][0]['message']['content']
    except:
        return f"Today: {trending_topic}. Official: {prompt_topic}. Source: USGS / NASA."

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
                bg = ColorClip(size=(1080,1920), color=(10,10,10), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(10,10,10), duration=duration)
        wrapped = textwrap.fill(script_text, width=36)
        try:
            txt_clip = TextClip(wrapped, fontsize=46, color='white', stroke_color='black', stroke_width=2, font='Arial-Bold', method='caption', size=(900,1400)).set_position('center').set_duration(duration)
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
    print("WORLD VIRAL TRENDI BOTTI V2")
    trending_topic = get_combined_trending_topic()
    official_data, pillar, pexels_kw = get_official_source_for_trend(trending_topic)
    actual_pillar = pillar if PILLAR == "auto" else PILLAR
    print(f"Virallinen data: {official_data}")
    pexels_clip = get_pexels_video(pexels_kw)
    script = generate_script(official_data, trending_topic)
    print(f"Script:\n{script}")
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {trending_topic} | World Viral\n\n{script}\n\n---\nTrending: {trending_topic}\nSource: USGS / NASA / NOAA / Reuters\n#worldviral #trending #{actual_pillar}")
    voice_file = await make_voice(script)
    video_file = make_video_trending(script, voice_file, pexels_clip)
    print(f"Valmis: {video_file}")
    if video_file and os.path.exists(video_file):
        try:
            from youtube_uploader import upload_video
            title = f"{trending_topic} - What We Know Today | World Viral"[:95]
            with open("script.txt","r", encoding="utf-8") as f:
                desc = f.read()
            upload_video(file_path=video_file, title=title, description=desc, tags=[trending_topic, actual_pillar, "worldviral", "trending"], privacy="public")
        except Exception as e:
            print(f"YouTube skip: {e}")

if __name__ == "__main__":
    asyncio.run(main())
