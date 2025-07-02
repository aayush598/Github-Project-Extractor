import streamlit as st
import sqlite3

DB_NAME = "extracted_data.db"

def get_all_repos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT repo_url FROM projects
        ORDER BY repo_url
    """)
    repos = cursor.fetchall()
    conn.close()
    return [repo[0] for repo in repos]

def search_data(table, repo_url, keyword):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    column_map = {
        "projects": "repo_url",
        "features": "feature",
        "tech_stack": "stack_item"
    }

    search_column = column_map.get(table)
    if not search_column:
        st.error(f"Invalid table selected: {table}")
        return []

    if table == "projects":
        query = f"SELECT * FROM projects WHERE repo_url LIKE ?"
        params = [f"%{keyword}%"]
    else:
        if repo_url == "All":
            query = f"""
                SELECT * FROM {table}
                WHERE {search_column} LIKE ?
            """
            params = [f"%{keyword}%"]
        else:
            query = f"""
                SELECT * FROM {table}
                WHERE project_id IN (
                    SELECT id FROM projects WHERE repo_url = ?
                ) AND {search_column} LIKE ?
            """
            params = [repo_url, f"%{keyword}%"]

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    st.title("📊 View Extracted GitHub Project Data")

    table = st.selectbox("Select Table to View", ["projects", "features", "tech_stack"])

    all_repos = get_all_repos()
    repo_options = ["All"] + all_repos
    selected_repo = st.selectbox("Select Repository", repo_options)

    keyword = st.text_input("Enter keyword to search", "")

    if st.button("🔍 Search"):
        results = search_data(table, selected_repo, keyword)

        if results:
            st.success(f"Found {len(results)} result(s)")
            st.write("### Results:")

            if table == "projects":
                st.dataframe(
                    [{"ID": r[0], "Repo URL": r[1], "Path": r[2], "Created At": r[3]} for r in results]
                )
            elif table == "features":
                st.dataframe(
                    [{"ID": r[0], "Project ID": r[1], "Feature": r[2]} for r in results]
                )
            elif table == "tech_stack":
                st.dataframe(
                    [{"ID": r[0], "Project ID": r[1], "Stack Item": r[2]} for r in results]
                )
        else:
            st.warning("No results found.")

if __name__ == "__main__":
    main()
