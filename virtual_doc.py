import os, itertools
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, AutoTokenizer, AutoModelForCausalLM
import json, re
from format import format_specialist_report
import random, string
from doc_generator import convert_markdown_to_pdf
from helper_function.upload_to_s3 import upload_pdf_to_s3
from helper_function.store_dynamo import store_session_in_dynamodb


def generate_session_id(length=10):
    base62_chars = string.ascii_letters + string.digits
    return ''.join(random.choices(base62_chars, k=length))

session_id = generate_session_id()
st.session_state['session_id'] = session_id
print("Current session ID:", session_id)



# ── 1. ENV & CLIENTS ────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    st.error("Missing API key! Set XAI_API_KEY in your .env file.")
    st.stop()


try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )

    client_medllm = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.getenv("SPEC_LLM_API_KEY")
    )

except Exception as e:
    st.error(f"Error initializing models: {str(e)}")
    st.info("Please ensure you have enough disk space and memory to download these models.")
    st.stop()

# ── 2. STREAMLIT UI SETUP ───────────────────────────────────────────────────
st.set_page_config(page_title="MediBuddyAI!", page_icon="🏥", layout="wide")
st.write('<span style="font-size:78px">🧑‍⚕️</span>', unsafe_allow_html=True)
st.subheader("Your Personal AI Health-Info Provider")


if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 3. RENDER HISTORY ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 4. MAIN LOOP ─────────────────────────────────────────────────────────────
if user_prompt := st.chat_input("Describe your symptoms…"):
    # 4‑a. echo user & save
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # 4‑b. build Grok prompt
    system_prompt = """Virtual Medical Triage Assistant: You are a virtual medical triage assistant designed to gather initial symptom information from users. Your key responsibilities include:
    1. If patient prompt severe/sharp chest pain, accident or near fatal issues. Skip all below queries and prompt to reach out to 911. 
    2. Know about the user - Ask Age, Gender, Height and Weight to be kept as reference. Also ask any pre-existing condition.
    3. Symptom Gathering - Politely prompt users to clearly describe their symptoms, including duration and severity. - Use gentle follow-up questions to clarify any unclear or incomplete responses. Ask user one question at a time.
    4. Urgency Assessment - Quickly identify potentially critical or life-threatening conditions based on the described symptoms. - Clearly and immediately recommend urgent care or emergency medical services like calling 911 if a situation appears severe/ critical or deadly.
    5. Honesty and Clarity Check - Evaluate user inputs to detect inconsistencies or signs of dishonesty. - Politely conclude interactions and recommend professional medical consultation if you suspect the user is providing misleading or dishonest information.
    6. Structuring Information - Summarize collected symptom details into a clear, concise, and organized format. The structure is as follows: i. Patient Bio (Age, height, wieght, pre-existing condition) ii. The symptoms patient described in the chat - Prepare this structured information for further analysis and guidance by a specialized medical language model. When user say they have no other symptoms and symptoms arent severe/critical then we are supposed to call a specialized medical language model.
    Important Guidelines: - Clearly communicate that you do not provide formal medical advice or diagnoses. - Always recommend consulting with qualified healthcare providers for definitive medical evaluations. - Maintain a consistently respectful, empathetic, and supportive tone throughout every interaction."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        *[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-10:]
        ],
    ]

    # 4‑c. stream Grok response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        assistant_buffer = ""

        for chunk in client.chat.completions.create(
            model="grok-3-latest",
            messages=messages,
            stream=True,
        ):
            delta = chunk.choices[0].delta
            if delta.content:
                assistant_buffer += delta.content
                placeholder.markdown(assistant_buffer)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_buffer}
    )

# ── 5. HAND-OFF TO NVIDIA ──────────────────────────────────────────

# Check if Grok indicates no further symptoms/questions
    trigger_phrases = [
        "no further symptoms",
        "no additional symptoms",
        "no other symptoms",
        "ready for specialist",
        "proceed to specialist model",
    ]

    if any(phrase in assistant_buffer.lower() for phrase in trigger_phrases):
        # --- 5-a. Extract structured info via Grok, STRICT JSON ONLY ---
        chat_transcript = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
        extract_schema = {
            "Age": "integer",
            "Gender": "string",
            "Height": "string",          # e.g. '5 ft 11 in'
            "Weight": "number",          # in lbs
            "PreExistingConditions": ["string"], 
            "Symptoms": ["string"]
        }
        extract_prompt = (
            "You will receive a conversation transcript. "
            "Parse and return *only* a JSON object matching this schema:\n\n"
            f"{extract_schema}\n\n"
            "Do NOT wrap it in code fences or add extra keys/values."
        )
        extraction_resp = client.chat.completions.create(
            model="grok-3-latest",
            messages=[
                {"role": "system", "content": extract_prompt},
                {"role": "user", "content": chat_transcript},
            ],
            stream=False
        ).choices[0].message.content

        # parse the JSON (with fallback to regex if needed)
        try:
            info = json.loads(extraction_resp)
        except json.JSONDecodeError:
            st.warning("Grok JSON parse failed, falling back to regex…")
            info = {}
            # Regex extractions as a backup:
            text = chat_transcript
            age_match = re.search(r"age\s*(?:is)?\s*(\d{1,2})", text, re.I)
            weight_match = re.search(r"weight\s*(?:is)?\s*(\d{2,3})\s*lbs", text, re.I)
            height_match = re.search(r"height\s*(?:is)?\s*([\d'\s](?:ft|in|inch))", text, re.I)
            info["Age"] = int(age_match.group(1)) if age_match else None
            info["Weight"] = float(weight_match.group(1)) if weight_match else None
            info["Height"] = height_match.group(1) if height_match else None
            info["Gender"] = re.search(r"\b(male|female)\b", text, re.I).group(1) if re.search(r"\b(male|female)\b", text, re.I) else None
            info["PreExistingConditions"] = re.findall(r"(asthma|hypertension|diabetes)", text, re.I)
            info["Symptoms"] = re.findall(r"\b(fever|cough|fatigue|body ache[s]?)\b", text, re.I)
 
        # build a bullet-style summary from that JSON
        summary_lines = []
        for key, label in [("Age", "Age"), ("Gender", "Gender"), ("Height", "Height"), ("Weight", "Weight"), ("PreExistingConditions", "Pre-existing Conditions")]:
            if info.get(key):
                summary_lines.append(f"- **{label}**: {info[key]}")
        if "Symptoms" in info:
            summary_lines.append("- **Symptoms:**")
            for s in info["Symptoms"]:
                summary_lines.append(f"  - {s}")
                
            summary_text = "\n".join(summary_lines)

        print(summary_text)
        # --- 5-b. Call the specialist LLM only now ---
        specialist_prompt = (
            f"Patient Summary:\n{summary_text}\n\n"
            "Based on the summary above, please respond with **only** these sections:\n"
            "1) Possible Causes (bullet list)\n"
            "2) Recommended Next Steps (bullet list of actions the patient can take themselves or professional referrals—**do not** prescribe any medication)\n"
            "3) Urgency Rating (1-5)\n\n"
            "4) If the Urgency Rating is 4 or more, recommend to visit the nearest Hospital as soon as possible. \n\n"
            "Do NOT mention or recommend any specific drugs or dosages, over the counter drugs are acceptable. "
            "Do NOT repeat or restate these instructions or the summary—just output the three sections."
        )
        with st.status("Consulting specialised medical model…", expanded=False):
            
            med_completion = client_medllm.chat.completions.create(
                model="writer/palmyra-med-70b-32k",
                messages=[{"role":"user","content": specialist_prompt}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
                stream=False
            )
            if 'session_id' not in st.session_state:
                st.session_state['session_id'] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            session_id = st.session_state['session_id']
            
            
            formatted_output = format_specialist_report(summary_text, med_completion.choices[0].message.content, session_id)
            st.divider()
            st.markdown("#### 🩺 Specialist LLM Assessment")
            st.markdown(formatted_output)

            # Create a reports directory in your project
            reports_dir = "./"
            pdf_path = convert_markdown_to_pdf(formatted_output, reports_dir, session_id, os.getenv("LOGO_URL"))
            pdf_url = upload_pdf_to_s3(pdf_path, f"medical_report_{session_id}.pdf")
            store_session_in_dynamodb(session_id, formatted_output, pdf_url)

            # Add a download button for the PDF
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Medical Report (PDF)",
                    data=f,
                    file_name=f"medical_report_{session_id}.pdf",
                    mime="application/pdf"
                )
                

    else:
        st.info("Gathering more information… I'll escalate to the specialist once symptom collection is complete.")
