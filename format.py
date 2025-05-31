import re

def format_specialist_report(summary_text, raw_llm_output, session_id):
    """
    Build a full report with:
      1. Session ID
      2. Patient Profile (summary_text)
      3. Possible Causes
      4. Recommended Next Steps
      5. Urgency Rating
    """
    # Start with session and patient profile
    report = f"**Session ID:** `{session_id}`\n\n"
    report += "**Patient Profile:**\n" + summary_text.strip() + "\n\n"

    # Work on the raw LLM output
    out = raw_llm_output.strip()

    # Ensure each header is on its own line
    out = re.sub(r"(?i)(Possible Causes:?)", r"\n\n**Possible Causes:**\n", out)
    out = re.sub(r"(?i)(Recommended Next Steps:?)", r"\n\n**Recommended Next Steps:**\n", out)
    out = re.sub(r"(?i)(Urgency Rating:?)", r"\n\n**Urgency Rating:** ", out)

    # Split concatenated lines where a lowercase letter is followed by an uppercase header
    out = re.sub(r"([a-z0-9\.\)])(Recommended Next Steps:)", r"\1\n\n\2", out)

    # Convert any inline bullets or line breaks to markdown bullets
    def bulletify(section):
        pattern = rf"\*\*{re.escape(section)}\*\*(.*?)(?=\n\n\*\*|$)"
        def repl(m):
            body = m.group(1).strip()
            # split on bullets or sentence breaks
            items = re.split(r"\s*[•\-]\s*|\n", body)
            items = [itm.strip() for itm in items if itm.strip()]
            return f"**{section}:**\n" + "\n".join(f"- {itm}" for itm in items)
        return re.sub(pattern, repl, out, flags=re.S)

    for sec in ["Possible Causes", "Recommended Next Steps"]:
        out = bulletify(sec)

    # Ensure urgency rating on its own line
    out = re.sub(r"\*\*Urgency Rating:\*\*\s*(\d+)", r"**Urgency Rating:** \1", out)

    # Collapse any multiple blank lines
    out = re.sub(r"\n{3,}", "\n\n", out).strip()

    # Append LLM sections to the report
    report += out
    return report
