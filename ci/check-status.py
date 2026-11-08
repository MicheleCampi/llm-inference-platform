"""README status sentence must match docs/status.md."""
import re, sys
st = sys.argv[1] if len(sys.argv) > 1 else "docs/status.md"
rd = sys.argv[2] if len(sys.argv) > 2 else "README.md"
sec = open(st).read().split("## Layers", 1)[1].split("\n## ", 1)[0]
rows = [[c.strip().strip("*") for c in l.strip().strip("|").split("|")]
        for l in sec.splitlines() if re.match(r"^\| [^-]", l) and not l.startswith("| Layer")]
found, layers, total = rows[0], rows[1:-1], rows[-1]
if not found[0].startswith("Foundations"):
    sys.exit("FAIL: first row is not Foundations")
s = [sum(int(r[i]) for r in layers) for i in (1, 2, 3)]
t = [int(total[i]) for i in (1, 2, 3)]
if s != t:
    sys.exit(f"FAIL: layer rows sum to {s}, total row says {t}")
pct = round(100 * (t[1] + t[2] / 2) / t[0])
want = (pct, t[1], t[2], t[0], int(found[2]), int(found[1]))
text = " ".join(open(rd).read().split())
m = re.search(r"about (\d+)% \((\d+) done, (\d+) partial, of (\d+)\); foundations (\d+) of (\d+)", text)
if not m:
    sys.exit("FAIL: README has no status sentence")
got = tuple(int(x) for x in m.groups())
if got != want:
    sys.exit(f"FAIL: README says {got}, status has {want}")
print(f"status OK: {pct}% ({t[1]} done, {t[2]} partial, of {t[0]}); foundations {found[2]} of {found[1]}")
