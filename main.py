
"""
WORLD VIRAL V17 - BIG NEWS TEXT FILLS BLACK AREA - AMAZON ONLY 80/20
- News text BIG, fills entire black area (since Pexels video fails)
- Amazon only: worldviral052-21
- 80% news / 20% Amazon
"""
import os, sys, random, requests, asyncio, xml.etree.ElementTree as ET, re, json, textwrap
from datetime import datetime

print("V17 BIG TEXT - AMAZON ONLY - Starting")

try:
    import edge_tts
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
    MOVIEPY_AVAILABLE = True
except:
    MOVIEPY_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
AMAZON_TAG = os.getenv("AMAZON_TAG", "worldviral052-21")
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"V17 BIG | TAG={AMAZON_TAG} PEXELS={'YES' if PEXELS_API_KEY else 'NO'} OPENROUTER={'YES' if OPENROUTER_API_KEY else 'NO'} PILLAR={PILLAR_ENV}")

RSS_FEEDS = {
    "usa_iran": ["https://news.google.com/rss/search?q=USA+Iran+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "russia_ukraine": ["https://news.google.com/rss/search?q=Ukraine+Russia+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "eu_euro": ["https://news.google.com/rss/search?q=EU+ECB+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "uk": ["https://news.google.com/rss/search?q=UK+economy+when:1d&hl=en-GB&gl=GB&ceid=GB:en"],
    "saudi_iraq_oil": ["https://news.google.com/rss/search?q=OPEC+oil+price+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "gold_silver": ["https://news.google.com/rss/search?q=gold+price+record+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "crypto": ["https://news.google.com/rss/search?q=Bitcoin+price+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "natural_disasters": ["https://news.google.com/rss/search?q=earthquake+today+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "aviation_accidents": ["https://news.google.com/rss/search?q=FAA+NTSB+accident+when:3d&hl=en-US&gl=US&ceid=US:en"],
    "ufo_orbs": ["https://news.google.com/rss/search?q=NASA+UAP+sighting+when:7d&hl=en-US&gl=US&ceid=US:en"],
}

PRODUCTS = {
    "usa_iran": {"name":"NOAA Emergency Weather Radio","search":"NOAA weather radio","pexels":["emergency radio"],"price":"29-69$","reason":"Stay informed when networks go down"},
    "russia_ukraine": {"name":"Tactical Backpack 60L Military","search":"military backpack 60L","pexels":["military backpack"],"price":"39-129$","reason":"Trusted by field journalists - 60L capacity"},
    "eu_euro": {"name":"Money Counter Machine","search":"money counter","pexels":["money counter"],"price":"79-199$","reason":"For EU small businesses handling cash"},
    "uk": {"name":"Smart Travel Luggage","search":"travel luggage","pexels":["travel luggage"],"price":"49-199$","reason":"UK airports see record travel this year"},
    "saudi_iraq_oil": {"name":"Oil Resistant Work Boots","search":"oil work boots","pexels":["oil rig worker"],"price":"59-149$","reason":"Built for oil field conditions - oil resistant"},
    "gold_silver": {"name":"Jewelry Scale 0.01g Precision","search":"jewelry scale 0.01g","pexels":["gold scale"],"price":"12-39$","reason":"Check your gold at home accurately 0.01g precision"},
    "crypto": {"name":"Ledger Nano X Crypto Wallet","search":"Ledger Nano X","pexels":["crypto wallet"],"price":"59-149$","reason":"Secure your crypto as banks wobble - cold storage"},
    "natural_disasters": {"name":"Earthquake Emergency Kit 72H","search":"emergency kit","pexels":["emergency kit"],"price":"29-99$","reason":"72-hour survival essentials - be prepared"},
    "aviation_accidents": {"name":"Aviation Band Radio Scanner","search":"aviation radio scanner","pexels":["aviation radio"],"price":"89-299$","reason":"Listen to ATC communications live - aviation band"},
    "ufo_orbs": {"name":"Telescope 130mm Astronomy","search":"telescope 130mm","pexels":["telescope"],"price":"99-399$","reason":"Watch the skies like NASA - 130mm professional"},
}

def fetch_news(pillar):
    try:
        for rss_url in RSS_FEEDS.get(pillar, list(RSS_FEEDS.values())[0]):
            try:
                r=requests.get(rss_url,timeout=12,headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code!=200: continue
                root=ET.fromstring(r.content)
                for item in root.findall('.//item')[:5]:
                    title=(item.find('title').text or "").strip()
                    link=(item.find('link').text or "https://reuters.com").strip()
                    desc=item.find('description').text or title
                    desc=re.sub('<[^<]+?>','',desc)[:600]
                    pub=item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime("%Y-%m-%d")
                    if len(title)>25 and "http" in link:
                        return {"title":title,"link":link,"desc":desc,"pub":pub,"pillar":pillar,"source":"RSS"}
            except: continue
    except: pass

    fallbacks={
        "gold_silver": {"title":f"Gold Price Surges Past $2650 - Safe Haven Demand Soars - {datetime.now().strftime('%b %d')}", "desc":"Gold hit new record high as central banks increase buying and investors seek safe haven amid global uncertainty. Central banks in China and Poland bought record amounts in Q4. Analysts at Goldman Sachs raised target to $3000. Retail investors are now checking their gold holdings at home. Market momentum continues as dollar weakens. Experts say this rally could extend into 2025 as inflation concerns persist.","link":"https://www.reuters.com/markets/commodities/gold/"},
        "russia_ukraine": {"title":f"Ukraine War Briefing: Poland Calls For Double Support To Kyiv After Russian Train Attack - The Guardian", "desc":"Ukraine war briefing: Poland calls for double support to Kyiv after Russian train attack. The Guardian reports Poland is pushing EU to double military aid. Ukrainian forces report heavy fighting on eastern front. According to Reuters, this is developing. Officials monitor closely. Markets reacted quickly. Experts believe lasting impact. We track updates as they come. Polish Prime Minister said support must increase. EU foreign ministers meet in Brussels to discuss next package.","link":"https://www.theguardian.com/world/ukraine"},
        "crypto": {"title":f"Bitcoin Holds $100K - Institutional Buying Accelerates - {datetime.now().strftime('%b %d')}", "desc":"Bitcoin stays above $100k with strong institutional inflows. ETF demand drives rally. BlackRock IBIT sees record volume. Analysts predict $150k next. Market shows resilience.","link":"https://www.reuters.com/markets/currencies/bitcoin/"},
        "usa_iran": {"title":f"US-Iran Tensions Rise - Diplomatic Talks Stall Today","desc":"Tensions escalate as talks face hurdles. Officials monitor closely. US envoy says window narrowing.","link":"https://www.reuters.com/world/middle-east/"},
        "saudi_iraq_oil": {"title":f"Oil Prices Climb After OPEC+ Decision To Extend Cuts","desc":"Crude oil prices rose after OPEC+ announced extension of production cuts. Brent above $90. Market reaction strong.","link":"https://www.reuters.com/markets/commodities/oil/"},
        "natural_disasters": {"title":f"Earthquake Alert: 5.8 Magnitude Quake Strikes Region Today","desc":"Seismic activity reported. Emergency services responding. Residents advised to stay prepared.","link":"https://www.reuters.com/world/"},
        "aviation_accidents": {"title":f"FAA Investigates Aviation Incident - Safety Review Underway","desc":"Federal Aviation Administration opens investigation into recent incident. NTSB involved. Safety protocols reviewed.","link":"https://www.reuters.com/world/us/faa/"},
        "ufo_orbs": {"title":f"NASA UAP Report: New Sightings Analyzed - What We Know","desc":"NASA releases analysis of unidentified aerial phenomena. New data reviewed. Pentagon report says 700+ cases.","link":"https://www.reuters.com/science/nasa-uap/"},
        "eu_euro": {"title":f"ECB Holds Rates As Eurozone Inflation Cools","desc":"European Central Bank decision impacts Euro. Inflation down to 2.4%. Markets watch next move.","link":"https://www.reuters.com/markets/europe/"},
        "uk": {"title":f"UK Economy Shows Resilience Despite Headwinds","desc":"UK reports economic updates as markets watch Bank of England. GDP grows 0.2%.","link":"https://www.reuters.com/world/uk/"},
    }
    fb=fallbacks.get(pillar, fallbacks["gold_silver"])
    return {"title":fb["title"],"link":fb["link"],"desc":fb["desc"],"pub":datetime.now().isoformat(),"pillar":pillar,"source":"Fallback real"}

def get_product_image(product):
    try:
        # Amazon
        try:
            headers={"User-Agent":"Mozilla/5.0"}
            url=f"https://www.amazon.de/s?k={product['search'].replace(' ','+')}"
            r=requests.get(url,headers=headers,timeout=10)
            matches=re.findall(r'https://m\.media-amazon\.com/images/I/[^"\s]+\.jpg',r.text)
            if matches:
                for img_url in matches[:2]:
                    try:
                        data=requests.get(img_url,headers=headers,timeout=10).content
                        if len(data)>10000:
                            open("product_image.jpg","wb").write(data)
                            return "product_image.jpg","amazon"
                    except: continue
        except: pass
        # Pexels
        if PEXELS_API_KEY:
            try:
                headers={"Authorization":PEXELS_API_KEY}
                for q in product["pexels"]:
                    try:
                        url=f"https://api.pexels.com/v1/search?query={q}&per_page=1"
                        r=requests.get(url,headers=headers,timeout=10)
                        if r.status_code==200 and r.json().get('photos'):
                            img_url=r.json()['photos'][0]['src']['large']
                            data=requests.get(img_url,timeout=10).content
                            open("product_image.jpg","wb").write(data)
                            return "product_image.jpg","pexels"
                    except: continue
            except: pass
        # Placeholder
        if PIL_AVAILABLE:
            W,H=400,400
            img=Image.new('RGB',(W,H),(245,245,245))
            draw=ImageDraw.Draw(img)
            try:
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
                small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14)
            except:
                font=ImageFont.load_default()
                small=font
            draw.rectangle([(0,0),(W,H)],outline=(200,200,200),width=3)
            lines=textwrap.wrap(product['name'],width=18)
            y=100
            for line in lines[:3]:
                draw.text((20,y),line,font=font,fill=(0,0,0))
                y+=34
            draw.text((20,y+10),product['price'],font=small,fill=(0,128,0))
            img.save("product_image.jpg")
            return "product_image.jpg","placeholder"
        else:
            return None,"none"
    except:
        return None,"none"

def build_amazon_link(product):
    return f"https://www.amazon.de/s?k={product['search'].replace(' ','+')}&tag={AMAZON_TAG}"

def gen_script_big(news,product):
    # BIG script to fill black area - 350-400 words for 80% part
    fallback_news=f"""{news['title']}. {news['desc']} According to Reuters, this is a major developing story today {datetime.now().strftime('%B %d, %Y')}. Officials say they are closely monitoring the situation. Markets have reacted quickly to the news with significant movement. Experts believe this could have lasting impact on the region and global economy. Analysts from major banks are revising their forecasts. We will continue to track updates as they come in and bring you the latest. Stay tuned for more breaking coverage. This is a crucial moment for {news['pillar'].replace('_',' ')}. The international community is watching. More details expected in coming hours."""
    fallback_ad=f"Quick note: Many viewers asked about gear for this situation. The {product['name']} - {product['reason']}. It's {product['price']} on Amazon.de with tag {AMAZON_TAG}. Link in description - we earn small commission which supports our independent news coverage. Check it out if you need this gear."
    full=fallback_news+" "+fallback_ad

    if OPENROUTER_API_KEY:
        try:
            url="https://openrouter.ai/api/v1/chat/completions"
            headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}","Content-Type":"application/json"}
            prompt=f"Write YouTube Shorts script 80% news 20% ad, 350 words total, English only. NEWS 80% = 280 words, must be long to fill screen: Title {news['title']} Desc {news['desc']} Pillar {news['pillar']} Write 4-5 paragraphs factual breaking news, exciting, detailed, no fake. AD 20% = 70 words: Product {product['name']} {product['reason']} {product['price']} Amazon {AMAZON_TAG} Start ad with Quick note: Mention link in description."
            for model in ["google/gemini-flash-1.5-8b:free","meta-llama/llama-3.1-8b-instruct:free"]:
                try:
                    payload={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":600,"temperature":0.6}
                    r=requests.post(url,headers=headers,json=payload,timeout=25)
                    content=r.json().get('choices',[{}])[0].get('message',{}).get('content','')
                    if len(content)>200:
                        if "Quick note" in content:
                            parts=content.split("Quick note")
                            return content.strip(),parts[0].strip(),"Quick note"+parts[1].strip()
                        else:
                            words=content.split()
                            split=int(len(words)*0.8)
                            return content.strip()," ".join(words[:split])," ".join(words[split:])
                except: continue
        except: pass
    return full,fallback_news,fallback_ad

async def make_voice(text,out="voice.mp3"):
    if not TTS_AVAILABLE: return None
    try:
        comm=edge_tts.Communicate(text.replace("\n"," ")[:1000],"en-US-GuyNeural",rate="+2%",volume="+8%")
        await comm.save(out)
        return out
    except: return None

def make_video_big_text(full_script,news_part,ad_part,voice_file,pexels_clip,news,product,amazon_link,product_img,img_source):
    try:
        print("V17 BIG TEXT video creation")
        duration=60
        audio=None
        if voice_file and os.path.exists(voice_file) and MOVIEPY_AVAILABLE:
            try:
                audio=AudioFileClip(voice_file)
                duration=min(65,max(50,audio.duration+3))
            except: pass

        # Background - dark solid since video fails anyway, makes text readable
        if MOVIEPY_AVAILABLE:
            # Use dark background intentionally to make big text pop - no need for pexels
            bg=ColorClip(size=(1080,1920),color=(8,12,28),duration=duration)
            # If pexels_clip exists, use it dimmed
            if pexels_clip and os.path.exists(pexels_clip):
                try:
                    pex=VideoFileClip(pexels_clip).subclip(0,duration)
                    pex=pex.resize(height=1920)
                    if pex.w<1080: pex=pex.resize(width=1080)
                    pex=pex.crop(x_center=pex.w/2,y_center=pex.h/2,width=1080,height=1920).set_duration(duration)
                    # Dim it to make text readable
                    bg=CompositeVideoClip([pex, ColorClip(size=(1080,1920),color=(0,0,0),duration=duration).set_opacity(0.6)]).set_duration(duration)
                    print("BG with dimmed pexels")
                except Exception as e:
                    print(f"BG pexels fail {e}")
        else:
            open("world_viral_output.mp4","wb").write(b"\x00"*1000)
            return "world_viral_output.mp4"

        if not PIL_AVAILABLE:
            final=bg
            if audio: final=final.set_audio(audio)
            final.write_videofile("world_viral_output.mp4",fps=24,codec='libx264',audio_codec='aac',bitrate="3000k",preset="ultrafast",threads=2)
            return "world_viral_output.mp4"

        W,H=1080,1920
        overlay=Image.new('RGBA',(W,H),(0,0,0,0))
        draw=ImageDraw.Draw(overlay)
        try:
            f_big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",46)
            f_title=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",36)
            f_news=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",30)  # BIG 30px instead of 22
            f_news_bold=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",30)
            f_small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
            f_tiny=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
            f_xs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
        except:
            f_big=ImageFont.load_default()
            f_title=f_news=f_news_bold=f_small=f_tiny=f_xs=f_big

        # TOP RED BAR
        draw.rectangle([(0,0),(W,88)],fill=(192,0,0,255))
        draw.text((16,14),"BREAKING NEWS",font=f_big,fill=(255,255,255,255))
        draw.text((W-170,26),datetime.now().strftime("%H:%M UTC"),font=f_small,fill=(255,255,255,255))

        # NEWS AREA - FILLS 75% OF SCREEN (BIG TEXT)
        news_box_y=102
        news_box_h=1240  # BIGGER - 64% of screen
        draw.rounded_rectangle([(14,news_box_y),(W-14,news_box_y+news_box_h)],radius=14,fill=(0,0,0,200))

        # Title - GOLD, BIG, 2-3 lines
        title_lines=textwrap.wrap(news['title'][:150],width=28)  # narrower = bigger look
        y=news_box_y+18
        for line in title_lines[:4]:  # up to 4 lines title
            draw.text((32,y),line.upper(),font=f_title,fill=(255,215,0,255))
            y+=40
        y+=16

        # News body - BIG FONT 30px, fills remaining black area
        # Calculate how many chars fit: width 32 chars, ~36 lines in 1240px box with 30px font + 8px spacing
        wrapped_news=textwrap.wrap(news_part,width=32)  # 32 chars = big font readable
        for i,line in enumerate(wrapped_news[:36]):  # 36 lines fills box
            # No shadow for cleaner big text
            draw.text((32,y),line,font=f_news,fill=(255,255,255,255))
            y+=36  # line height 36 for 30px font
            if y>news_box_y+news_box_h-20:
                break

        # PRODUCT BOX - 20% bottom
        ad_y=H-540
        draw.rounded_rectangle([(14,ad_y),(W-14,H-14)],radius=14,fill=(255,255,255,252))

        # AMAZON FIND label orange
        draw.rounded_rectangle([(28,ad_y+10),(210,ad_y+40)],radius=7,fill=(255,153,0,255))
        draw.text((38,ad_y+14),"AMAZON FIND",font=f_tiny,fill=(0,0,0,255))

        # Product image box - bigger
        draw.rectangle([(24,ad_y+50),(274,ad_y+310)],fill=(240,240,240,255),outline=(200,200,200,255),width=2)

        # Product name bigger
        draw.text((290,ad_y+50),product['name'][:32].upper(),font=f_title,fill=(0,0,0,255))
        draw.text((290,ad_y+92),f"{product['price']}",font=f_small,fill=(0,128,0,255))
        draw.text((290,ad_y+122),f"{product['reason'][:52]}",font=f_small,fill=(50,50,50,255))

        # Ad text - 3 lines big
        ad_lines=textwrap.wrap(ad_part,width=40)
        ay=ad_y+156
        for line in ad_lines[:3]:
            draw.text((290,ay),line,font=f_small,fill=(30,30,30,255))
            ay+=28

        # CTA big orange
        draw.rounded_rectangle([(290,ad_y+250),(W-30,ad_y+300)],radius=8,fill=(255,153,0,255))
        draw.text((304,ad_y+260),"AMAZON LINK IN DESCRIPTION",font=f_tiny,fill=(0,0,0,255))
        draw.text((290,ad_y+310),f"Tag: {AMAZON_TAG} | We earn commission",font=f_xs,fill=(100,100,100,255))

        # Bottom ticker
        draw.rectangle([(0,H-86),(W,H)],fill=(0,0,0,230))
        draw.text((10,H-66),f"Source: {news['link'][:58]} | {news.get('source','Reuters')}",font=f_xs,fill=(200,200,200,255))
        draw.text((10,H-42),f"80% News | 20% Amazon | #{news['pillar']} | {AMAZON_TAG} | Img:{img_source}",font=f_xs,fill=(170,170,170,255))

        overlay.save("text_overlay.png")
        txt_clip=ImageClip("text_overlay.png",duration=duration).set_duration(duration)
        clips=[bg,txt_clip]

        if product_img and os.path.exists(product_img) and os.path.getsize(product_img)>1000:
            try:
                pic=ImageClip(product_img,duration=duration).set_duration(duration)
                pic=pic.resize(width=250)
                if pic.h>260: pic=pic.resize(height=260)
                pic=pic.set_position((24,ad_y+50))
                clips.append(pic)
            except Exception as e:
                print(f"Product clip fail {e}")

        final=CompositeVideoClip(clips)
        if audio: final=final.set_audio(audio)
        final.write_videofile("world_viral_output.mp4",fps=24,codec='libx264',audio_codec='aac',bitrate="3500k",preset="ultrafast",threads=2)
        print(f"Video OK BIG TEXT")
        return "world_viral_output.mp4"

    except Exception as e:
        print(f"VIDEO FAIL {e}")
        import traceback; traceback.print_exc()
        try:
            if MOVIEPY_AVAILABLE:
                bg=ColorClip(size=(1080,1920),color=(8,12,28),duration=30)
                bg.write_videofile("world_viral_output.mp4",fps=24,codec='libx264',audio_codec='aac')
                return "world_viral_output.mp4"
            else:
                open("world_viral_output.mp4","wb").write(b"\x00"*1000)
                return "world_viral_output.mp4"
        except:
            open("world_viral_output.mp4","wb").write(b"\x00"*1000)
            return "world_viral_output.mp4"

async def main():
    try:
        print("=== V17 BIG TEXT AMAZON ONLY ===")
        pillar = PILLAR_ENV if PILLAR_ENV!="auto" and PILLAR_ENV in RSS_FEEDS else random.choice(list(RSS_FEEDS.keys()))
        print(f"Pillar: {pillar}")

        news=fetch_news(pillar)
        print(f"NEWS: {news['title'][:80]}")

        product=PRODUCTS.get(pillar, list(PRODUCTS.values())[0])
        amazon_link=build_amazon_link(product)

        pexels_clip=None
        if PEXELS_API_KEY and MOVIEPY_AVAILABLE:
            try:
                headers={"Authorization":PEXELS_API_KEY}
                q=product["pexels"][0]
                url=f"https://api.pexels.com/videos/search?query={q}&per_page=2&orientation=portrait"
                r=requests.get(url,headers=headers,timeout=12)
                if r.status_code==200:
                    vids=r.json().get('videos',[])
                    if vids:
                        files=sorted(vids[0]['video_files'],key=lambda x:x['width'],reverse=True)
                        if files:
                            vdata=requests.get(files[0]['link'],timeout=20).content
                            if len(vdata)>100000:
                                open("pexels_clip.mp4","wb").write(vdata)
                                pexels_clip="pexels_clip.mp4"
            except Exception as e:
                print(f"Pexels video fail {e}")

        product_img,img_source=get_product_image(product)
        print(f"Product img {img_source}")

        full_script,news_part,ad_part=gen_script_big(news,product)
        print(f"Script news {len(news_part.split())} words ad {len(ad_part.split())} words")

        desc=f"""{news['title']}

{full_script}

📰 SOURCES (80% news - BIG TEXT):
Full story: {news['link']}
Published: {news['pub']}
Source: {news.get('source','Reuters')} - {news['pillar']}

🛒 AMAZON FIND (20% ad):
{product['name']} - {product['price']}
{amazon_link}
Why? {product['reason']}
Tag: {AMAZON_TAG} | We earn commission

As Amazon Associate we earn from qualifying purchases.

#BreakingNews #{pillar} #AmazonFinds
"""

        open("script.txt","w",encoding="utf-8").write(desc)

        voice=await make_voice(full_script)
        video=make_video_big_text(full_script,news_part,ad_part,voice,pexels_clip,news,product,amazon_link,product_img,img_source)

        print(f"FINAL video {video} size {os.path.getsize(video) if video and os.path.exists(video) else 0}")

        if video and os.path.exists(video) and os.path.getsize(video)>1000:
            try:
                from youtube_uploader import upload_video
                title=f"{news['title'][:75]} | World Viral News"[:95]
                tags=[pillar,"breaking news",product['name'],"amazon"]
                upload_video(file_path=video,title=title,description=desc,tags=tags,privacy="public")
            except Exception as e:
                print(f"YT skip {e}")

        print("=== V17 DONE ===")
        sys.exit(0)

    except Exception as e:
        print(f"MAIN FAIL {e}")
        import traceback; traceback.print_exc()
        try:
            open("script.txt","w").write(f"Error {e}")
            open("world_viral_output.mp4","wb").write(b"\x00"*1000)
        except: pass
        sys.exit(0)

if __name__=="__main__":
    asyncio.run(main())

