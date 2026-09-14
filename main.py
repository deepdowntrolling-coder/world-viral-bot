
"""
WORLD VIRAL V10 HYBRID - NEWS + PRODUCT WITH REAL IMAGE
- Combines V8 real news + V9 sales but with REAL product image
- Flow: Real Reuters news 20s -> Recommended product 10s with image
- Fetches product image from Amazon.de + Pexels background
- 100% English, product image overlay, news ticker with source
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET, re, json, textwrap
from datetime import datetime
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG", "worldviral052-21")
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"V10 HYBRID | PEXELS: {'SET' if PEXELS_API_KEY else 'NOT'} | TAG: {AMAZON_TAG}")

# V8 RSS - real news
RSS_FEEDS = {
    "usa_iran": ["https://news.google.com/rss/search?q=USA+Iran+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "russia_ukraine": ["https://news.google.com/rss/search?q=Ukraine+Russia+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "eu_euro": ["https://news.google.com/rss/search?q=EU+ECB+Euro+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "uk": ["https://news.google.com/rss/search?q=UK+economy+when:1d&hl=en-GB&gl=GB&ceid=GB:en"],
    "saudi_iraq_oil": ["https://news.google.com/rss/search?q=OPEC+oil+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "gold_silver": ["https://news.google.com/rss/search?q=gold+price+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "crypto": ["https://news.google.com/rss/search?q=Bitcoin+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "natural_disasters": ["https://news.google.com/rss/search?q=earthquake+OR+hurricane+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "aviation_accidents": ["https://news.google.com/rss/search?q=FAA+NTSB+when:3d&hl=en-US&gl=US&ceid=US:en"],
    "ufo_orbs": ["https://news.google.com/rss/search?q=NASA+UAP+when:7d&hl=en-US&gl=US&ceid=US:en"],
}

# Map news pillar -> relevant product (for natural placement)
PILLAR_TO_PRODUCT = {
    "usa_iran": {"name": "Emergency Radio NOAA", "search": "NOAA weather radio", "pexels": ["emergency radio","weather radio"], "price": "29-69€", "commission": "5%", "reason": "Stay informed during crisis"},
    "russia_ukraine": {"name": "Military Backpack 60L", "search": "military backpack 60L", "pexels": ["military backpack","tactical backpack"], "price": "39-129€", "commission": "12%", "reason": "Field gear used by reporters"},
    "eu_euro": {"name": "Money Counter Machine", "search": "money counter", "pexels": ["money counting machine","euro money"], "price": "79-199€", "commission": "5%", "reason": "For cash businesses"},
    "uk": {"name": "Travel Luggage Lock", "search": "travel luggage", "pexels": ["travel luggage","airport suitcase"], "price": "49-199€", "commission": "10%", "reason": "UK travel essential"},
    "saudi_iraq_oil": {"name": "Oil Work Boots Resistant", "search": "oil resistant work boots", "pexels": ["oil rig worker","work boots oil"], "price": "59-149€", "commission": "10%", "reason": "Oil industry gear"},
    "gold_silver": {"name": "Gold Scale 0.01g Jewelry", "search": "jewelry scale 0.01g", "pexels": ["gold scale","jewelry scale","gold bars"], "price": "12-39€", "commission": "5%", "reason": "Weigh your gold accurately"},
    "crypto": {"name": "Ledger Nano Crypto Wallet", "search": "Ledger Nano", "pexels": ["crypto wallet hardware","bitcoin wallet"], "price": "59-149€", "commission": "15%", "reason": "Secure your crypto"},
    "natural_disasters": {"name": "Earthquake Emergency Kit", "search": "earthquake emergency kit", "pexels": ["emergency kit","survival backpack"], "price": "29-99€", "commission": "15%", "reason": "Be prepared"},
    "aviation_accidents": {"name": "Aviation Radio Scanner", "search": "aviation radio scanner", "pexels": ["aviation radio","air traffic control"], "price": "89-299€", "commission": "5%", "reason": "Listen to ATC"},
    "ufo_orbs": {"name": "Telescope 130mm Astronomy", "search": "telescope 130mm", "pexels": ["telescope stars","astronomy telescope"], "price": "99-399€", "commission": "5%", "reason": "Watch the skies"},
}

def fetch_real_news(pillar):
    feeds = RSS_FEEDS.get(pillar, list(RSS_FEEDS.values())[0])
    for rss_url in feeds:
        try:
            r = requests.get(rss_url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
            items = root.findall('.//item')[:5]
            for item in items:
                title = item.find('title').text if item.find('title') is not None else "Breaking News"
                link = item.find('link').text if item.find('link') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else title
                pub = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime("%Y-%m-%d")
                # Clean HTML
                desc = re.sub('<[^<]+?>', '', desc)[:300]
                if len(title) > 15:
                    return {"title": title.strip(), "link": link, "desc": desc, "pub": pub, "pillar": pillar}
        except Exception as e:
            print(f"RSS fail {rss_url}: {e}")
            continue
    return {"title": f"{pillar.replace('_',' ').title()} Update Today", "link": "https://reuters.com", "desc": f"Latest {pillar} news update", "pub": datetime.now().isoformat(), "pillar": pillar}

def get_pexels_video(queries):
    if not PEXELS_API_KEY:
        return None
    if isinstance(queries, str):
        queries = [queries]
    headers = {"Authorization": PEXELS_API_KEY}
    for q in queries:
        try:
            url = f"https://api.pexels.com/videos/search?query={q}&per_page=3&orientation=portrait"
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                for video in r.json().get('videos', []):
                    try:
                        files = sorted(video['video_files'], key=lambda x: x['width'], reverse=True)
                        best = files[0]
                        vdata = requests.get(best['link'], timeout=30).content
                        if len(vdata) > 150000:
                            with open("pexels_clip.mp4","wb") as f:
                                f.write(vdata)
                            print(f"Pexels OK: {q}")
                            return "pexels_clip.mp4"
                    except:
                        continue
        except Exception as e:
            print(f"Pexels fail {e}")
    return None

def get_amazon_product_image(search_term):
    """Try to fetch real Amazon.de product image via scraping, fallback to Pexels image of product"""
    # Try Amazon.de search page for first image
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "en-US,en;q=0.9"}
        url = f"https://www.amazon.de/s?k={search_term.replace(' ','+')}"
        r = requests.get(url, headers=headers, timeout=12)
        # Find first product image via regex
        # Amazon images: https://m.media-amazon.com/images/I/...
        matches = re.findall(r'https://m\.media-amazon\.com/images/I/[^"\s]+\.jpg', r.text)
        if matches:
            img_url = matches[0].replace("._SS", "._SL500_")  # larger
            img_data = requests.get(img_url, headers=headers, timeout=12).content
            if len(img_data) > 10000:
                with open("product_image.jpg","wb") as f:
                    f.write(img_data)
                print(f"Amazon image OK: {search_term} -> {img_url[:60]}")
                return "product_image.jpg"
    except Exception as e:
        print(f"Amazon image fail {e}")
    
    # Fallback: search Pexels image for product
    if PEXELS_API_KEY:
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=1"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200 and r.json().get('photos'):
                img_url = r.json()['photos'][0]['src']['large']
                img_data = requests.get(img_url, timeout=10).content
                with open("product_image.jpg","wb") as f:
                    f.write(img_data)
                print(f"Pexels product image fallback: {search_term}")
                return "product_image.jpg"
        except Exception as e:
            print(f"Pexels image fallback fail {e}")
    return None

def generate_script(news, product):
    title = news['title']
    pillar = news['pillar']
    fallback = f"Breaking News: {title}. This is a major update today. Reports confirm developments in {pillar.replace('_',' ')}. Officials are monitoring the situation. Stay tuned for live updates. In related news, many viewers are getting {product['name']} - {product['reason']}. Link in description. Price {product['price']}."

    if not OPENROUTER_API_KEY:
        return fallback
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-viral", "X-Title": "World Viral V10"}
        prompt = f"You are a YouTube Shorts news anchor. Write 150-word script in English only.\nNews: {title}. Desc: {news['desc']}. Pillar: {pillar}.\nFirst 100 words: explain the news factually, exciting, like Breaking News.\nLast 50 words: natural transition to product recommendation: '{product['name']}' - {product['reason']}. Price {product['price']}. Say 'Link in description' and 'We earn commission'. No Finnish. No fake claims."
        for model in ["google/gemini-flash-1.5-8b:free","meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload = {"model": model, "messages": [{"role":"user","content": prompt}], "max_tokens": 350, "temperature": 0.7}
                r = requests.post(url, headers=headers, json=payload, timeout=25)
                data = r.json()
                if "choices" in data and data["choices"][0].get("message",{}).get("content"):
                    txt = data["choices"][0]["message"]["content"].strip()
                    if len(txt) > 80:
                        return txt
            except Exception as e:
                continue
        return fallback
    except Exception as e:
        return fallback

async def make_voice(text, output="voice.mp3"):
    try:
        clean = text.replace("\n"," ").strip()[:900]
        communicate = edge_tts.Communicate(clean, "en-US-GuyNeural", rate="+5%", volume="+10%")
        await communicate.save(output)
        return output
    except Exception as e:
        print(f"TTS fail {e}")
        return None

def make_hybrid_video(script_text, voice_file, pexels_clip, news, product, product_image_path):
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import os

        duration = 35
        audio_clip = None
        if voice_file and os.path.exists(voice_file):
            try:
                audio_clip = AudioFileClip(voice_file)
                duration = min(58, max(28, audio_clip.duration + 2.5))
            except:
                pass

        # Background video
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration)
                bg = bg.resize(height=1920)
                if bg.w < 1080:
                    bg = bg.resize(width=1080)
                bg = bg.crop(x_center=bg.w/2, y_center=bg.h/2, width=1080, height=1920).set_duration(duration)
            except:
                bg = ColorClip(size=(1080,1920), color=(10,20,40), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(10,20,40), duration=duration)

        W, H = 1080, 1920
        # Create overlay PIL
        overlay = Image.new('RGBA', (W, H), (0,0,0,0))
        draw = ImageDraw.Draw(overlay)
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        except:
            font_big = ImageFont.load_default()
            font_med = font_big
            font_small = font_big
            font_tiny = font_big

        # TOP BREAKING BANNER
        draw.rectangle([(0,0),(W,105)], fill=(200,0,0,255))
        draw.text((20,22), "🔴 BREAKING NEWS", font=font_big, fill=(255,255,255,255))
        draw.text((W-210,30), datetime.now().strftime("%H:%M UTC"), font=font_small, fill=(255,255,255,255))

        # MAIN NEWS BOX
        box_y = 130
        box_h = 850
        draw.rounded_rectangle([(20, box_y),(W-20, box_y+box_h)], radius=20, fill=(0,0,0,175))

        # Title
        title_lines = textwrap.wrap(news['title'][:110], width=32)
        y = box_y + 20
        for line in title_lines[:3]:
            draw.text((40, y), line.upper(), font=font_med, fill=(255,215,0,255))
            y += 42

        # Script wrapped - first part
        y += 10
        wrapped = textwrap.wrap(script_text, width=36)[:14]
        for i, line in enumerate(wrapped):
            # shadow
            for dx,dy in [(-1,-1),(1,1)]:
                draw.text((40+dx, y+dy), line, font=font_small, fill=(0,0,0,255))
            draw.text((40, y), line, font=font_small, fill=(255,255,255,255))
            y += 34
            if y > box_y+box_h-20:
                break

        # PRODUCT SECTION - bottom 800px
        prod_y = H - 820
        draw.rounded_rectangle([(20, prod_y),(W-20, H-20)], radius=20, fill=(255,255,255,240))

        # Product image - will be placed via moviepy if exists, but draw placeholder frame
        # If product image exists, we will composite it later
        draw.rectangle([(35, prod_y+15),(335, prod_y+315)], fill=(240,240,240,255), outline=(200,200,200,255), width=2)
        draw.text((40, prod_y+320), "PRODUCT IMAGE", font=font_tiny, fill=(100,100,100,255))

        # Product info to the right of image
        draw.text((360, prod_y+15), product['name'][:28].upper(), font=font_med, fill=(0,0,0,255))
        draw.text((360, prod_y+60), f"{product['price']} | {product['commission']} commission", font=font_small, fill=(0,128,0,255))
        draw.text((360, prod_y+100), product['reason'][:45], font=font_small, fill=(50,50,50,255))

        # CTA
        draw.rounded_rectangle([(360, prod_y+145),(W-40, prod_y+210)], radius=10, fill=(255,140,0,255))
        draw.text((380, prod_y+160), "👉 LINK IN DESCRIPTION", font=font_med, fill=(255,255,255,255))

        draw.text((360, prod_y+225), f"Amazon: {product['search']} | {AMAZON_TAG}", font=font_tiny, fill=(80,80,80,255))
        draw.text((360, prod_y+250), "As Amazon Associate we earn commission", font=font_tiny, fill=(100,100,100,255))

        # Source ticker
        ticker_y = H - 110
        draw.rectangle([(0, H-110),(W, H)], fill=(0,0,0,230))
        draw.text((15, H-90), f"Source: Reuters/Google News | {news['link'][:60]} | #{news['pillar']} #WorldViral", font=font_tiny, fill=(200,200,200,255))
        draw.text((15, H-60), f"Product: {product['name']} {product['price']} | Disclaimer: affiliate link", font=font_tiny, fill=(180,180,180,255))

        overlay.save("text_overlay.png")
        txt_clip = ImageClip("text_overlay.png", duration=duration).set_duration(duration)

        clips = [bg, txt_clip]

        # If real product image exists, add it as ImageClip over the placeholder
        if product_image_path and os.path.exists(product_image_path):
            try:
                prod_img_clip = ImageClip(product_image_path, duration=duration).set_duration(duration)
                # Resize to fit 300x300 box at (35, prod_y+15)
                prod_img_clip = prod_img_clip.resize(width=300)
                if prod_img_clip.h > 300:
                    prod_img_clip = prod_img_clip.resize(height=300)
                # Position
                prod_img_clip = prod_img_clip.set_position((35, prod_y+15))
                clips.append(prod_img_clip)
                print(f"Product image overlay added: {product_image_path}")
            except Exception as e:
                print(f"Product img clip fail {e}")

        final = CompositeVideoClip(clips)
        if audio_clip:
            final = final.set_audio(audio_clip)

        final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac', bitrate="4500k", preset="ultrafast", threads=4)
        print(f"V10 hybrid video done: {news['title'][:40]} + {product['name']}")
        return "world_viral_output.mp4"

    except Exception as e:
        print(f"Video fail {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("WORLD VIRAL V10 HYBRID - NEWS + PRODUCT IMAGE")

    # Pick pillar
    if PILLAR_ENV != "auto" and PILLAR_ENV in RSS_FEEDS:
        pillar = PILLAR_ENV
    else:
        pillar = random.choice(list(RSS_FEEDS.keys()))

    print(f"Pillar: {pillar}")

    news = fetch_real_news(pillar)
    product = PILLAR_TO_PRODUCT.get(pillar, list(PILLAR_TO_PRODUCT.values())[0])

    pexels_clip = get_pexels_video(product["pexels"] + [pillar.replace("_"," ")])
    product_img = get_amazon_product_image(product["search"])
    script = generate_script(news, product)

    amazon_search = product["search"].replace(" ","+")
    amazon_link = f"https://www.amazon.de/s?k={amazon_search}&tag={AMAZON_TAG}"
    # Also direct product page link search
    amazon_direct = f"https://www.amazon.de/s?k={amazon_search}&tag={AMAZON_TAG}&linkCode=ll1"

    desc = f"""🔴 {news['title']}

