from pathlib import Path

import streamlit as st

from parser import load_nlp, parse_resume
from utils import save_to_json, save_to_csv


st.set_page_config(
    page_title="Smart Resume Parser",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
    }
    .sub-text {
        font-size: 18px;
        color: #444;
        text-align: center;
        margin-bottom: 20px;
    }
    .box {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #d9e2ec;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📄 Smart Resume Parser</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Upload a PDF or DOCX resume and extract structured information instantly.</p>', unsafe_allow_html=True)

nlp = load_nlp()

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

with col2:
    st.info("Supported files: PDF and DOCX")

if uploaded_file is not None:
    upload_dir = Path("uploaded_resumes")
    output_dir = Path("output_files")

    upload_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    saved_file_path = upload_dir / uploaded_file.name

    with open(saved_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        result = parse_resume(saved_file_path, nlp)

        st.success("Resume parsed successfully")

        st.markdown("## Extracted Details")
        c1, c2 = st.columns(2)

        with c1:
            st.write(f"**Name:** {result['name']}")
            st.write(f"**Email:** {result['email']}")
            st.write(f"**Phone:** {result['phone']}")

        with c2:
            st.write("**Skills:**")
            if result["skills"]:
                st.write(", ".join(result["skills"]))
            else:
                st.write("Not found")

        st.markdown("### Education")
        if result["education"]:
            for item in result["education"]:
                st.write(f"- {item}")
        else:
            st.write("Not found")

        st.markdown("### Experience")
        if result["experience"]:
            for item in result["experience"]:
                st.write(f"- {item}")
        else:
            st.write("Not found")

        st.markdown("### Raw Text Preview")
        st.text_area("Preview", result["raw_text_preview"], height=200)

        json_file = output_dir / f"{saved_file_path.stem}.json"
        csv_file = output_dir / f"{saved_file_path.stem}.csv"

        save_to_json(result, json_file)
        save_to_csv(result, csv_file)

        with open(json_file, "rb") as jf:
            st.download_button(
                label="Download JSON",
                data=jf,
                file_name=json_file.name,
                mime="application/json"
            )

        with open(csv_file, "rb") as cf:
            st.download_button(
                label="Download CSV",
                data=cf,
                file_name=csv_file.name,
                mime="text/csv"
            )

        st.json(result)

    except Exception as e:
        st.error(f"Error while parsing resume: {e}")
