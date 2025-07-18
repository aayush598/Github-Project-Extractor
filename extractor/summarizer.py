# extractor/summarizer.py

import os
from dotenv import load_dotenv
from groq import Groq
from utils.helpers import chunk_text

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_with_llm(prompt: str, model: str = "llama-3.1-8b-instant"):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] LLM summarization failed: {e}")
        return ""

def extract_features_and_techstack(repo_data):
    combined_text = repo_data["readme"] + "\n\n"
    for file in repo_data["files"]:
        combined_text += f"# File: {file['path']}\n{file['content']}\n\n"

    chunks = chunk_text(combined_text, max_length=3000)

    all_features = []
    all_tech_stack = []

    for idx, chunk in enumerate(chunks):
        prompt = (
            "Given the following project code and documentation, extract:\n"
            "1. A list of features with descriptions.\n"
            "2. The tech stack used in the project.\n\n"
            f"### INPUT CHUNK {idx+1} ###\n{chunk}\n"
        )

        summary = summarize_with_llm(prompt)
        all_features.append(f"Chunk {idx+1}:\n" + summary)

    final_prompt = (
        "Summarize all of the following LLM outputs into:\n"
        "1. Final list of major project features with brief descriptions.\n"
        "2. Final tech stack used (languages, libraries, tools, etc.)\n\n"
        f"### INPUT ###\n{'\n'.join(all_features)}"
    )

    final_summary = summarize_with_llm(final_prompt)
    return final_summary

def suggest_new_features_from_features(existing_features_text):
    """
    Suggests new features based on a list of existing features from similar projects.
    """
    prompt = (
        "Given the following extracted features from similar projects, "
        "suggest new and innovative features for the original idea:\n\n"
        f"{existing_features_text}\n\n"
        "### Suggested New Features with descriptions:"
    )
    return summarize_with_llm(prompt)

def suggest_new_tech_stack_from_tech_stack(existing_tech_stack_text: str, generated_features_text: str) -> str:
    """
    Suggests new tech stack components based on a list of existing tech stacks
    and the generated features for a new project.
    The output will be a newline-separated list of tech stack items, with no other information.
    """
    prompt = (
        "Based on the following existing tech stack components from similar projects "
        "and the generated features for a new project, suggest additional or alternative "
        "tech stack components that would be most beneficial.\n\n"
        "Existing Tech Stack:\n"
        f"{existing_tech_stack_text}\n\n"
        "Generated Features for the New Project:\n"
        f"{generated_features_text}\n\n"
        "Provide ONLY a list of tech stack components, with each item on a new line. "
        "Do NOT include any headings, introductory/concluding remarks, explanations, "
        "code blocks, or any other additional text. Just the tech stack items, one per line."
    )
    return summarize_with_llm(prompt)