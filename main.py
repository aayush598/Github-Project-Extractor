# main.py

import os
import streamlit as st

from extractor.clone_repo import clone_repo
from extractor.parse_repo import parse_repo
from extractor.summarizer import (
    extract_features_and_techstack,
    suggest_new_features_from_features,
)
from database.db import (
    init_db,
    insert_project,
    insert_features,
    insert_tech_stack,
    insert_ideated_features,  # ⬅️ Make sure this exists in db.py
)
from utils.helpers import parse_llm_summary
from github_search import search_similar_repositories

# ────────────────────────────────
#  Init
# ────────────────────────────────
init_db()
st.set_page_config(
    page_title="GitHub Extractor & Ideator",
    page_icon="🔍",
    layout="wide",
)
st.title("🔍 GitHub Extractor  &  💡 Feature Ideator")

tab_single, tab_multi = st.tabs(["Single‑Repo Extractor", "Multi‑Repo Ideation"])

# ────────────────────────────────
#  Single‑repo
# ────────────────────────────────
with tab_single:
    st.header("Single Repository Workflow")

    repo_url = st.text_input("Enter GitHub Repository URL", placeholder="https://github.com/owner/project")

    if st.button("Clone, Parse, Analyze, and Store", key="single"):
        if not repo_url.strip():
            st.warning("Please enter a repository URL.")
            st.stop()

        with st.spinner("Cloning repository…"):
            repo_path = clone_repo(repo_url)
        if not repo_path:
            st.error("Cloning failed.")
            st.stop()
        st.success(f"✅ Cloned to {repo_path}")

        repo_data = parse_repo(repo_path)

        if repo_data["readme"]:
            st.subheader("README")
            st.code(repo_data["readme"][:1000] + "..." if len(repo_data["readme"]) > 1000 else repo_data["readme"])

        with st.spinner("Analyzing with LLM…"):
            llm_summary = extract_features_and_techstack(repo_data)
        st.markdown("### LLM Summary")
        st.markdown(llm_summary)

        features, tech_stack = parse_llm_summary(llm_summary)

        project_id = insert_project(repo_url, repo_path)
        insert_features(project_id, features)
        insert_tech_stack(project_id, tech_stack)

        st.success("✅ Data stored in database!")
        col1, col2 = st.columns(2)
        col1.metric("Features", len(features))
        col2.metric("Tech Stack", len(tech_stack))

# ────────────────────────────────
#  Multi‑repo
# ────────────────────────────────
with tab_multi:
    st.header("Automatic Multi‑Repository Workflow")

    query = st.text_input("Enter keywords or app idea", placeholder="e.g. expense tracker react express")
    max_repos = st.slider("Number of repos to fetch", 1, 10, 3)

    if st.button("Run Multi‑Repo Ideation", key="multi"):
        if not query.strip():
            st.warning("Enter a search query first.")
            st.stop()

        with st.spinner("Searching GitHub…"):
            repo_candidates = search_similar_repositories(query, max_repos)

        if not repo_candidates:
            st.error("No repositories found.")
            st.stop()

        st.success(f"🔗 Found {len(repo_candidates)} repositories")

        for r in repo_candidates:
            st.markdown(f"- **[{r['name']}]({r['url']})**")

        aggregated_features = []

        for repo in repo_candidates:
            st.write("---")
            st.subheader(f"📦 Processing {repo['name']}")

            with st.spinner("Cloning…"):
                local_path = clone_repo(repo["url"])
            if not local_path:
                st.warning("Failed to clone.")
                continue

            repo_data = parse_repo(local_path)

            with st.spinner("Extracting features…"):
                summary = extract_features_and_techstack(repo_data)
            features, _ = parse_llm_summary(summary)

            if features:
                st.markdown("**Extracted Features:**")
                for f in features:
                    st.markdown(f"- {f}")
                aggregated_features.extend(features)
            else:
                st.info("_No features extracted._")

        # ── Aggregate & deduplicate ──────────────────────
        unique_features = list(dict.fromkeys(aggregated_features))

        if not unique_features:
            st.warning("No features extracted.")
            st.stop()

        st.subheader("📋 Aggregated Feature Set")
        for f in unique_features:
            st.markdown(f"- {f}")

        # ── Generate ideas ───────────────────────────────
        with st.spinner("Generating new features…"):
            ideas_text = suggest_new_features_from_features("\n".join(unique_features))

        st.subheader("💡 Suggested New Features")
        st.markdown(ideas_text)

        # ── Store in database ────────────────────────────
        with st.spinner("Storing in database…"):
            project_id = insert_project(f"[MultiRepo:{query}]", "virtual")
            insert_features(project_id, unique_features)
            insert_ideated_features(project_id, ideas_text)

        st.success("✅ All data stored!")
        st.balloons()
