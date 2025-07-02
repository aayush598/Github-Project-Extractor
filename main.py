# main.py
"""
Updated main entry‑point for:
  • Single‑repo clone → extract → store workflow
  • NEW automatic multi‑repo ideation workflow
"""

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
)
from utils.helpers import parse_llm_summary
from github_search import search_similar_repositories

# ─────────────────────────────────────────────────────────────────────────────
#  Initialise DB + Streamlit
# ─────────────────────────────────────────────────────────────────────────────
init_db()

st.set_page_config(
    page_title="GitHub Extractor & Ideator",
    page_icon="🔍",
    layout="wide",
)
st.title("🔍 GitHub Extractor  &  💡 Feature Ideator")

# ─────────────────────────────────────────────────────────────────────────────
#  Tabs for the two workflows
# ─────────────────────────────────────────────────────────────────────────────
tab_single, tab_multi = st.tabs(
    ["Single‑Repo Extractor", "Multi‑Repo Ideation"]
)

# ════════════════════════════════════════════════════════════════════════════
#  1️⃣  Single‑Repository workflow  (clone → extract → store)
# ════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.header("Single Repository Workflow")

    repo_url = st.text_input(
        "Enter GitHub Repository URL",
        placeholder="https://github.com/owner/project",
    )

    if st.button("Clone, Parse, Analyze, and Store", key="single"):
        if not repo_url.strip():
            st.warning("Please enter a repository URL.")
            st.stop()

        # ── Clone ──────────────────────────────────────────────────────────
        with st.spinner("Cloning repository…"):
            repo_path = clone_repo(repo_url)
        if not repo_path:
            st.error("Cloning failed — see logs for details.")
            st.stop()
        st.success(f"✅ Repository cloned to **{repo_path}**")

        # ── Parse repo ────────────────────────────────────────────────────
        repo_data = parse_repo(repo_path)
        if repo_data["readme"]:
            st.subheader("README (truncated to 1 000 chars)")
            st.code(
                repo_data["readme"][:1000]
                + (" …" if len(repo_data["readme"]) > 1000 else "")
            )

        # ── LLM summarisation ─────────────────────────────────────────────
        with st.spinner("Analyzing with Groq LLM…"):
            llm_summary = extract_features_and_techstack(repo_data)

        st.markdown("### LLM Summary")
        st.markdown(llm_summary)

        # ── Parse & store in DB ───────────────────────────────────────────
        features, tech_stack = parse_llm_summary(llm_summary)

        project_id = insert_project(repo_url, repo_path)
        insert_features(project_id, features)
        insert_tech_stack(project_id, tech_stack)

        st.success("🎉 Project info stored in database!")
        col1, col2 = st.columns(2)
        col1.metric("Features Extracted", len(features))
        col2.metric("Tech‑Stack Items", len(tech_stack))

# ════════════════════════════════════════════════════════════════════════════
#  2️⃣  Multi‑Repository workflow  (search → batch‑process → ideate)
# ════════════════════════════════════════════════════════════════════════════
with tab_multi:
    st.header("Automatic Multi‑Repository Workflow")

    query = st.text_input(
        "Describe your project or enter keywords to search GitHub:",
        placeholder="e.g. real‑time chat app socket.io",
        key="query",
    )
    max_repos = st.slider(
        "Number of top GitHub repos to process",
        min_value=1,
        max_value=10,
        value=3,
        key="max_repos",
    )

    if st.button("Run Multi‑Repo Ideation", key="multi"):
        if not query.strip():
            st.warning("Please provide a search query / project description.")
            st.stop()

        # ── GitHub search ────────────────────────────────────────────────
        with st.spinner(f"Searching GitHub for “{query}”…"):
            repo_candidates = search_similar_repositories(query, max_repos)

        if not repo_candidates:
            st.error("No repositories found. Try different keywords.")
            st.stop()

        st.success(f"🔗 Found {len(repo_candidates)} repositories")

        for r in repo_candidates:
            st.markdown(f"- **[{r['name']}]({r['url']})**")

        # ── Process each repo ────────────────────────────────────────────
        aggregated_features: list[str] = []

        for repo in repo_candidates:
            st.write("---")
            st.subheader(f"📦 Processing **{repo['name']}**")

            with st.spinner("Cloning…"):
                local_path = clone_repo(repo["url"])
            if not local_path:
                st.error("Clone failed, skipping this repository.")
                continue

            with st.spinner("Parsing repository…"):
                repo_data = parse_repo(local_path)

            with st.spinner("Extracting features with Groq LLM…"):
                summary = extract_features_and_techstack(repo_data)
            features, _ = parse_llm_summary(summary)

            if features:
                st.markdown("**Extracted Features:**")
                for f in features:
                    st.markdown(f"- {f}")
                aggregated_features.extend(features)
            else:
                st.info("_No features extracted from this repo._")

        # ── Aggregate & deduplicate features ─────────────────────────────
        unique_features: list[str] = []
        seen: set[str] = set()
        for feat in aggregated_features:
            if feat not in seen:
                seen.add(feat)
                unique_features.append(feat)

        if not unique_features:
            st.warning("No features were extracted from any repository.")
            st.stop()

        st.subheader("📋 Aggregated Feature Set")
        for f in unique_features:
            st.markdown(f"- {f}")

        # ── Ideate new features via Groq LLM ─────────────────────────────
        with st.spinner("Generating new feature ideas…"):
            ideas_text = suggest_new_features_from_features(
                "\n".join(unique_features)
            )

        st.subheader("💡 Suggested New Features")
        st.markdown(ideas_text)
