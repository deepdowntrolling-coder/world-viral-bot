
"""
WORLD VIRAL V9 SALES - 100 KATEGORIAN AFFILIATE BOT
- Arpoo 100 kategoriasta (Amazon Best + Awin + 26 pilaria + DIY)
- Hakee REAL tuotteen + REAL videon + affiliate linkin
- Myyntigrafiikat: DEAL banneri + hinta + CTA
- Automaattinen tulo: Amazon.de + Awin -> IBAN
"""
import os, random, requests, asyncio, xml.etree.ElementTree as ET, re, json
from datetime import datetime
import edge_tts

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG", "worldviral052-21")  # Amazon.de tag
AWIN_ID = os.getenv("AWIN_ID", "")
PILLAR_ENV = os.getenv("PILLAR", "auto")

print(f"PEXELS: {'SET' if PEXELS_API_KEY else 'NOT SET'} | AMAZON_TAG: {AMAZON_TAG}")

# TOP 100 KATEGORIA - Myyvimmät Amazon + Awin + Pilarit + DIY
TOP100 = [
    # DIY & KORJAUS 1-20
    {"id": "diy_drill", "name": "Akkuporakone 18V", "keywords": ["cordless drill", "akkuporakone"], "pexels": ["drill construction","power tools workshop","construction worker drill"], "amazon_search": "cordless drill 18V", "awin": "Bauhaus", "commission": "7%", "price_range": "89-199€"},
    {"id": "diy_sealant", "name": "Tiiviste & Liimat", "keywords": ["sealant adhesive"], "pexels": ["construction sealant","home repair","caulking gun"], "amazon_search": "silicone sealant", "awin": "K-Rauta", "commission": "8%", "price_range": "5-25€"},
    {"id": "diy_saw", "name": "Saha & Hiomakone", "keywords": ["circular saw"], "pexels": ["circular saw cutting","woodworking saw","carpenter work"], "amazon_search": "circular saw", "awin": "Toolstation", "commission": "6%", "price_range": "99-299€"},
    {"id": "diy_plumbing", "name": "Putkityökalut", "keywords": ["plumbing tools"], "pexels": ["plumber work","pipe wrench","plumbing repair"], "amazon_search": "plumbing tools", "awin": "Ahlsell", "commission": "7%", "price_range": "19-99€"},
    {"id": "auto_obd2", "name": "OBD2 Autolukija", "keywords": ["OBD2 scanner"], "pexels": ["car mechanic diagnostic","auto repair garage","car engine"], "amazon_search": "OBD2 scanner", "awin": "Autodoc", "commission": "10%", "price_range": "25-89€"},
    {"id": "bike_repair", "name": "Pyörän Korjaussarja", "keywords": ["bike repair kit"], "pexels": ["bicycle repair","bike mechanic","cycling tools"], "amazon_search": "bike repair kit", "awin": "Bike24", "commission": "8%", "price_range": "15-59€"},
    {"id": "mocc_axe", "name": "Kirves & Moottorisaha", "keywords": ["axe chainsaw"], "pexels": ["axe wood chopping","chainsaw cutting tree","forest lumberjack"], "amazon_search": "axe bushcraft", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "29-399€"},
    {"id": "welding", "name": "Hitsauskone", "keywords": ["welding machine"], "pexels": ["welding sparks","welder work","metal welding"], "amazon_search": "welding machine", "awin": "Wurth", "commission": "12%", "price_range": "149-599€"},
    {"id": "painting", "name": "Maaliruisku", "keywords": ["paint sprayer"], "pexels": ["painting wall","painter work","spray paint"], "amazon_search": "paint sprayer", "awin": "Bauhaus", "commission": "7%", "price_range": "49-199€"},
    {"id": "safety_gear", "name": "Turvakypärä & Hanskat", "keywords": ["safety helmet gloves"], "pexels": ["construction safety helmet","safety gloves work","construction worker"], "amazon_search": "safety helmet construction", "awin": "Safety", "commission": "8%", "price_range": "9-49€"},
    {"id": "laser_measure", "name": "Laser Etäisyysmittari", "keywords": ["laser measure"], "pexels": ["laser measure tool","construction measurement","laser level"], "amazon_search": "laser distance measure", "awin": "Toolstation", "commission": "6%", "price_range": "29-99€"},
    {"id": "screws_bulk", "name": "Ruuvit Bulk 1000kpl", "keywords": ["screws bulk"], "pexels": ["screws hardware","toolbox screws","construction screws"], "amazon_search": "screws assortment kit", "awin": "Bauhaus", "commission": "7%", "price_range": "12-39€"},
    {"id": "electrical", "name": "Sähköasennus Tarvikkeet", "keywords": ["electrical wire"], "pexels": ["electrician work","electrical wiring","electrical tools"], "amazon_search": "electrical wire connectors", "awin": "Ahlsell", "commission": "7%", "price_range": "8-59€"},
    {"id": "wood_chisel", "name": "Talttasarja Puutyöt", "keywords": ["wood chisel set"], "pexels": ["wood carving chisel","woodworking tools","carpenter chisel"], "amazon_search": "wood chisel set", "awin": "Bauhaus", "commission": "7%", "price_range": "19-79€"},
    {"id": "diy_book", "name": "DIY Korjausopas Kirja", "keywords": ["diy repair book"], "pexels": ["diy book manual","home repair book","toolbox book"], "amazon_search": "diy home repair book", "awin": "Amazon", "commission": "5%", "price_range": "15-35€"},
    {"id": "pressure_washer", "name": "Painepesuri Kärcher", "keywords": ["pressure washer"], "pexels": ["pressure washer cleaning","car wash pressure","cleaning driveway"], "amazon_search": "Karcher pressure washer", "awin": "Karcher", "commission": "7%", "price_range": "99-399€"},
    {"id": "ladder", "name": "Tikkaat Teleskooppi", "keywords": ["telescopic ladder"], "pexels": ["ladder construction","worker on ladder","telescopic ladder"], "amazon_search": "telescopic ladder", "awin": "Bauhaus", "commission": "7%", "price_range": "59-199€"},
    {"id": "compressor", "name": "Kompressori Ilma", "keywords": ["air compressor"], "pexels": ["air compressor workshop","pneumatic tools","garage compressor"], "amazon_search": "air compressor", "awin": "Wurth", "commission": "12%", "price_range": "99-499€"},
    {"id": "battery_18v", "name": "Akkusarja 18V", "keywords": ["18V battery"], "pexels": ["battery power tools","drill battery","tool battery"], "amazon_search": "18V battery Makita", "awin": "Toolstation", "commission": "6%", "price_range": "39-99€"},
    {"id": "solar_kit", "name": "Aurinkopaneeli DIY Kit", "keywords": ["solar panel kit"], "pexels": ["solar panel roof","solar installation","solar energy"], "amazon_search": "solar panel kit 100W", "awin": "Solar", "commission": "10%", "price_range": "89-599€"},

    # KOTI & ARKI 21-40
    {"id": "water_filter", "name": "Veden Suodatin & Kahvikone", "keywords": ["water filter coffee"], "pexels": ["water filter","coffee machine brewing","kitchen water"], "amazon_search": "water filter", "awin": "Amazon", "commission": "5%", "price_range": "19-299€"},
    {"id": "air_fryer", "name": "Air Fryer 5L", "keywords": ["air fryer"], "pexels": ["air fryer cooking","kitchen air fryer","cooking healthy"], "amazon_search": "air fryer", "awin": "Amazon", "commission": "5%", "price_range": "59-149€"},
    {"id": "ring_doorbell", "name": "Ring Ovikello Kamera", "keywords": ["ring doorbell"], "pexels": ["doorbell camera","smart home security","ring doorbell"], "amazon_search": "Ring Video Doorbell", "awin": "Amazon", "commission": "5%", "price_range": "59-199€"},
    {"id": "vitamins", "name": "Vitamiinit & Lisäravinteet", "keywords": ["vitamins supplements"], "pexels": ["vitamins pills","supplements health","healthy vitamins"], "amazon_search": "vitamins D3", "awin": "Health", "commission": "12%", "price_range": "9-39€"},
    {"id": "pet_food", "name": "Koiran Ruoka Premium", "keywords": ["dog food premium"], "pexels": ["dog eating food","pet dog food","dog bowl"], "amazon_search": "dog food premium", "awin": "Pet", "commission": "15%", "price_range": "19-69€"},
    {"id": "kindle", "name": "Kindle & Fire TV Stick", "keywords": ["kindle fire tv"], "pexels": ["kindle reading","fire tv remote","amazon kindle"], "amazon_search": "Kindle Paperwhite", "awin": "Amazon", "commission": "5%", "price_range": "39-149€"},
    {"id": "vacuum_shark", "name": "Shark Pölynimuri", "keywords": ["shark vacuum"], "pexels": ["vacuum cleaning home","shark vacuum","cleaning floor"], "amazon_search": "Shark vacuum", "awin": "Amazon", "commission": "5%", "price_range": "99-399€"},
    {"id": "workwear", "name": "Työvaatteet Outdoor", "keywords": ["workwear outdoor"], "pexels": ["workwear construction","outdoor work clothes","worker jacket"], "amazon_search": "workwear jacket", "awin": "Engelbert Strauss", "commission": "10%", "price_range": "29-129€"},
    {"id": "smart_plug", "name": "Smart Plug & Echo Show", "keywords": ["smart plug echo"], "pexels": ["smart plug home","echo show amazon","smart home"], "amazon_search": "Amazon Smart Plug", "awin": "Amazon", "commission": "5%", "price_range": "19-129€"},
    {"id": "powerbank", "name": "Anker Power Bank 20000mAh", "keywords": ["anker powerbank"], "pexels": ["power bank charging","anker powerbank","phone charging"], "amazon_search": "Anker Power Bank", "awin": "Amazon", "commission": "5%", "price_range": "19-59€"},
    {"id": "bose_earbuds", "name": "Bose Kuulokkeet", "keywords": ["bose earbuds"], "pexels": ["bose headphones","earbuds music","headphones listening"], "amazon_search": "Bose QuietComfort earbuds", "awin": "Bose", "commission": "8%", "price_range": "79-299€"},
    {"id": "pillows", "name": "Casper Tyyny", "keywords": ["casper pillow"], "pexels": ["pillow bed sleeping","bedroom pillow","sleep pillow"], "amazon_search": "memory foam pillow", "awin": "Amazon", "commission": "5%", "price_range": "19-69€"},
    {"id": "water_bottle", "name": "Juomapullo Teräs", "keywords": ["steel water bottle"], "pexels": ["water bottle steel","drinking bottle","gym water bottle"], "amazon_search": "steel water bottle", "awin": "Amazon", "commission": "5%", "price_range": "9-29€"},
    {"id": "home_fitness", "name": "Kuntolaite - Assault Bike", "keywords": ["assault bike fitness"], "pexels": ["assault bike gym","fitness workout bike","gym training"], "amazon_search": "assault bike", "awin": "Assault Fitness", "commission": "25%", "price_range": "599-2999€"},
    {"id": "bbq", "name": "Grilli & BBQ", "keywords": ["bbq grill"], "pexels": ["bbq grill cooking","barbecue grill","grill meat"], "amazon_search": "BBQ grill", "awin": "Grill", "commission": "10%", "price_range": "99-599€"},
    {"id": "led_bulb", "name": "LED Älylamppu", "keywords": ["led smart bulb"], "pexels": ["led bulb smart","smart lighting home","led light"], "amazon_search": "Philips Hue bulb", "awin": "Philips", "commission": "8%", "price_range": "9-49€"},
    {"id": "storage_box", "name": "Säilytyslaatikot", "keywords": ["storage box"], "pexels": ["storage boxes home","organizing home","storage organization"], "amazon_search": "storage boxes", "awin": "IKEA", "commission": "7%", "price_range": "9-49€"},
    {"id": "coffee_specialty", "name": "Erikoiskahvi Pavut", "keywords": ["specialty coffee beans"], "pexels": ["coffee beans roasting","specialty coffee","barista coffee"], "amazon_search": "specialty coffee beans", "awin": "Coffee", "commission": "10%", "price_range": "9-29€"},
    {"id": "cleaning_karcher", "name": "Kärcher Siivouskone", "keywords": ["karcher cleaner"], "pexels": ["karcher cleaning","steam cleaner","cleaning machine"], "amazon_search": "Karcher steam cleaner", "awin": "Karcher", "commission": "7%", "price_range": "99-399€"},
    {"id": "outdoor_jacket", "name": "Outdoor Takki", "keywords": ["outdoor jacket"], "pexels": ["outdoor jacket hiking","rain jacket outdoor","hiking jacket"], "amazon_search": "outdoor jacket waterproof", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "59-299€"},

    # KULTA / HOPEA / KRYPTO / RAHA 41-55
    {"id": "gold_capsule", "name": "Kultakapseli Säilytys", "keywords": ["gold coin capsule"], "pexels": ["gold bars closeup","gold coins money","gold storage"], "amazon_search": "gold coin capsule", "awin": "Nordic Gold", "commission": "12%", "price_range": "5-29€"},
    {"id": "silver_clean", "name": "Hopean Puhdistus", "keywords": ["silver cleaner"], "pexels": ["silver bars","silver coins","jewelry cleaning"], "amazon_search": "silver cleaner", "awin": "Nordic Gold", "commission": "12%", "price_range": "8-19€"},
    {"id": "gold_scale", "name": "Kultavaaka 0.01g", "keywords": ["gold scale 0.01g"], "pexels": ["gold scale weighing","jewelry scale","precision scale"], "amazon_search": "jewelry scale 0.01g", "awin": "Amazon", "commission": "5%", "price_range": "12-39€"},
    {"id": "ledger_wallet", "name": "Ledger Crypto Lompakko", "keywords": ["ledger wallet crypto"], "pexels": ["bitcoin cryptocurrency","crypto wallet hardware","blockchain technology"], "amazon_search": "Ledger Nano", "awin": "Ledger", "commission": "15%", "price_range": "59-149€"},
    {"id": "gold_detector", "name": "Metallinpaljastin Kulta", "keywords": ["gold detector metal"], "pexels": ["metal detector beach","gold detector","treasure hunting"], "amazon_search": "metal detector gold", "awin": "Amazon", "commission": "5%", "price_range": "89-599€"},
    {"id": "safe_box", "name": "Kassakaappi Pieni", "keywords": ["safe box small"], "pexels": ["safe box security","safe vault","money safe"], "amazon_search": "safe box small", "awin": "Burg Wachter", "commission": "9%", "price_range": "59-299€"},
    {"id": "investment_book", "name": "Sijoituskirja Kulta & Krypto", "keywords": ["investment book gold crypto"], "pexels": ["investment book reading","crypto book","finance book"], "amazon_search": "gold investment book", "awin": "Amazon", "commission": "5%", "price_range": "15-39€"},
    {"id": "cash_counter", "name": "Rahanlaskukone", "keywords": ["cash counter money"], "pexels": ["money counting machine","cash counter","bank money"], "amazon_search": "money counter", "awin": "Amazon", "commission": "5%", "price_range": "79-199€"},
    {"id": "money_belt", "name": "Rahavyö Matkalle", "keywords": ["money belt travel"], "pexels": ["money belt travel","travel security","passport money"], "amazon_search": "money belt travel", "awin": "Travel", "commission": "8%", "price_range": "9-29€"},
    {"id": "trading_monitor", "name": "Trading Näyttö 4K", "keywords": ["trading monitor 4k"], "pexels": ["trading monitors","stock trading desk","trading setup"], "amazon_search": "4K monitor", "awin": "Amazon", "commission": "5%", "price_range": "199-599€"},
    {"id": "faraday_bag", "name": "Faraday Bag Crypto", "keywords": ["faraday bag crypto"], "pexels": ["faraday bag security","crypto security","signal blocking bag"], "amazon_search": "faraday bag", "awin": "Amazon", "commission": "5%", "price_range": "15-39€"},
    {"id": "silver_jewelry_diy", "name": "Hopeakoru DIY Kit", "keywords": ["silver jewelry diy kit"], "pexels": ["jewelry making diy","silver jewelry craft","jewelry tools"], "amazon_search": "jewelry making kit silver", "awin": "Amazon", "commission": "5%", "price_range": "19-59€"},
    {"id": "euro_wallet", "name": "Euro Kolikko Lompakko", "keywords": ["euro coin wallet"], "pexels": ["euro money coins","euro wallet","money euro"], "amazon_search": "euro coin wallet", "awin": "Amazon", "commission": "5%", "price_range": "9-19€"},
    {"id": "blockchain_course", "name": "Blockchain Kurssi Online", "keywords": ["blockchain course"], "pexels": ["blockchain technology","crypto learning","online course"], "amazon_search": "blockchain book", "awin": "Udemy", "commission": "20%", "price_range": "19-99€"},
    {"id": "precious_metal_ira", "name": "Kulta IRA Opas USA", "keywords": ["gold ira guide"], "pexels": ["gold investment retirement","gold bars retirement","finance retirement"], "amazon_search": "gold IRA guide", "awin": "Finance", "commission": "15%", "price_range": "0-99€"},

    # SELVIYTYMINEN / ÖLJY / SOTA 56-75
    {"id": "earthquake_kit", "name": "Maanjäristys Ensiapupakkaus", "keywords": ["earthquake emergency kit"], "pexels": ["emergency kit survival","earthquake kit","survival backpack"], "amazon_search": "earthquake emergency kit", "awin": "Survival", "commission": "15%", "price_range": "29-99€"},
    {"id": "weather_radio", "name": "NOAA Sääradio", "keywords": ["NOAA weather radio"], "pexels": ["weather radio emergency","noaa radio","storm radio"], "amazon_search": "NOAA weather radio", "awin": "Amazon", "commission": "5%", "price_range": "25-69€"},
    {"id": "flood_pump", "name": "Tulvapumppu", "keywords": ["flood pump water"], "pexels": ["flood water pump","water pump flood","flooding house"], "amazon_search": "water pump flood", "awin": "Bauhaus", "commission": "7%", "price_range": "89-399€"},
    {"id": "volcano_mask", "name": "Tulivuori Hengityssuojain", "keywords": ["volcano mask respirator"], "pexels": ["volcano eruption lava","respirator mask","gas mask"], "amazon_search": "P100 respirator", "awin": "Safety", "commission": "8%", "price_range": "19-59€"},
    {"id": "oil_workwear", "name": "Öljy Työvaatteet", "keywords": ["oil workwear"], "pexels": ["oil refinery industry","oil rig worker","oil worker"], "amazon_search": "oil resistant work boots", "awin": "Engelbert Strauss", "commission": "10%", "price_range": "39-149€"},
    {"id": "oil_barrel_model", "name": "Öljytynnyri Malli Keräily", "keywords": ["oil barrel model"], "pexels": ["oil barrel","oil rig sea","oil industry"], "amazon_search": "oil barrel decor", "awin": "Amazon", "commission": "5%", "price_range": "19-59€"},
    {"id": "cargo_ship", "name": "Rahtilaiva Tarvikkeet", "keywords": ["cargo ship supplies"], "pexels": ["cargo ship ocean","container ship sea","ocean waves"], "amazon_search": "nautical decor", "awin": "Amazon", "commission": "5%", "price_range": "15-99€"},
    {"id": "military_backpack", "name": "Armeija Reppu 60L", "keywords": ["military backpack 60L"], "pexels": ["military army backpack","tactical backpack","army rucksack"], "amazon_search": "military backpack 60L", "awin": "Military", "commission": "12%", "price_range": "39-129€"},
    {"id": "un_medical", "name": "UN Kenttä Ensiapu", "keywords": ["field medical kit"], "pexels": ["military medical kit","first aid field","united nations medical"], "amazon_search": "military first aid kit", "awin": "Survival", "commission": "15%", "price_range": "29-99€"},
    {"id": "flight_radio", "name": "Lentokoneradio Scanner", "keywords": ["aviation scanner radio"], "pexels": ["airplane runway takeoff","air traffic control","aviation radio"], "amazon_search": "aviation radio scanner", "awin": "Amazon", "commission": "5%", "price_range": "89-299€"},
    {"id": "faa_guide", "name": "FAA Lentokirja", "keywords": ["FAA pilot book"], "pexels": ["pilot book aviation","flight manual","aviation book"], "amazon_search": "FAA pilot handbook", "awin": "Amazon", "commission": "5%", "price_range": "19-49€"},
    {"id": "emergency_light", "name": "Hälytysvalo Poliisi", "keywords": ["emergency light police"], "pexels": ["emergency lights police","police car lights","fire truck emergency"], "amazon_search": "emergency light bar", "awin": "Autodoc", "commission": "10%", "price_range": "29-199€"},
    {"id": "cctv_ring", "name": "Valvontakamera Ring", "keywords": ["ring security camera"], "pexels": ["security camera cctv","ring camera home","surveillance camera"], "amazon_search": "Ring security camera", "awin": "Ring", "commission": "8%", "price_range": "59-199€"},
    {"id": "travel_luggage", "name": "Matkalaukku Lukolla", "keywords": ["travel luggage lock"], "pexels": ["travel luggage airport","suitcase travel","luggage lock"], "amazon_search": "travel luggage", "awin": "Samsonite", "commission": "10%", "price_range": "49-199€"},
    {"id": "nautical_map", "name": "Merikartta & Kompassi", "keywords": ["nautical chart compass"], "pexels": ["nautical map compass","sailing compass","marine navigation"], "amazon_search": "nautical compass", "awin": "Amazon", "commission": "5%", "price_range": "19-59€"},
    {"id": "pet_survival", "name": "Lemmikki Selviytymispakkaus", "keywords": ["pet survival kit"], "pexels": ["pet emergency kit","dog survival","pet carrier"], "amazon_search": "pet emergency kit", "awin": "Pet", "commission": "15%", "price_range": "19-59€"},
    {"id": "camping_stove", "name": "Retkikeitin Kaasu", "keywords": ["camping stove gas"], "pexels": ["camping stove cooking","camp stove gas","outdoor cooking"], "amazon_search": "camping stove", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "29-99€"},
    {"id": "solar_powerbank", "name": "Aurinko Powerbank 30000mAh", "keywords": ["solar powerbank 30000"], "pexels": ["solar power bank","solar charger phone","power bank outdoor"], "amazon_search": "solar power bank", "awin": "Amazon", "commission": "5%", "price_range": "29-79€"},
    {"id": "storm_tent", "name": "Myrskyteltta 4 Henkilö", "keywords": ["storm tent 4 person"], "pexels": ["storm tent camping","tent wind storm","camping tent"], "amazon_search": "4 person tent waterproof", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "99-399€"},
    {"id": "water_filter_survival", "name": "Veden Puhdistin Selviytyminen", "keywords": ["water filter survival"], "pexels": ["water filter survival","life straw filter","survival water"], "amazon_search": "LifeStraw water filter", "awin": "Survival", "commission": "15%", "price_range": "15-59€"},

    # UFO / AVARUUS / LENTO 76-85
    {"id": "telescope", "name": "Teleskooppi 130mm", "keywords": ["telescope 130mm"], "pexels": ["telescope stars night","night sky telescope","astronomy telescope"], "amazon_search": "telescope 130mm", "awin": "Amazon", "commission": "5%", "price_range": "99-399€"},
    {"id": "star_map", "name": "Tähtikartta Juliste", "keywords": ["star map poster"], "pexels": ["star map night sky","milky way galaxy","constellation map"], "amazon_search": "star map poster", "awin": "Amazon", "commission": "5%", "price_range": "9-29€"},
    {"id": "aurora_camera", "name": "Revontuli Kamera Jalusta", "keywords": ["aurora camera tripod"], "pexels": ["northern lights aurora","aurora borealis camera","tripod camera night"], "amazon_search": "camera tripod", "awin": "Amazon", "commission": "5%", "price_range": "19-99€"},
    {"id": "ufo_book", "name": "UFO Kirja Top", "keywords": ["ufo book"], "pexels": ["ufo book reading","alien book","ufo document"], "amazon_search": "UFO book", "awin": "Amazon", "commission": "5%", "price_range": "15-35€"},
    {"id": "night_vision", "name": "Yökiikari Night Vision", "keywords": ["night vision binoculars"], "pexels": ["night vision goggles","night vision binoculars","night observation"], "amazon_search": "night vision binoculars", "awin": "Amazon", "commission": "5%", "price_range": "89-399€"},
    {"id": "drone_4k", "name": "Drone 4K Kamera", "keywords": ["drone 4k camera"], "pexels": ["drone flying 4k","drone aerial view","drone camera"], "amazon_search": "drone 4K", "awin": "DJI", "commission": "5%", "price_range": "199-999€"},
    {"id": "flight_sim", "name": "Flight Sim Ohjain", "keywords": ["flight sim joystick"], "pexels": ["flight simulator joystick","pilot simulator","flight sim"], "amazon_search": "flight simulator joystick", "awin": "Amazon", "commission": "5%", "price_range": "49-199€"},
    {"id": "astronaut_costume", "name": "Astronautti Puku", "keywords": ["astronaut costume"], "pexels": ["astronaut suit space","space costume","nasa astronaut"], "amazon_search": "astronaut costume", "awin": "Amazon", "commission": "5%", "price_range": "19-59€"},
    {"id": "meteorite", "name": "Meteoriitti Keräily", "keywords": ["meteorite collection"], "pexels": ["meteorite rock space","meteorite collection","space rock"], "amazon_search": "meteorite", "awin": "Amazon", "commission": "5%", "price_range": "19-199€"},
    {"id": "planetarium", "name": "Planetaario Projektori", "keywords": ["planetarium projector"], "pexels": ["planetarium stars projector","star projector bedroom","galaxy projector"], "amazon_search": "star projector", "awin": "Amazon", "commission": "5%", "price_range": "29-99€"},

    # MAAILMAN KULTTUURI & MATKAILU 86-100
    {"id": "london_souvenir", "name": "London Souvenir", "keywords": ["london souvenir"], "pexels": ["london city timelapse","big ben london","british flag"], "amazon_search": "London souvenir", "awin": "CheapOair Travel", "commission": "$15 flight", "price_range": "5-25€"},
    {"id": "berlin_beer", "name": "Saksa Olutlasi & Työkalut", "keywords": ["german beer glass tools"], "pexels": ["berlin city timelapse","german beer glass","berlin brandenburg gate"], "amazon_search": "German beer glass", "awin": "Bauhaus", "commission": "7%", "price_range": "9-39€"},
    {"id": "paris_perfume", "name": "Ranska Hajuvesi", "keywords": ["france perfume"], "pexels": ["paris eiffel tower","perfume france","paris city"], "amazon_search": "French perfume", "awin": "Perfume", "commission": "12%", "price_range": "29-99€"},
    {"id": "spain_fan", "name": "Espanja Fanituote", "keywords": ["spain fan"], "pexels": ["madrid city","spain flag","barcelona sagrada"], "amazon_search": "Spain fan", "awin": "Travel", "commission": "$15", "price_range": "9-29€"},
    {"id": "sweden_knife", "name": "Ruotsi Puukko Mora", "keywords": ["mora knife sweden"], "pexels": ["mora knife sweden","bushcraft knife","swedish knife"], "amazon_search": "Mora knife", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "19-59€"},
    {"id": "india_spice", "name": "Intia Mauste Setti", "keywords": ["india spice set"], "pexels": ["taj mahal india","india spices","indian spices"], "amazon_search": "Indian spice set", "awin": "Amazon", "commission": "5%", "price_range": "9-29€"},
    {"id": "china_gadget", "name": "Kiina Gadget Mini", "keywords": ["china gadget mini"], "pexels": ["beijing city timelapse","china gadget","shanghai skyline"], "amazon_search": "mini gadget", "awin": "Amazon", "commission": "5%", "price_range": "5-29€"},
    {"id": "japan_knife", "name": "Japani Veitsi Santoku", "keywords": ["japan knife santoku"], "pexels": ["tokyo city night","japanese knife santoku","japan cherry blossom"], "amazon_search": "Japanese knife Santoku", "awin": "Amazon", "commission": "5%", "price_range": "29-99€"},
    {"id": "australia_hat", "name": "Australia Hattu & Surf", "keywords": ["australia hat surf"], "pexels": ["sydney opera house","australia beach hat","surfboard australia"], "amazon_search": "Australia hat", "awin": "Travel", "commission": "$15", "price_range": "15-39€"},
    {"id": "mosque_decor", "name": "Moskeija Koriste", "keywords": ["mosque decor"], "pexels": ["mosque islamic interior","islamic decor","mosque lamp"], "amazon_search": "Islamic decor", "awin": "Amazon", "commission": "5%", "price_range": "9-49€"},
    {"id": "desert_tent", "name": "Aavikko Teltta", "keywords": ["desert tent"], "pexels": ["desert tent camping","desert sunset tent","bedouin tent"], "amazon_search": "desert tent", "awin": "Scandinavian Outdoor", "commission": "9%", "price_range": "99-299€"},
    {"id": "eu_flag", "name": "EU Lippu & Kartta", "keywords": ["eu flag map"], "pexels": ["european parliament flag","eu flag","europe map"], "amazon_search": "EU flag", "awin": "Amazon", "commission": "5%", "price_range": "9-19€"},
    {"id": "travel_package", "name": "Matkapaketti Loma", "keywords": ["travel package vacation"], "pexels": ["travel vacation package","beach vacation travel","hotel resort"], "amazon_search": "travel package", "awin": "CheapOair", "commission": "$25", "price_range": "299-1999€"},
    {"id": "flight_cheap", "name": "Halvat Lennot", "keywords": ["cheap flights"], "pexels": ["airplane sky flying","airport terminal travel","flight takeoff"], "amazon_search": "travel pillow", "awin": "CheapOair", "commission": "$15 flight", "price_range": "19-199€"},
    {"id": "hotel_booking", "name": "Hotelli Varaus", "keywords": ["hotel booking"], "pexels": ["hotel room luxury","hotel booking","resort hotel"], "amazon_search": "hotel slippers", "awin": "Booking.com Awin", "commission": "4% hotel", "price_range": "50-300€/night"},
]

