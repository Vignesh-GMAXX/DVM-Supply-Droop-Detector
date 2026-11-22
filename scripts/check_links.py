"""Check relative links, images and #anchors in the repository's markdown files (GitHub heading-slug rules).

Usage: python3 scripts/check_links.py [repo_root]      exit status 1 if anything is broken
"""
import re, os, sys, glob, unicodedata
root = os.path.normpath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def slugify(text):
    text = re.sub(r'`([^`]*)`', r'\1', text)                 # inline code -> text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)      # links -> text
    text = re.sub(r'<[^>]+>', '', text)                       # html tags
    text = text.replace('*', '').strip().lower()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in '-_ ' or cat[0] in 'LNM' or cat == 'Pc':
            out.append(ch)
    return ''.join(out).replace(' ', '-')

def anchors(path):
    s = open(path, encoding='utf-8').read()
    s_nocode = re.sub(r'```.*?```', '', s, flags=re.S)
    seen = {}
    res = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', s_nocode))
    for m in re.finditer(r'^(#{1,6})\s+(.*?)\s*#*\s*$', s_nocode, re.M):
        base = slugify(m.group(2))
        n = seen.get(base, 0)
        res.add(base if n == 0 else f'{base}-{n}')
        seen[base] = n + 1
    return res

cache = {}
bad = 0; ext = set(); count = 0
files = [f for f in glob.glob(os.path.join(root, '**/*.md'), recursive=True) if '/report/latex/' not in f]
for f in sorted(files):
    s = open(f, encoding='utf-8').read()
    s_nocode = re.sub(r'```.*?```', '', s, flags=re.S)
    s_nocode = re.sub(r'`[^`\n]*`', '', s_nocode)
    targets = re.findall(r'\]\(([^)\s]+)\)', s_nocode) + re.findall(r'(?:src|href)="([^"]+)"', s_nocode)
    for t in targets:
        count += 1
        if t.startswith(('http://', 'https://', 'mailto:')):
            ext.add(t); continue
        path, _, frag = t.partition('#')
        tgt = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
        if not os.path.exists(tgt):
            print(f'MISSING  {os.path.relpath(f, root)} -> {t}'); bad += 1; continue
        if frag:
            if os.path.isdir(tgt) or not tgt.endswith('.md'):
                print(f'ANCHOR-ON-NON-MD {os.path.relpath(f, root)} -> {t}'); bad += 1; continue
            if tgt not in cache: cache[tgt] = anchors(tgt)
            if frag not in cache[tgt]:
                print(f'BAD-ANCHOR {os.path.relpath(f, root)} -> {t}'); bad += 1
print(f'{count} links checked, {bad} problems, {len(ext)} external links not checked')
sys.exit(1 if bad else 0)
