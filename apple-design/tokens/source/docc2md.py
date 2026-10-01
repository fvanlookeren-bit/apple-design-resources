import json, sys
def inline(items, refs):
    out = []
    for it in items or []:
        t = it.get("type")
        if t == "text": out.append(it.get("text", ""))
        elif t in ("emphasis", "strong", "newTerm"): out.append(inline(it.get("inlineContent"), refs))
        elif t == "codeVoice": out.append("`" + it.get("code", "") + "`")
        elif t == "reference":
            r = refs.get(it.get("identifier"), {})
            out.append(r.get("title") or it.get("identifier", "").split("/")[-1])
        elif t == "image": out.append("[imagen]")
        else: out.append(inline(it.get("inlineContent"), refs))
    return "".join(out)
def block(b, refs, depth=0):
    t = b.get("type")
    if t == "heading": return "\n" + "#" * min(6, b.get("level", 2) + 1) + " " + b.get("text", "") + "\n"
    if t == "paragraph": return inline(b.get("inlineContent"), refs) + "\n"
    if t in ("unorderedList", "orderedList"):
        return "".join("  " * depth + "- " + "".join(block(c, refs, depth + 1) for c in i.get("content", [])).strip() + "\n" for i in b.get("items", []))
    if t == "aside": return "> " + b.get("name", b.get("style", "")) + ": " + " ".join(block(c, refs).strip() for c in b.get("content", [])) + "\n"
    if t == "table":
        rows = []
        for row in b.get("rows", []):
            rows.append("| " + " | ".join(" ".join(block(c, refs).strip() for c in cell).replace("\n", " ") for cell in row) + " |")
        if rows: rows.insert(1, "|" + "---|" * (rows[0].count("|") - 1))
        return "\n".join(rows) + "\n"
    if t == "tabNavigator":
        return "".join("\n**[" + tab.get("title", "") + "]**\n" + "".join(block(c, refs) for c in tab.get("content", [])) for tab in b.get("tabs", []))
    if t == "row": return "".join("".join(block(c, refs) for c in col.get("content", [])) for col in b.get("columns", []))
    if t == "links": return ""
    if "content" in b: return "".join(block(c, refs) for c in b["content"])
    return ""
d = json.load(open(sys.argv[1]))
refs = d.get("references", {})
out = ["# " + d.get("metadata", {}).get("title", "")]
for s in d.get("primaryContentSections", []):
    for b in s.get("content", []): out.append(block(b, refs))
print("\n".join(out))
