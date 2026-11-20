# Build the compact "reader edition" PDF of all artifacts. Source HTML is never modified:
# each artifact is copied to a temp dir, a compact print style and a script that drops the
# header table, required-sections table and the tail (checks, Reviewed by, Appendix) are
# injected, then Chrome prints it. An "Open items" page from PROGRESS.md goes at the end.
# Needs: Google Chrome, pypdf.  Usage: python3 tools/build_reader_pdf.py [out.pdf]
import sys, re, glob, os, subprocess, html, tempfile
from pypdf import PdfWriter, PdfReader

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else f"{repo}/build/AI-SRE-Artifacts-reader.pdf"
os.makedirs(os.path.dirname(out), exist_ok=True)
work = tempfile.mkdtemp(prefix="ai-sre-pdf-")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """<style>
@page{size:A4;margin:10mm}
@page erd{size:A3 landscape;margin:8mm}
@media print{
 body{font-size:10.5px;line-height:1.4}
 main{padding:0}
 h1{font-size:20px}
 h2{font-size:15px;margin:14px 0 2px;padding-top:6px;border-top-width:1px}
 h3{font-size:12px;margin:10px 0 3px}
 .sub{margin:0 0 8px}
 table{font-size:9.5px;margin:4px 0 8px}
 th,td{padding:2px 5px}
 .reg{font-size:8.5px}
 .qs,.cap{font-size:9px;margin:0 0 6px}
 .note,.no{padding:4px 8px;margin:6px 0}
 .fig{padding:4px;margin:6px 0}
 .fig:not(.erd) svg{max-height:175mm;width:auto!important;margin:0 auto}
 .L{font-size:8.5px;padding:0 4px}
 pre{font-size:8.5px;padding:6px 8px}
 ul,ol{margin:4px 0}
}
</style>"""

JS = """<script>
document.addEventListener('DOMContentLoaded',function(){
 var m=document.querySelector('main')||document.body;
 // header table (Team / Breakout room / Date / Members)
 m.querySelectorAll('table').forEach(function(t){var th=t.querySelector('th');if(th&&th.textContent.trim()==='Team')t.remove();});
 // required-sections table
 m.querySelectorAll('h3').forEach(function(h){if(h.textContent.trim()==='Required sections'){var n=h.nextElementSibling;if(n&&n.tagName==='TABLE')n.remove();h.remove();}});
 // tail: acceptance checks, Reviewed by, Appendix
 var h=[].find.call(m.querySelectorAll('h2'),function(x){return /^Acceptance checks/.test(x.textContent.trim());});
 if(h){var n=h;while(n){var nx=n.nextElementSibling;n.remove();n=nx;}}
 // short label chips: F / D / A, "source: Artifact 5" -> "A5"
 var ab={'Fixed requirement':'F','Decision':'D','Assumption':'A'};
 m.querySelectorAll('.L').forEach(function(s){var k=s.textContent.trim();if(ab[k]){s.title=k;s.textContent=ab[k];}});
 m.querySelectorAll('td').forEach(function(td){if(!td.querySelector('.L'))return;
  td.innerHTML=td.innerHTML.replace(/source:\\s*/g,'').replace(/Artifacts? (\\d+)/g,'A$1');});
 // legend: say what the letters mean
 var lg=document.createElement('p');lg.className='qs';
 lg.innerHTML='Labels: <span class="L F">F</span> Fixed requirement (source given), <span class="L D">D</span> Decision, <span class="L A">A</span> Assumption. An = Artifact n.';
 var sub=m.querySelector('.sub');if(sub)sub.after(lg);
});
</script>"""

files = sorted(glob.glob(f"{repo}/specs/layer-*/artifact-*.html"))
titles, pdfs = [], []
for i, f in enumerate(files, 1):
    src = open(f, encoding="utf-8").read()
    titles.append("A%s %s" % re.search(r"<h1>Artifact (\d+) - (.*?)</h1>", src).groups())
    src = src.replace("</head>", CSS + "</head>", 1).replace("</body>", JS + "</body>", 1)
    tmp = f"{work}/{i:02d}.html"; open(tmp, "w", encoding="utf-8").write(src)
    pdf = f"{work}/{i:02d}.pdf"; pdfs.append(pdf)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + tmp], check=True, capture_output=True)

# Open items page from PROGRESS.md (replaces the per-artifact appendices)
prog = open(f"{repo}/PROGRESS.md", encoding="utf-8").read()
sec = prog.split("## Open items carried across layers", 1)[1].split("\n## ", 1)[0]
rows = [l.strip().strip("|").split("|") for l in sec.splitlines() if l.startswith("|")]
def md(s): return re.sub(r"`([^`]+)`", r"<code>\1</code>", re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s.strip())))
style = re.search(r"<style>.*?</style>", open(files[-1], encoding="utf-8").read(), re.S).group(0)
trs = "".join("<tr>" + "".join(f"<{'th' if r is rows[0] else 'td'}>{md(c)}</{'th' if r is rows[0] else 'td'}>" for c in r) + "</tr>"
              for r in rows if not set("".join(r)) <= set("-: "))
page = f"<!doctype html><html><head><meta charset='utf-8'>{style}{CSS}</head><body><main><h1>Open items carried across layers</h1><table>{trs}</table></main></body></html>"
open(f"{work}/open.html", "w", encoding="utf-8").write(page)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={work}/open.pdf", f"file://{work}/open.html"], check=True, capture_output=True)
titles.append("Open items"); pdfs.append(f"{work}/open.pdf")

w = PdfWriter()
for t, p in zip(titles, pdfs):
    start = len(w.pages); w.append(PdfReader(p)); w.add_outline_item(t, start)
    print(f"{t}: pages {start+1}-{len(w.pages)} ({len(w.pages)-start})")
w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
w.write(out)
print("total", len(w.pages))
