"""README Security posture counts must match docs/threat-model.md."""
import re, sys
tm = sys.argv[1] if len(sys.argv) > 1 else "docs/threat-model.md"
rd = sys.argv[2] if len(sys.argv) > 2 else "README.md"
ALLOWED = {"Mitigated", "Partly mitigated", "NOT mitigated", "Not assessed"}
rows = [l for l in open(tm) if re.match(r"^\| [A-Z][0-9]+ \|", l)]
status = [l.split("|")[4].strip().split(" (")[0] for l in rows]
bad = sorted(set(status) - ALLOWED)
if bad:
    sys.exit(f"FAIL: status not allowed: {bad}")
c = {k: status.count(k) for k in ALLOWED}
want = (len(rows), c["Mitigated"], c["Partly mitigated"], c["NOT mitigated"], c["Not assessed"])
text = " ".join(open(rd).read().split())
m = re.search(r"covers (\d+) threats: (\d+) mitigated, (\d+) partly mitigated, (\d+) not mitigated, (\d+) not yet assessed", text)
if not m:
    sys.exit("FAIL: README has no Security posture count sentence")
got = tuple(int(x) for x in m.groups())
if got != want:
    sys.exit(f"FAIL: README says {got}, threat model has {want}")
print(f"threat model OK: {want[0]} threats, {want[1]}/{want[2]}/{want[3]}/{want[4]}")
