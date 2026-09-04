import json, sys, os

OUT = "/tmp/claude-0/-home-user--github/96f99610-ebd0-55f7-b5d1-052084382799/scratchpad/sessions.jsonl"

def extract(path):
    raw = open(path, encoding="utf-8").read()
    i = raw.find('{"ccr"')
    j = raw.rfind('}}')
    if i == -1 or j == -1:
        sys.exit("no json found in %s" % path)
    return json.loads(raw[i:j+2])["ccr"]

rows = []
for path in sys.argv[1:]:
    ccr = extract(path)
    for s in ccr["data"]:
        ctx = s.get("session_context", {}) or {}
        ext = s.get("external_metadata", {}) or {}
        rows.append({
            "id": s.get("id"),
            "title": s.get("title"),
            "created": s.get("created_at", "")[:19],
            "updated": s.get("updated_at", "")[:19],
            "bucket": (s.get("status_bucket") or "").replace("SESSION_STATUS_BUCKET_", ""),
            "state": (s.get("session_status") or "").replace("SESSION_STATUS_", ""),
            "origin": s.get("origin"),
            "envkind": s.get("environment_kind"),
            "model": s.get("configured_model"),
            "effort": ctx.get("effort_level"),
            "tags": ",".join(s.get("tags") or []),
            "conn": s.get("connection_status"),
            "cost": (ext.get("usage") or {}).get("cost_usd"),
            "tokens": (ext.get("context_usage") or {}).get("used_tokens"),
            "ratelimit": (ext.get("rate_limit_info") or {}).get("status"),
        })
    print("%s -> %d rows, has_more=%s, last_id=%s" % (
        os.path.basename(path), len(ccr["data"]), ccr.get("has_more"), ccr.get("last_id")), file=sys.stderr)

with open(OUT, "a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended %d rows to %s" % (len(rows), OUT), file=sys.stderr)
