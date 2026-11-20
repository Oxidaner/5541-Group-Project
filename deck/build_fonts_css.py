import re, os, pathlib
base = pathlib.Path("deck/fonts")
out = []
for css_name in ["space.css","inter.css","mono.css","fraunces.css"]:
    txt = (base / css_name).read_text()
    # replace absolute gstatic urls with local basenames
    def repl(m):
        url = m.group(1)
        return "url(fonts/" + url.rsplit("/",1)[-1] + ")"
    txt = re.sub(r"url\((https://[^)]*\.woff2)\)", repl, txt)
    out.append(txt)
pathlib.Path("deck/fonts.css").write_text("\n".join(out))
print("written", len("\n".join(out)), "bytes")
# verify no https remains
print("https remaining:", "\n".join(out).count("https://"))
