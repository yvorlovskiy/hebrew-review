# Usage: python build.py [--audio]   (needs edge-tts for --audio)
# Source of truth: cards.tsv. Writes index.html, audio/*.mp3, and the Obsidian deck.
import csv, hashlib, json, os, sys, subprocess, html
VAULT = os.path.expanduser("~/ObsidianVault/flaschards/Hebrew Review.md")
VOICE = "he-IL-AvriNeural"
rows = [r for r in csv.reader(open("cards.tsv"), delimiter="\t") if r and not r[0].startswith("#")]
cards = []
for sec, en, he, tr, note in rows:
    cid = hashlib.sha1((en + he).encode()).hexdigest()[:10]
    cards.append(dict(id=cid, s=sec, en=en, he=he, tr=tr, n=note))
if "--audio" in sys.argv:
    os.makedirs("audio", exist_ok=True)
    tts = sys.argv[sys.argv.index("--audio") + 1]
    for c in cards:
        f = f"audio/{c['id']}.mp3"
        if os.path.exists(f): continue
        text = c["he"].replace(" / ", ". ").replace("...", "")
        subprocess.run([tts, "--voice", VOICE, "--rate=-15%", "--text", text, "--write-media", f], check=True, capture_output=True)
        print("audio", c["en"])
# Obsidian deck
secs = list(dict.fromkeys(c["s"] for c in cards))
names = {"Basics":"Basics","Help":"When you're stuck","Asking":"Asking for things","Cafe":"Cafe and restaurant","Paying":"Paying","Grocery":"Grocery store","Around":"Getting around","Numbers":"Numbers past 10"}
md = ["---","title: Hebrew Review","created: 2026-11-23","tags:","  - terms/hebrew","---","",
      "Quick get-around Hebrew. Transliteration first; `kh` is the throaty sound (Bach). Men's forms by default. Phone version with audio: https://yury.ml/hebrew-review/",""]
for s in secs:
    md += [f"## {names[s]}", ""]
    for c in cards:
        if c["s"] != s: continue
        back = f"**{c['tr']}** ({c['he']})" + (f". {c['n']}" if c["n"] else "")
        md += [c["en"], "?", back, ""]
open(VAULT, "w").write("\n".join(md))
tpl = open("template.html").read()
open("index.html", "w").write(tpl.replace("/*CARDS*/[]", json.dumps(cards, ensure_ascii=False)).replace("/*NAMES*/{}", json.dumps(names)))
print(len(cards), "cards")
