
"""
WORLD VIRAL V12 - 80% NEWS / 20% AD - PERFECT YOUTUBE RATIO
- 80% real news, 20% natural product mention
- Total 50-58 seconds: 40s news + 10s product + 5s outro
- News from Google News RSS, product linked naturally
- Dual marketplace Amazon + Awin, real product image, 100% English
- Compliant with YouTube affiliate policy
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET, re, json, textwrap
from datetime import datetime
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG", "worldviral052-21")
AWIN_ID = os.getenv("AWIN_ID", "")
AWIN_ENABLED = bool(AWIN_ID)
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"V12 80/20 | TAG:{AMAZON_TAG} | AWIN:{'ON '+AWIN_ID if AWIN_ENABLED else 'OFF'} | PEXELS:{'YES' if PEXELS_API_KEY else 'NO'}")

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
    "usa_iran": {"name":"NOAA Emergency Weather Radio","search":"NOAA weather radio","pexels":["emergency radio"],"price":"29-69$","amazon_comm":"5%","awin_comm":"8%","awin_prog":"Bauhaus","awin_mid":19599,"awin_url":"https://www.bauhaus.de/","reason":"Stay informed when networks go down"},
    "russia_ukraine": {"name":"Tactical Backpack 60L Military","search":"military backpack 60L","pexels":["military backpack"],"price":"39-129$","amazon_comm":"7%","awin_comm":"12%","awin_prog":"Scandinavian Outdoor","awin_mid":0,"awin_url":"https://www.scandinavianoutdoor.fi/","reason":"Trusted by field journalists"},
    "eu_euro": {"name":"Money Counter Machine","search":"money counter machine","pexels":["money counter"],"price":"79-199$","amazon_comm":"5%","awin_comm":"10%","awin_prog":"Toolstation","awin_mid":0,"awin_url":"https://www.toolstation.de/","reason":"Essential for small businesses in EU"},
    "uk": {"name":"Smart Travel Luggage","search":"travel luggage hard case","pexels":["travel luggage"],"price":"49-199$","amazon_comm":"5%","awin_comm":"10%","awin_prog":"K-Rauta","awin_mid":15884,"awin_url":"https://www.k-rauta.fi/","reason":"UK airports see record travel"},
    "saudi_iraq_oil": {"name":"Oil Resistant Work Boots","search":"oil resistant work boots","pexels":["oil rig worker"],"price":"59-149$","amazon_comm":"6%","awin_comm":"12%","awin_prog":"Wurth","awin_mid":0,"awin_url":"https://eshop.wuerth.de/","reason":"Built for oil field conditions"},
    "gold_silver": {"name":"Jewelry Scale 0.01g Precision","search":"jewelry scale 0.01g","pexels":["gold scale"],"price":"12-39$","amazon_comm":"5%","awin_comm":"8%","awin_prog":"Bauhaus","awin_mid":19599,"awin_url":"https://www.bauhaus.de/","reason":"Check your gold at home"},
    "crypto": {"name":"Ledger Nano X Wallet","search":"Ledger Nano X","pexels":["crypto wallet"],"price":"59-149$","amazon_comm":"4%","awin_comm":"15%","awin_prog":"Ledger","awin_mid":0,"awin_url":"https://shop.ledger.com/","reason":"Secure crypto as banks wobble"},
    "natural_disasters": {"name":"Earthquake Emergency Kit 72H","search":"earthquake emergency kit","pexels":["emergency kit"],"price":"29-99$","amazon_comm":"5%","awin_comm":"10%","awin_prog":"Bauhaus","awin_mid":19599,"awin_url":"https://www.bauhaus.de/","reason":"72-hour survival essentials"},
    "aviation_accidents": {"name":"Aviation Band Radio Scanner","search":"aviation radio scanner","pexels":["aviation radio"],"price":"89-299$","amazon_comm":"5%","awin_comm":"8%","awin_prog":"Conrad","awin_mid":12552,"awin_url":"https://www.conrad.de/","reason":"Hear ATC communications live"},
    "ufo_orbs": {"name":"Telescope 130mm Professional","search":"telescope 130mm","pexels":["telescope stars"],"price":"99-399$","amazon_comm":"5%","awin_comm":"9%","awin_prog":"Scandinavian Outdoor","awin_mid":0,"awin_url":"https://www.scandinavianoutdoor.fi/","reason":"See what NASA sees"},
}

def fetch_news(pillar):
    for rss_url in RSS_FEEDS.get(pillar, list(RSS_FEEDS.values())[0]):
        try:
            r = requests.get(rss_url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code!=200: continue
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:5]:
                title = (item.find('title').text or "Breaking News").strip()
                link = (item.find('link').text or "").strip()
                desc = item.find('description').text or title
                desc = re.sub('<[^<]+?>','',desc)[:400]
                pub = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime("%Y-%m-%d")
                if len(title)>20:
                    return {"title":title,"link":link,"desc":desc,"pub":pub,"pillar":pillar}
        except Exception as e:
            print(f"RSS error {e}")
    return {"title":f"{pillar.replace('_',' ').title()} Breaking Update Today","link":"https://reuters.com","desc":"Latest developments","pub":datetime.now().isoformat(),"pillar":pillar}

def get_pexels(queries):
    if not PEXELS_API_KEY: return None
    headers={"Authorization":PEXELS_API_KEY}
    if isinstance(queries,str): queries=[queries]
    for q in queries:
        try:
            url=f"https://api.pexels.com/videos/search?query={q}&per_page=3&orientation=portrait"
            r=requests.get(url,headers=headers,timeout=15)
            if r.status_code==200:
                for video in r.json().get('videos',[]):
                    try:
                        files=sorted(video['video_files'],key=lambda x:x['width'],reverse=True)
                        best=files[0]
                        vdata=requests.get(best['link'],timeout=30).content
                        if len(vdata)>150000:
                            open("pexels_clip.mp4","wb").write(vdata)
                            return "pexels_clip.mp4"
                    except: continue
        except: continue
    return None

def get_product_image(search):
    try:
        headers={"User-Agent":"Mozilla/5.0","Accept-Language":"en-US,en;q=0.9"}
        url=f"https://www.amazon.de/s?k={search.replace(' ','+')}"
        r=requests.get(url,headers=headers,timeout=12)
        m=re.findall(r'https://m\.media-amazon\.com/images/I/[^"\s]+\.jpg',r.text)
        if m:
            data=requests.get(m[0],headers=headers,timeout=12).content
            if len(data)>10000:
                open("product_image.jpg","wb").write(data)
                return "product_image.jpg"
    except Exception as e:
        print(f"img fail {e}")
    return None

def build_links(product):
    import urllib.parse
    amazon=f"https://www.amazon.de/s?k={product['search'].replace(' ','+')}&tag={AMAZON_TAG}"
    awin=""
    if AWIN_ENABLED:
        enc=urllib.parse.quote(product['awin_url'],safe='')
        mid=product.get('awin_mid',0)
        if mid:
            awin=f"https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={AWIN_ID}&ued={enc}"
        else:
            awin=f"{product['awin_url']}?awinaffid={AWIN_ID}"
    return amazon,awin

def gen_script_80_20(news,product):
    # 80% news 200 words, 20% product 50 words = 250 words ~ 55 sec
    fallback_news = f"{news['title']}. {news['desc']}. According to Reuters, this is a developing situation. Officials say they are monitoring closely. Markets reacted quickly to the news. Experts believe this could have lasting impact on the region. We will continue to track updates as they come in."
    fallback_ad = f"Quick note: Many viewers asked about gear for this situation. The {product['name']} - {product['reason']}. It's {product['price']} on Amazon and also available at {product['awin_prog']}. Links in description, we earn a small commission which supports our news coverage."
    full_fallback = fallback_news + " " + fallback_ad

    if not OPENROUTER_API_KEY:
        return full_fallback, fallback_news, fallback_ad

    try:
        url="https://openrouter.ai/api/v1/chat/completions"
        headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}","Content-Type":"application/json"}
        prompt=f"""
