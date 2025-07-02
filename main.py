# main.py

import streamlit as st
from extractor.clone_repo import clone_repo
from extractor.parse_repo import parse_repo
from extractor.summarizer import extract_features_and_techstack
from database.db import init_db, insert_project, insert_features, insert_tech_stack
from utils.helpers import parse_llm_summary

init_db()

st.title("GitHub Extractor")

repo_url = st.text_input("Enter GitHub Repository URL")


if st.button("Clone, Parse, Analyze, and Store"):
    if repo_url:
        repo_path = clone_repo(repo_url)
        if repo_path:
            st.success(f"Repository cloned to {repo_path}")
            repo_data = parse_repo(repo_path)

            st.subheader("README")
            st.code(repo_data["readme"][:500] + "...")

            with st.spinner("Analyzing with Groq LLM..."):
                llm_summary = extract_features_and_techstack(repo_data)
                st.markdown(llm_summary)

                # Parse summary into structured lists
                features, tech_stack = parse_llm_summary(llm_summary)

                # Insert into DB
                project_id = insert_project(repo_url, repo_path)
                insert_features(project_id, features)
                insert_tech_stack(project_id, tech_stack)

                st.success("Project info stored in database!")
                st.markdown(f"**Features Extracted:** {len(features)}")
                st.markdown(f"**Tech Stack Items Extracted:** {len(tech_stack)}")