def get_product_category():
    if PILLAR_ENV != "auto":
        # Etsi pillar mätsi
        for cat in TOP100:
            if PILLAR_ENV in cat["id"] or PILLAR_ENV == cat["id"].split("_")[0]:
                return cat
    return random.choice(TOP100)

def get_pexels_video(pexels_queries):
    if not PEXELS_API_KEY:
        return None
    if isinstance(pexels_queries, str):
        queries = [pexels_queries]
    else:
        queries = pexels_queries
    headers = {"Authorization": PEXELS_API_KEY}
    for query in queries:
        try:
            for orientation in ["portrait", "landscape"]:
                url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation={orientation}"
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    for video in r.json().get('videos', []):
                        try:
                            files = sorted(video['video_files'], key=lambda x: x['width'], reverse=True)
                            best = files[0]
                            vdata = requests.get(best['link'], timeout=35).content
                            if len(vdata) > 150000:
                                with open("pexels_clip.mp4","wb") as f:
                                    f.write(vdata)
                                print(f"Pexels OK: {query}")
                                return "pexels_clip.mp4"
                        except:
                            continue
        except Exception as e:
            print(f"Pexels fail {e}")
            continue
    return None

def generate_sales_script(category):
    """Myyntiskripti tuotteelle"""
    name = category["name"]
    price = category["price_range"]
    commission = category["commission"]
    
    fallback = f"VIRAL DEAL: {name}. Price {price}. This is Amazon best seller 2025. Top rated, thousands of reviews. Limited stock. Thousands sold this week. Get yours now before price goes up. Link in description. Commission {commission} supports channel."
    
    if not OPENROUTER_API_KEY:
        return fallback
    
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-viral-bot", "X-Title": "World Viral Sales"}
        prompt = f"Write 100-word viral sales script for YouTube Shorts. Product: {name}. Price: {price}. Keywords: {', '.join(category['keywords'])}. Make it exciting, urgent, with 3 benefits. End with Call to Action: Link in description. English. No hate, no fake claims."
        for model in ["google/gemini-flash-1.5-8b:free", "meta-llama/llama-3.1-8b-instruct:free"]:
            try:
                payload = {"model": model, "messages": [{"role":"user","content": prompt}], "max_tokens": 250, "temperature": 0.8}
                r = requests.post(url, headers=headers, json=payload, timeout=25)
                data = r.json()
                if "choices" in data and data["choices"][0].get("message", {}).get("content"):
                    content = data["choices"][0]["message"]["content"].strip()
                    if len(content) > 50:
                        return content
            except:
                continue
        return fallback
    except:
        return fallback