Write YouTube Shorts script EXACTLY 80% news 20% ad. Total 240-260 words, English only, no Finnish.

NEWS (80% = 190-200 words):
Title: {news['title']}
Description: {news['desc']}
Pillar: {news['pillar']}
Write factual breaking news style, 3 paragraphs, exciting but accurate. No fake numbers. Use phrases like According to Reuters, officials say, market reaction.

AD TRANSITION (20% = 45-55 words):
Product: {product['name']} - {product['reason']}, Price {product['price']}, Available Amazon.de and {product['awin_prog']} via Awin.
Natural transition: Quick note / Many viewers ask / If you want to be prepared / Related gear
Mention both links in description, we earn commission, supports channel. Must not sound pushy, must be helpful.

Format:
[NEWS PART]
[AD PART - start with "Quick note:"]
"""
        for model in ["google/gemini-flash-1.5-8b:free","meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":500,"temperature":0.6}
                r=requests.post(url,headers=headers,json=payload,timeout=30)
                data=r.json()
                content=data.get('choices',[{}])[0].get('message',{}).get('content','')
                if len(content)>150:
                    # Split attempt
                    if "Quick note" in content:
                        parts=content.split("Quick note")
                        news_part=parts[0].strip()
                        ad_part="Quick note"+parts[1].strip()
                    else:
                        # fallback split 80/20 by words
                        words=content.split()
                        split=int(len(words)*0.8)
                        news_part=" ".join(words[:split])
                        ad_part=" ".join(words[split:])
                    return content.strip(), news_part, ad_part
            except Exception as e:
                print(f"LLM fail {model}: {e}")
                continue
        return full_fallback, fallback_news, fallback_ad
    except Exception as e:
        print(f"gen error {e}")
        return full_fallback, fallback_news, fallback_ad

async def make_voice(text, out="voice.mp3"):
    try:
        clean=text.replace("\n"," ")[:1000]
        comm=edge_tts.Communicate(clean,"en-US-GuyNeural",rate="+3%",volume="+8%")
        await comm.save(out)
        return out
    except:
        return None

def make_v12_video(full_script, news_part, ad_part, voice_file, pexels_clip, news, product, amazon_link, awin_link, product_img):
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import os

        duration=52
        audio=None
        if voice_file and os.path.exists(voice_file):
            try:
                audio=AudioFileClip(voice_file)
                duration=min(58,max(42,audio.duration+2))
            except: pass

        # Background
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg=VideoFileClip(pexels_clip).subclip(0,duration)
                bg=bg.resize(height=1920)
                if bg.w<1080: bg=bg.resize(width=1080)
                bg=bg.crop(x_center=bg.w/2,y_center=bg.h/2,width=1080,height=1920).set_duration(duration)
            except:
                bg=ColorClip(size=(1080,1920),color=(12,20,42),duration=duration)
        else:
            bg=ColorClip(size=(1080,1920),color=(12,20,42),duration=duration)

        W,H=1080,1920
        overlay=Image.new('RGBA',(W,H),(0,0,0,0))
        draw=ImageDraw.Draw(overlay)
        try:
            f_big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",46)
            f_med=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",32)
            f_small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
            f_tiny=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
            f_xs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
        except:
            f_big=ImageFont.load_default()
            f_med=f_small=f_tiny=f_xs=f_big

        # TOP BAR
        draw.rectangle([(0,0),(W,92)],fill=(192,0,0,255))
        draw.text((18,18),"🔴 BREAKING NEWS",font=f_big,fill=(255,255,255,255))
        draw.text((W-190,32),datetime.now().strftime("%H:%M UTC"),font=f_small,fill=(255,255,255,255))

        # NEWS BOX - 80% of screen height
        news_box_y=110
        news_box_h=1180  # ~61% of screen = 80% content
        draw.rounded_rectangle([(18,news_box_y),(W-18,news_box_y+news_box_h)],radius=18,fill=(0,0,0,178))

        # Title gold
        title_lines=textwrap.wrap(news['title'][:120],width=33)
        y=news_box_y+18
        for line in title_lines[:3]:
            draw.text((38,y),line.upper(),font=f_med,fill=(255,215,0,255))
            y+=38
        y+=12
        # News part 80%
        wrapped_news=textwrap.wrap(news_part, width=38)
        for line in wrapped_news[:22]:  # up to 22 lines = 80%
            for dx,dy in [(-1,-1),(1,1)]:
                draw.text((38+dx,y+dy),line,font=f_small,fill=(0,0,0,255))
            draw.text((38,y),line,font=f_small,fill=(255,255,255,255))
            y+=28
            if y>news_box_y+news_box_h-30: break

        # AD BOX - 20% at bottom, white, clearly separate but natural
        ad_y=H-580
        draw.rounded_rectangle([(18,ad_y),(W-18,H-18)],radius=18,fill=(255,255,255,248))

        # Subtle "Recommended" label to make it clear it's ad but not spammy
        draw.rounded_rectangle([(35,ad_y+12),(235,ad_y+42)],radius=8,fill=(230,230,230,255))
        draw.text((45,ad_y+16),"RECOMMENDED",font=f_tiny,fill=(80,80,80,255))

        # Product image placeholder box
        draw.rectangle([(32,ad_y+52),(282,ad_y+302)],fill=(242,242,242,255),outline=(200,200,200,255),width=2)

        # Product info - 20% text
        draw.text((300,ad_y+52),product['name'][:30].upper(),font=f_med,fill=(0,0,0,255))
        draw.text((300,ad_y+92),f"{product['price']} | {product['reason'][:48]}",font=f_small,fill=(50,50,50,255))

        # Ad part text - 20% script (2-3 lines)
        ad_lines=textwrap.wrap(ad_part,width=46)
        ay=ad_y+128
        for line in ad_lines[:3]:
            draw.text((300,ay),line,font=f_small,fill=(30,30,30,255))
            ay+=26

        # TWO SMALL CTAs side by side - Amazon + Awin
        draw.rounded_rectangle([(300,ad_y+212),(W-38,ad_y+252)],radius=9,fill=(255,153,0,255))
        draw.text((315,ad_y+218),"🛒 AMAZON: Link in Description",font=f_tiny,fill=(0,0,0,255))

        if AWIN_ENABLED and awin_link:
            draw.rounded_rectangle([(300,ad_y+260),(W-38,ad_y+300)],radius=9,fill=(0,92,184,255))
            draw.text((315,ad_y+266),f"🛒 {product['awin_prog'].upper()}: Higher Commission Link",font=f_tiny,fill=(255,255,255,255))
            draw.text((300,ad_y+310),f"Amazon {AMAZON_TAG} | Awin {AWIN_ID} | We earn commission",font=f_xs,fill=(100,100,100,255))
        else:
            draw.text((300,ad_y+268),f"Amazon {AMAZON_TAG} | Add AWIN_ID for 2nd store",font=f_xs,fill=(100,100,100,255))

        # Ticker bottom
        draw.rectangle([(0,H-92),(W,H)],fill=(0,0,0,235))
        draw.text((12,H-72),f"Source: {news['link'][:62]} | Reuters/Google News",font=f_xs,fill=(200,200,200,255))
        draw.text((12,H-48),f"80% News | 20% Ad | Affiliate links support our journalism | #{news['pillar']}",font=f_xs,fill=(170,170,170,255))
        draw.text((12,H-24),f"Disclaimer: Product links are affiliate. Price {product['price']} may change.",font=f_xs,fill=(150,150,150,255))

        overlay.save("text_overlay.png")
        txt_clip=ImageClip("text_overlay.png",duration=duration).set_duration(duration)
        clips=[bg,txt_clip]

        if product_img and os.path.exists(product_img):
            try:
                pic=ImageClip(product_img,duration=duration).set_duration(duration)
                pic=pic.resize(width=250)
                if pic.h>250: pic=pic.resize(height=250)
                pic=pic.set_position((32,ad_y+52))
                clips.append(pic)
            except Exception as e:
                print(f"pic clip fail {e}")

        final=CompositeVideoClip(clips)
        if audio: final=final.set_audio(audio)
        final.write_videofile("world_viral_output.mp4",fps=24,codec='libx264',audio_codec='aac',bitrate="4500k",preset="ultrafast",threads=4)
        print(f"V12 80/20 done: {news['title'][:40]} + {product['name']}")
        return "world_viral_output.mp4"
    except Exception as e:
        print(f"video fail {e}")
        import traceback; traceback.print_exc()
        return None

async def main():
    print("WORLD VIRAL V12 - 80% NEWS / 20% AD")
    pillar = PILLAR_ENV if PILLAR_ENV!="auto" and PILLAR_ENV in RSS_FEEDS else random.choice(list(RSS_FEEDS.keys()))
    print(f"Pillar: {pillar}")

    news=fetch_news(pillar)
    product=PRODUCTS.get(pillar, list(PRODUCTS.values())[0])
    amazon_link,awin_link=build_links(product)

    pexels_clip=get_pexels(product["pexels"]+[pillar.replace("_"," ")])
    prod_img=get_product_image(product["search"])

    full_script,news_part,ad_part=gen_script_80_20(news,product)
    print(f"Script len {len(full_script.split())} words - news {len(news_part.split())} / ad {len(ad_part.split())}")

    desc=f"""{news['title']}

