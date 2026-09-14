"""
WORLD VIRAL - TRENDI BOTTI V2
100% Free & Laillinen
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
        if r.status_code!= 200:
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
    return random.choice(trends) if trends else random.choice(get_trending_fallback())

def get_earth_data():
    try:
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1&orderby=time", timeout=10)
        data = r.json()
        props = data['features'][0]['properties']
        return f"Magnitude {props['mag']} earthquake hit {props['place']}"
    except:
        return "Significant seismic activity today"

def get_official_source_for_trend(trend):
    return f"Official: {trend} - USGS / NASA reports today", "earth", "earthquake"

def generate_script(prompt_topic, trending_topic):
    if not OPENROUTER_API_KEY:
        return f"Breaking: {trending_topic}. {prompt_topic}. Officials monitoring. Source: USGS."
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "google/gemini-flash-1.5-8b:free","messages": [{"role":"user","content": f"Write 100 words news about: {trending_topic} - {prompt_topic}"}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()['choices'][0]['message']['content']
    except:
        return f"Today: {trending_topic}. {prompt_topic}. Source: USGS."

async def make_voice(text, output_file="voice.mp3"):
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        await communicate.save(output_file)
        return output_file
    except:
        return None

def make_video_trending(script_text, voice_file, pexels_clip=None):
    try:
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
        import textwrap
        duration = 30
        bg = ColorClip(size=(1080,1920), color=(10,10,10), duration=duration)
        wrapped = textwrap.fill(script_text, width=36)
        txt_clip = TextClip(wrapped, fontsize=42, color='white', stroke_color='black', stroke_width=2, method='caption', size=(900,1400)).set_position('center').set_duration(duration)
        if voice_file and os.path.exists(voice_file):
            audio = AudioFileClip(voice_file)
            bg = bg.set_duration(audio.duration + 1).set_audio(audio)
            txt_clip = txt_clip.set_duration(audio.duration + 1)
        final = CompositeVideoClip([bg, txt_clip])
        final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac')
        return "world_viral_output.mp4"
    except Exception as e:
        print(f"Video error {e}")
        return None

async def main():
    print("WORLD VIRAL TRENDI BOTTI V2")
    trending_topic = get_combined_trending_topic()
    official_data, pillar, pexels_kw = get_official_source_for_trend(trending_topic)
    script = generate_script(official_data, trending_topic)
    print(f"Script: {script}")
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(f"TITLE: {trending_topic}\n\n{script}")
    voice_file = await make_voice(script)
    video_file = make_video_trending(script, voice_file, None)
    print(f"Valmis: {video_file}")

if __name__ == "__main__":
    asyncio.run(main())