def build_affiliate_link(category):
    """Rakentaa affiliate linkin"""
    amazon_search = category["amazon_search"].replace(" ", "+")
    # Amazon.de haku linkki tagilla
    amazon_link = f"https://www.amazon.de/s?k={amazon_search}&tag={AMAZON_TAG}"
    # Jos Awin ID, voisi lisätä Awin deep link - nyt placeholder
    awin_note = f"Awin: {category['awin']} {category['commission']}"
    return amazon_link, awin_note

async def make_voice(text, output_file="voice.mp3"):
    try:
        clean = text.replace("\n", " ").strip()[:700]
        communicate = edge_tts.Communicate(clean, "en-US-GuyNeural", rate="+8%", volume="+15%")
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print(f"TTS fail {e}")
        return None

def make_sales_video(script_text, voice_file, pexels_clip, category):
    try:
        from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import textwrap, os
        
        duration = 30
        audio_clip = None
        if voice_file and os.path.exists(voice_file):
            try:
                audio_clip = AudioFileClip(voice_file)
                duration = min(55, max(22, audio_clip.duration + 2))
            except:
                pass
        
        # Background
        if pexels_clip and os.path.exists(pexels_clip):
            try:
                bg = VideoFileClip(pexels_clip).subclip(0, duration)
                bg = bg.resize(height=1920)
                if bg.w < 1080:
                    bg = bg.resize(width=1080)
                bg = bg.crop(x_center=bg.w/2, y_center=bg.h/2, width=1080, height=1920).set_duration(duration)
            except:
                bg = ColorClip(size=(1080,1920), color=(20,30,50), duration=duration)
        else:
            bg = ColorClip(size=(1080,1920), color=(20,30,50), duration=duration)
        
        # SALES overlay
        try:
            W, H = 1080, 1920
            pil_img = Image.new('RGBA', (W, H), (0,0,0,0))
            draw = ImageDraw.Draw(pil_img)
            try:
                big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
                med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
                small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            except:
                big = ImageFont.load_default()
                med = big
                small = big
            
            # TOP DEAL BANNER
            draw.rectangle([(0,0),(W, 120)], fill=(255, 140, 0, 255))  # Orange
            draw.text((30, 25), f"🔥 VIRAL DEAL", font=big, fill=(255,255,255,255))
            draw.text((W-280, 35), f"{category['price_range']}", font=big, fill=(0,0,0,255))
            
            # MIDDLE BOX
            box_y = 300
            box_h = 1100
            draw.rounded_rectangle([(30, box_y),(W-30, box_y+box_h)], radius=25, fill=(0,0,0,195))
            
            # Product name
            draw.text((60, box_y+20), category["name"][:32].upper(), font=big, fill=(255,215,0,255))
            
            wrapped = textwrap.wrap(script_text, width=32)[:11]
            y = box_y + 100
            for i, line in enumerate(wrapped):
                font = med
                for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
                    draw.text((60+dx, y+dy), line, font=font, fill=(0,0,0,255))
                draw.text((60, y), line, font=font, fill=(255,255,255,255))
                y += 58
            
            # BOTTOM CTA
            ticker_y = H - 160
            draw.rectangle([(0, ticker_y),(W, H)], fill=(220,20,20,255))
            draw.text((30, ticker_y+20), f"👉 LINK IN DESCRIPTION - {category['commission']} OFF", font=med, fill=(255,255,255,255))
            draw.text((30, ticker_y+70), f"{category['awin']} | {category['name']} | #ViralDeal #AmazonFinds", font=small, fill=(255,255,200,255))
            
            # Price badge
            draw.ellipse([(W-180, 140),(W-20, 260)], fill=(255,215,0,255))
            draw.text((W-155, 175), "DEAL", font=med, fill=(0,0,0,255))
            
            pil_img.save("text_overlay.png")
            txt_clip = ImageClip("text_overlay.png", duration=duration).set_duration(duration)
            
            if audio_clip:
                final = CompositeVideoClip([bg, txt_clip]).set_audio(audio_clip)
            else:
                final = CompositeVideoClip([bg, txt_clip])
            
            final.write_videofile("world_viral_output.mp4", fps=24, codec='libx264', audio_codec='aac', bitrate="4500k", preset="ultrafast", threads=4)
            print(f"Sales video done: {category['name']}")
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
    print("WORLD VIRAL V9 SALES - 100 KATEGORIA AFFILIATE BOT")
    
    category = get_product_category()
    print(f"Selected: {category['id']} | {category['name']} | {category['price_range']} | {category['commission']}")
    
    pexels_clip = get_pexels_video(category["pexels"])
    script = generate_sales_script(category)
    amazon_link, awin_note = build_affiliate_link(category)
    
    print(f"SCRIPT: {script[:180]}...\nLINK: {amazon_link}")
    
    # Description with affiliate
    desc = f"""🔥 {category['name']} - VIRAL DEAL {category['price_range']}

{script}

🛒 GET IT HERE (Affiliate - supports channel):
Amazon: {amazon_link}
{awin_note}
Search: {category['amazon_search']}

💰 Price: {category['price_range']} | Commission: {category['commission']}
⭐ Amazon Best Seller 2025 | Thousands of reviews

#ViralDeal #AmazonFinds #BestSeller #{category['id']} #DIY #Deals

---
Disclaimer: As Amazon Associate we earn from qualifying purchases. Price may change.

Pexels video: {', '.join(category['pexels'])}
Category ID: {category['id']} / 100
"""
    
    with open("script.txt","w", encoding="utf-8") as f:
        f.write(desc)
    
    voice_file = await make_voice(script)
    video_file = make_sales_video(script, voice_file, pexels_clip, category)
    
    print(f"Valmis: {video_file} | Category: {category['name']} | Pexels: {pexels_clip is not None}")
    
    if video_file and os.path.exists(video_file):
        try:
            from youtube_uploader import upload_video
            title = f"{category['name']} - {category['price_range']} - VIRAL DEAL | World Viral"[:95]
            tags = [category["name"], "viral deal", "amazon finds", "best seller", category["id"], "diy", "deals", category["awin"]]
            upload_video(file_path=video_file, title=title, description=desc, tags=tags, privacy="public")
            print(f"Uploaded: {title}")
        except Exception as e:
            print(f"YouTube skip: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
