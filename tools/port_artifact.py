"""One-time port of the CheReeSizer claude.ai artifact to a standalone page (src/index.html).
Every replacement is asserted, so a changed source fails loudly instead of half-porting."""
import re, sys, os

src_path, root = sys.argv[1], sys.argv[2]
html = open(src_path, encoding="utf-8").read()

def sub(old, new, count=1):
    global html
    n = html.count(old)
    assert n == count, f"expected {count} of {old[:70]!r}, found {n}"
    html = html.replace(old, new)

# 1. The artifact host's skeleton: replace the first line with a proper document head.
first, rest = html.split("\n", 1)
assert first.startswith("<!doctype html><html><head>"), "unexpected first line"
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n' + rest)

# 2. Google Fonts links -> embedded IBM Plex (Latin subset, de-duplicated faces).
faces = [l for l in open(os.path.join(root, "tools", "fonts.css"), encoding="utf-8").read().splitlines() if l]
by_data = {}
for f in faces:
    fam = re.search(r"font-family:'([^']+)'", f).group(1)
    wt = int(re.search(r"font-weight:(\d+)", f).group(1))
    data = re.search(r"src:url\((data:[^)]+)\)", f).group(1)
    by_data.setdefault((fam, data), []).append(wt)
merged = []
for (fam, data), wts in by_data.items():
    w = str(wts[0]) if len(wts) == 1 else f"{min(wts)} {max(wts)}"
    rng = re.search(r"unicode-range:([^;]+);", next(f for f in faces if data in f)).group(1)
    merged.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url({data}) format('woff2');unicode-range:{rng};}}")
fonts_block = "<style>\n/* IBM Plex (SIL Open Font License 1.1), Latin subset, embedded so the app works offline */\n" + "\n".join(merged) + "\n</style>"
sub('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">',
    fonts_block)

# 3. Close the head before the page body begins.
sub("</style>\n\n<div class=\"wrap\">", "</style>\n</head>\n<body>\n\n<div class=\"wrap\">")

# 4. Copy: nothing leaves the computer (it is no longer "this browser" in the desktop app).
sub("Nothing is uploaded &mdash; every pixel stays in this browser.", "Nothing is uploaded &mdash; every pixel stays on this computer.")

# 5. Saving: native Save As dialog in the desktop app, a normal browser download otherwise.
sub("  var downloads = null, downloadsResolved = false;\n", "")
old_save = html[html.index("  function saveImage(){"):html.index("  /* ---------------- boot ---------------- */")]
new_save = r'''  function saveImage(){
    var note = $("saveNote");
    if(!S.src) return;
    note.className = "notice";
    note.textContent = "Encoding\u2026";

    var mime = S.fmt === "png" ? "image/png" : (S.fmt === "jpeg" ? "image/jpeg" : "image/webp");
    var ext  = S.fmt === "png" ? "png" : (S.fmt === "jpeg" ? "jpg" : "webp");
    var q    = S.quality / 100;
    var filename = baseName() + "." + ext;

    // JPEG has no alpha: flatten onto the pad colour so transparency never becomes black
    var srcCanvas = out;
    if(S.fmt === "jpeg"){
      var fc = document.createElement("canvas");
      fc.width = out.width; fc.height = out.height;
      var fx = fc.getContext("2d");
      fx.fillStyle = S.mode === "contain" ? S.pad : "#000000";
      fx.fillRect(0,0,fc.width,fc.height);
      fx.drawImage(out,0,0);
      srcCanvas = fc;
    }

    srcCanvas.toBlob(function(blob){
      if(!blob){
        note.className = "notice bad";
        note.textContent = "This system could not encode " + S.fmt.toUpperCase() + ". Try PNG.";
        return;
      }
      var kb = blob.size / 1024;
      var size = kb > 1024 ? (kb/1024).toFixed(1) + " MB" : Math.round(kb) + " KB";
      var done = function(where){
        note.className = "notice good";
        note.textContent = "Saved \u2014 " + where + ", " + size + ".";
      };
      var fail = function(err){
        note.className = "notice bad";
        note.textContent = "Save failed: " + ((err && (err.message || err)) || "unknown error");
      };

      var T = window.__TAURI__;
      if(T && T.dialog && T.fs){
        // Desktop app: native Save As dialog, then write the bytes to the chosen path.
        T.dialog.save({
          defaultPath: filename,
          filters: [{name: S.fmt.toUpperCase() + " image", extensions: [ext]}]
        }).then(function(path){
          if(!path){ note.className = "notice"; note.textContent = "Save cancelled."; return null; }
          return blob.arrayBuffer().then(function(buf){
            return T.fs.writeFile(path, new Uint8Array(buf));
          }).then(function(){ done(path); });
        }).catch(fail);
      } else {
        // Standalone page in a browser: a normal download.
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url; a.download = filename;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
        done(filename);
      }
    }, mime, S.fmt === "png" ? undefined : q);
  }

'''
html = html.replace(old_save, new_save)

# Boot: drop the claude.ai downloads probe; keep everything before it.
b0 = html.index("\n    if(window.claude && window.claude.use){")
b1 = html.index("  if(document.readyState")
html = html[:b0] + "  }\n\n" + html[b1:]

assert "window.claude" not in html and "downloadsResolved" not in html and "fonts.googleapis" not in html
os.makedirs(os.path.join(root, "src"), exist_ok=True)
open(os.path.join(root, "src", "index.html"), "w", encoding="utf-8", newline="\n").write(html)
print("ported:", len(html.splitlines()), "lines,", round(len(html.encode()) / 1024), "KB; font faces:", len(merged))
