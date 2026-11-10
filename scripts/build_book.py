"""வெளியீட்டு நூல்: முன்னுரைப் பகுதிகள் + 1602 சூத்திரம் (காண்டிகை, உரை) → HTML, PDF, EPUB.

மூலங்கள்:
  sources/munnurai.md        — முன்னுரைப் பகுதிகள் (ஆவணப் பதிப்பு 596-இலிருந்து; செயலிப் பகுதியும் ஆங்கிலமும் நீக்கியது)
  build/senthamil_marabu.md  — data_v2-இலிருந்து build_nool.py உருவாக்கிய உடலும் «ஆய்வுகள்» பிற்சேர்க்கையும
வெளியீடு: build/book/ (senthamil_marabu.html, .pdf, .epub)
python3 scripts/build_book.py [--no-pdf] [--no-epub]
"""
import re, sys, shutil, subprocess, json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/book"
FRONT_KEEP = ["நூல்", "ஆசிரியர் நெறி", "பாடம்", "நூல் மரபு", "பயன்பாட்டு நெறி", "தொகை ஒப்பு"]
TITLE = "செந்தமிழ் மரபு"
AUTHOR = "தனுசாந்தன் வர்ணகுலசிங்கம்"
ORCID = "https://orcid.org/0009-0005-4309-7476"
COPY = "© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic)."
TA_MONTH = ["சனவரி", "பிப்ரவரி", "மார்ச்சு", "ஏப்ரல்", "மே", "சூன்", "சூலை", "ஆகத்து",
            "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "திசம்பர்"]


def front_sections():
    md = (ROOT / "sources/munnurai.md").read_text("utf-8")
    parts = re.split(r"(?m)^(?=## )", md)
    keep = {}
    for p in parts[1:]:
        name = p.splitlines()[0][3:].strip()
        if name in FRONT_KEEP:
            keep[name] = p.rstrip() + "\n"
    missing = [n for n in FRONT_KEEP if n not in keep]
    if missing:
        sys.exit(f"முன்னுரைப் பகுதி இல்லை: {missing}")
    return "\n".join(keep[n] for n in FRONT_KEEP)


def body():
    md = (ROOT / "build/senthamil_marabu.md").read_text("utf-8")
    return md[md.index("## படலம் 1"):]


def title_block():
    d = date.today()
    ed = f"முதல் பதிப்பு · {d.day} {TA_MONTH[d.month-1]} {d.year}"
    return f"""```{{=html}}
<section class="title-page">
<p class="t">{TITLE}</p>
<p class="st">எழுத்து · சொல் · பொருள் — 1602 நூற்பா, காண்டிகை, உரை</p>
<p class="au">வழிநூல்: {AUTHOR}</p>
<p class="help" style="margin-bottom:2mm">ORCID {ORCID[18:]}</p>
<p class="help">தொழில்நுட்ப உதவி: Claude (Anthropic)</p>
<p class="ed">{ed}</p>
</section>
```

```{{=html}}
<section class="verso">
<p><b>{TITLE}</b> — வழிநூல் (தொகுத்தல், பொருள். 643).</p>
<p>சூத்திரங்கள்: முதல்வன் இயற்றியவை; இப்பதிப்பு அவற்றில் ஒரு சொல்லையும் மாற்றவில்லை (பொருள். 652).</p>
<p>மூலப் பாடம்: எழுத்ததிகாரம் — நச்சினார்க்கினியர் உரைப் பதிப்பின் மூலம்; சொல்லதிகாரம், பொருளதிகாரம் — மதுரைத் திட்ட (Project Madurai, projectmadurai.org) மின்பதிப்பு, அவர்களின் அனுமதி நிபந்தனைப்படி நன்றியுடன். இப்பதிப்பில் அம்மின்பாடத்தின் நிறுத்தக் குறிகள் நீக்கப்பட்டன; சில தட்டச்சுப் பிழைகள் திருத்தப்பட்டன («பாடம்» பகுதி காண்க).</p>
<p>காண்டிகை, உரை, தொகுப்பு: {AUTHOR} (ORCID: {ORCID}).</p>
<p>{COPY}</p>
<p>உரிமம்: காண்டிகை, உரை, தொகுப்பு — Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0), https://creativecommons.org/licenses/by-nc/4.0/ — ஆசிரியர் பெயரும் மூலமும் குறித்து, வணிக நோக்கின்றி, எவரும் படியெடுக்கவும் பகிரவும் தழுவவும் செய்யலாம். வணிகப் பயன்பாடு (விற்பனை, கட்டணச் சேவை, வணிக வெளியீடு முதலியன) ஆசிரியரின் எழுத்து இசைவுடன் மட்டும்; வணிக உரிமை ஆசிரியருக்கே. சூத்திரங்கள் பொதுவுடைமை; மதுரைத் திட்ட மின்பாடம் இவ்வுரிமத்துள் அடங்காது.</p>
<p>முதல் வெளியீடு: Zenodo, கருத்தாக்க DOI 10.5281/zenodo.24011590.</p>
<p>{ed}.</p>
</section>
```
"""


def postprocess(html):
    # சூத்திரத் தொகுதி: எண் வரி + மூலம், காண்டிகை, உரை, துணிவு
    html = re.sub(r"<p><strong>(\d+)</strong> · ((?:எழு|சொல்|பொருள்)\. \d+)<br\s*/?>\s*(.*?)</p>",
                  lambda m: f'<div class="sutra"><p class="moolam"><span class="snum"><strong>{m.group(1)}</strong> · {m.group(2)}</span>{m.group(3)}</p>',
                  html, flags=re.S)
    html = html.replace("<p><strong>காண்டிகை.</strong>", '<p class="k"><strong>காண்டிகை.</strong>')
    html = html.replace("<p><strong>உரை.</strong>", '<p class="u"><strong>உரை.</strong>')
    html = re.sub(r"<p><strong>துணிவு\.</strong>(.*?)</p>", r'<p class="thunivu"><strong>துணிவு.</strong>\1</p></div>', html, flags=re.S)
    html = re.sub(r"<colgroup>.*?</colgroup>", "", html, flags=re.S)   # அட்டவணை நெடுவரிசை அகலம் உள்ளடக்கத்துக்கேற்ப
    html = re.sub(r'<h2 id="([^"]*)">(படலம் \d+:)', r'<h2 id="\1" class="padalam">\2', html)
    html = re.sub(r'<h3 id="([^"]*)">(ஓத்து \d+:[^<]*)</h3>\s*<p>(\d+ சூத்திரங்கள் · [^<]*)</p>',
                  r'<h3 id="\1" class="othu">\2</h3>\n<p class="othu-meta">\3</p>', html)
    return html


def check(html):
    n_open = html.count('<div class="sutra">')
    n_close = html.count('<p class="thunivu">')
    if n_open != 1602 or n_close != 1602:
        sys.exit(f"சூத்திரத் தொகுதி எண்ணிக்கை பிழை: {n_open} / {n_close}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "book/fonts", OUT / "fonts", dirs_exist_ok=True)
    shutil.copy(ROOT / "book/book.css", OUT / "book.css")
    md = title_block() + "\n" + front_sections() + "\n" + body() + f"\n\n```{{=html}}\n<p class=\"end\">{COPY}</p>\n```\n"
    (OUT / "senthamil_marabu.md").write_text(md, "utf-8")
    meta = ["--metadata", f"title={TITLE}", "--metadata", f"author={AUTHOR}", "--metadata", "lang=ta"]
    subprocess.run(["pandoc", str(OUT / "senthamil_marabu.md"), "-f", "markdown-implicit_figures", "-t", "html5",
                    "-s", "--toc", "--toc-depth=3", "--css", "book.css", "--metadata", "pagetitle=" + TITLE,
                    "-V", "lang=ta", "-o", str(OUT / "senthamil_marabu.raw.html")], check=True)
    html = (OUT / "senthamil_marabu.raw.html").read_text("utf-8")
    html = re.sub(r'<header id="title-block-header">.*?</header>', "", html, flags=re.S)
    # பொருளடக்கம் தலைப்புப் பக்கங்களுக்குப் பின்
    toc = re.search(r'<nav id="TOC".*?</nav>', html, flags=re.S).group(0)
    html = html.replace(toc, "", 1)
    html = html.replace("</section>\n<h2", "</section>\n" + toc + "\n<h2", 1) if "</section>\n<h2" in html else \
        re.sub(r'(<section class="verso">.*?</section>)', lambda m: m.group(1) + "\n" + toc, html, count=1, flags=re.S)
    html = postprocess(html)
    check(html)
    (OUT / "senthamil_marabu.html").write_text(html, "utf-8")
    (OUT / "senthamil_marabu.raw.html").unlink()
    print("HTML: 1602 சூத்திரத் தொகுதி")

    if "--no-pdf" not in sys.argv:
        subprocess.run(["node", str(ROOT / "scripts/book_pdf.js"), str(OUT / "senthamil_marabu.html"),
                        str(OUT / "senthamil_marabu.pdf")], check=True)
    if "--no-epub" not in sys.argv:
        fonts = [f"--epub-embed-font={p}" for p in sorted((OUT / "fonts").glob("*.woff2"))]
        epub_md = re.sub(r"```\{=html\}\n<section class=\"title-page\">.*?```\n", "", md, flags=re.S)
        (OUT / "senthamil_marabu.epub.md").write_text(epub_md, "utf-8")
        subprocess.run(["pandoc", str(OUT / "senthamil_marabu.epub.md"), "-f", "markdown-implicit_figures",
                        "-t", "epub3", "--toc", "--toc-depth=3", "--split-level=3", "--css", str(OUT / "book.css"),
                        *meta, "--metadata", f"rights={COPY} உரிமம்: CC BY-NC 4.0 (காண்டிகை, உரை, தொகுப்பு); வணிக உரிமை ஆசிரியருக்கு மட்டும்.", *fonts, "-o", str(OUT / "senthamil_marabu.epub")],
                       check=True, cwd=OUT)
        (OUT / "senthamil_marabu.epub.md").unlink()
        print("EPUB: எழுதப்பட்டது")


if __name__ == "__main__":
    main()
