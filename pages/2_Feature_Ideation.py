# main.py

import streamlit as st
from github_search import search_similar_repositories
from extractor.clone_repo import clone_repo
from extractor.parse_repo import parse_repo
from extractor.summarizer import extract_features_and_techstack, suggest_new_features_from_features
from utils.helpers import parse_llm_summary

# existing UI code...

st.markdown("---")
st.subheader("📦 Automatic Multi-Repo Ideation Workflow")

query = st.text_input("Enter project description for auto GitHub search:")

max_repos = st.slider("Number of repos to fetch and process", min_value=1, max_value=10, value=3)

if st.button("🔄 Run Multi-Repo Ideation"):
    if not query:
        st.warning("Please enter a project description.")
    else:
        with st.spinner(f"Searching GitHub for top {max_repos} repos..."):
            repo_list = search_similar_repositories(query, max_repos)

        st.write(f"✅ Found {len(repo_list)} repos:")
        aggregated_features = []

        for repo in repo_list:
            st.write(f"- {repo['name']} — {repo['url']}")

        # Clone & extract from each
        for repo in repo_list:
            st.spinner(f"Cloning {repo['name']}...")
            path = clone_repo(repo['url'])
            if not path:
                st.error(f"Failed to clone {repo['name']}")
                continue

            st.spinner(f"Extracting from {repo['name']}...")
            repo_data = parse_repo(path)
            llm_summary = extract_features_and_techstack(repo_data)
            features, _ = parse_llm_summary(llm_summary)

            st.write(f"🔹 Features from {repo['name']}:")
            for f in features:
                st.write(f"- {f}")

            aggregated_features.extend(features)

        # Deduplicate
        aggregated_features = list(dict.fromkeys(aggregated_features))
        st.subheader("📋 Aggregated Feature List from All Repos")
        for f in aggregated_features:
            st.write(f"- {f}")

        if aggregated_features:
            combined = "\n".join(aggregated_features)
            with st.spinner("Generating new feature ideas via Groq..."):
                new_ideas = suggest_new_features_from_features(combined)

            st.subheader("💡 New Feature Ideas")
            st.text(new_ideas)
        else:
            st.warning("No features extracted from repos.")