{script}

📰 Full story: {news['link']}
Source: Reuters / Google News | Published: {news['pub']}

🛒 RECOMMENDED GEAR (Related to this news):
{product['name']} - {product['price']}
Why: {product['reason']}
Get it here: {amazon_link}
Search term: {product['search']}
Commission: {product['commission']} - supports our news channel

As Amazon Associate we earn from qualifying purchases.

#BreakingNews #WorldNews #{pillar} #AmazonFinds #NewsUpdate
Pillar: {pillar} | Product: {product['name']} | Tag: {AMAZON_TAG}
"""

    with open("script.txt","w", encoding="utf-8") as f:
        f.write(desc)

    voice = await make_voice(script)
    video = make_hybrid_video(script, voice, pexels_clip, news, product, product_img)

    print(f"Done: {video} | News: {news['title'][:50]} | Product: {product['name']} | Img: {product_img is not None}")

    if video and os.path.exists(video):
        try:
            from youtube_uploader import upload_video
            title = f"{news['title'][:70]} | {product['name']} | World Viral"[:95]
            tags = [pillar, "breaking news", "world news", product['name'], "amazon finds", "news update"]
            upload_video(file_path=video, title=title, description=desc, tags=tags, privacy="public")
        except Exception as e:
            print(f"YouTube skip: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

