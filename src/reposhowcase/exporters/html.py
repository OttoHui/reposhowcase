from __future__ import annotations

import html
from pathlib import Path

from ..models import Storyboard


def export_html(storyboard: Storyboard, output: str | Path) -> Path:
    """Write a self-contained, keyboard-navigable HTML presentation."""
    slides = []
    for slide in storyboard.slides:
        bullets = "".join(f"<li>{html.escape(item)}</li>" for item in slide.bullets)
        sources = "".join(
            f'<small class="source">{html.escape(item.path)} — {html.escape(item.detail)}</small>'
            for item in slide.evidence
        )
        slides.append(
            f'<article class="slide"><small>{slide.number:02d} / {len(storyboard.slides):02d}</small>'
            f"<h2>{html.escape(slide.title)}</h2><p>{html.escape(slide.body)}</p>"
            f"<ul>{bullets}</ul><div>{sources}</div></article>"
        )
    content = f"""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{html.escape(storyboard.title)}</title>
<style>
body{{margin:0;background:#f7f9fc;color:#162033;font:16px/1.5 system-ui,-apple-system,sans-serif}}
header{{padding:42px 24px;color:white;background:linear-gradient(120deg,#173b8f,#2864e8 55%,#7654d6)}}
header h1{{max-width:900px;margin:0 auto;font-size:clamp(2rem,5vw,4rem)}} main{{max-width:900px;margin:auto;padding:32px 24px}}
.slide{{display:none;background:white;border:1px solid #dbe2ef;border-radius:16px;padding:32px;min-height:360px;box-shadow:0 5px 18px #243d7110}}
.slide.active{{display:block}} h2{{font-size:2.5rem;color:#2864e8}} li{{margin:14px 0}} .source{{display:block;color:#63708a;margin-top:8px}}
button{{padding:10px 16px;border:0;border-radius:8px;background:#2864e8;color:white;cursor:pointer;margin-right:8px}}
button:focus-visible{{outline:3px solid #7654d6;outline-offset:2px}}
@media (prefers-reduced-motion: reduce){{*{{scroll-behavior:auto!important}}}}
</style><header><h1>{html.escape(storyboard.title)}</h1></header><main><section id="slides" aria-live="polite">{"".join(slides)}</section>
<p><button id="prev">Previous</button><button id="next">Next</button><span id="count"></span></p>
<script>let i=0,s=[...document.querySelectorAll('.slide')],count=document.querySelector('#count');function show(){{s.forEach((x,n)=>x.classList.toggle('active',n===i));count.textContent=` ${{i+1}} / ${{s.length}}`;}}document.querySelector('#next').onclick=()=>{{i=(i+1)%s.length;show()}};document.querySelector('#prev').onclick=()=>{{i=(i+s.length-1)%s.length;show()}};onkeydown=e=>{{if(e.key==='ArrowRight')document.querySelector('#next').click();if(e.key==='ArrowLeft')document.querySelector('#prev').click()}};show();</script></main>"""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination
