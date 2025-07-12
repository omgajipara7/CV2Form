# app.py or streamlit_app.py

import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import subprocess

# ✅ Auto-download the spaCy model if missing
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    import spacy
    nlp = spacy.load("en_core_web_sm")

# 🔍 Extract text from PDF
def extract_text(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# 👤 Extract Name
def extract_name(text):
    lines = text.strip().split("\n")[:10]
    bad_keywords = ['machine', 'developer', 'engineer', 'email', 'mobile', 'data', 'resume', 'github', '@', '+91']
    for line in lines:
        if any(bad in line.lower() for bad in bad_keywords):
            continue
        if re.match(r'^([A-Z][a-z]+\s[A-Z][a-z]+)$', line.strip()):
            return line.strip()
    doc = nlp("\n".join(lines))
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
            return ent.text.title()
    return "Not Found"

# 📧 Email
def extract_email(text):
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    return match.group(0) if match else "Not Found"

# 📞 Phone
def extract_phone(text):
    match = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', text)
    return match.group(0) if match else "Not Found"

# 🔗 LinkedIn
def extract_linkedin(text):
    match = re.search(r'https?://(www\.)?linkedin\.com/in/[^\s]+', text)
    if match:
        return match.group(0)
    match = re.search(r'linkedin\.com/in/[^\s]+', text)
    return "https://" + match.group(0) if match else "Not Found"

# 💻 GitHub
def extract_github(text):
    match = re.search(r'https?://(www\.)?github\.com/[^\s]+', text)
    return match.group(0) if match else "Not Found"

# 🧠 Skills
def extract_skills(text):
    skills = [
        'python', 'java', 'c++', 'sql', 'machine learning', 'deep learning',
        'nlp', 'data analysis', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
        'keras', 'django', 'flask', 'html', 'css', 'javascript', 'react',
        'excel', 'power bi', 'matplotlib', 'seaborn', 'linux', 'git'
    ]
    found = []
    for skill in skills:
        if re.search(rf'\b{skill}\b', text, re.IGNORECASE):
            found.append(skill.lower())
    return ', '.join(sorted(set(found))) if found else "Not Found"

# 🎓 Education
def extract_education(text):
    edu_keywords = ['b.tech', 'b.e.', 'm.tech', 'bachelor', 'master', 'mca', 'msc', 'bsc', 'degree', 'engineering']
    for line in text.lower().splitlines():
        if any(keyword in line for keyword in edu_keywords):
            return line.strip().title()
    return "Not Found"

# 🚀 Streamlit UI
st.set_page_config(page_title="CV2Form - Resume Extractor", page_icon="🧠")
st.title("🧾 CV2Form - Resume to Form Extractor")
st.write("Upload a PDF resume, and this app will extract important information!")

uploaded_file = st.file_uploader("📤 Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("🔍 Extracting data..."):
        text = extract_text(uploaded_file)
        data = {
            "Name": extract_name(text),
            "Email": extract_email(text),
            "Phone": extract_phone(text),
            "LinkedIn": extract_linkedin(text),
            "GitHub": extract_github(text),
            "Skills": extract_skills(text),
            "Education": extract_education(text)
        }

    st.success("✅ Data extracted! You can review and edit below:")

    # 🔧 Editable fields
    name = st.text_input("Name", value=data["Name"])
    email = st.text_input("Email", value=data["Email"])
    phone = st.text_input("Phone", value=data["Phone"])
    linkedin = st.text_input("LinkedIn", value=data["LinkedIn"])
    github = st.text_input("GitHub", value=data["GitHub"])
    skills = st.text_area("Skills", value=data["Skills"])
    education = st.text_input("Education", value=data["Education"])

    # 💾 Save button
    if st.button("💾 Save to CSV"):
        df = pd.DataFrame([{
            "Name": name, "Email": email, "Phone": phone,
            "LinkedIn": linkedin, "GitHub": github,
            "Skills": skills, "Education": education
        }])
        df.to_csv("resume_final_output.csv", index=False)
        st.success("🎉 Saved as 'resume_final_output.csv'")