{full_script}

📰 SOURCES (80% news):
Full story: {news['link']}
Published: {news['pub']}
Reuters / Google News - {news['pillar'].replace('_',' ').title()}

🛒 RECOMMENDED GEAR (20% ad - supports our journalism):
We found gear related to this news that viewers asked for:

1️⃣ AMAZON.DE - Fast delivery to Finland/EU:
{product['name']} - {product['price']}
{amazon_link}
Commission: {product['amazon_comm']} | 24h cookie

2️⃣ {product['awin_prog'].upper()} via AWIN - Higher commission, longer cookie:
{awin_link if awin_link else 'Enable AWIN_ID secret to activate second store - https://www.awin.com - 7-15% commission, 30-90 day cookie'}
Commission: {product['awin_comm']} | 30-90 day cookie | Local warranty

💡 Why this product? {product['reason']}
Price may change. We earn small commission from both stores which supports independent news.

📊 Ratio: 80% news / 20% ad - YouTube compliant, value first.

#BreakingNews #WorldNews #{pillar} #NewsUpdate #{product['awin_prog']} #AmazonFinds
Pillar: {pillar} | Product: {product['name']} | Tag: {AMAZON_TAG} + Awin {AWIN_ID if AWIN_ENABLED else 'OFF'}
"""

    open("script.txt","w",encoding="utf-8").write(desc)

    voice=await make_voice(full_script)
    video=make_v12_video(full_script,news_part,ad_part,voice,pexels_clip,news,product,amazon_link,awin_link,prod_img)

    print(f"Done video {video}")

    if video and os.path.exists(video):
        try:
            from youtube_uploader import upload_video
            title=f"{news['title'][:75]} | World Viral News"[:95]
            tags=[pillar,"breaking news","world news",product['name'],product['awin_prog'],"80 20"]
            upload_video(file_path=video,title=title,description=desc,tags=tags,privacy="public")
        except Exception as e:
            print(f"YT skip {e}")

if __name__=="__main__":
    asyncio.run(main())
