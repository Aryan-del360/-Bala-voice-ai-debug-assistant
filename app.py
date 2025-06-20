import streamlit as st

# ---- Custom CSS for your modern UI ----
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans', sans-serif;
        background: #f0f2f5;
        color: #111418;
    }
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #0c7ff2;
    }
    .nav-link {
        padding: 0.6em 1.2em;
        margin-bottom: 0.3em;
        border-radius: 10px;
        font-weight: 600;
        color: #111418;
        text-decoration: none;
        display: block;
        transition: background 0.15s;
    }
    .nav-link.selected, .nav-link:hover {
        background: #e6f2ff;
        color: #0c7ff2;
    }
    .page-title {
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 0.7em;
        color: #111418;
    }
    .tab-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0c7ff2;
    }
    .modern-btn {
        background: #0c7ff2;
        color: #fff;
        border-radius: 8px;
        padding: 0.5em 1.4em;
        font-weight: 700;
        margin-top: 1em;
        transition: background 0.13s;
        border: none;
    }
    .modern-btn:hover {
        background: #0a6cce;
        color: white;
    }
    .progress-bar-bg { background: #dbe0e6; border-radius: 7px; height: 15px; }
    .progress-bar-fill { background: #0c7ff2; border-radius: 7px; height: 15px; transition: width 0.5s; }
    </style>
""", unsafe_allow_html=True)

# ---- Sidebar Navigation ----
st.sidebar.markdown('<div class="sidebar-title">CodeHub</div>', unsafe_allow_html=True)
pages = {
    "Home": "🏠 Home",
    "Projects": "📁 Projects",
    "Editor": "📝 Editor",
    "Pipelines": "🚀 Pipelines",
    "Settings": "⚙️ Settings"
}
selected = st.sidebar.radio("Navigation", list(pages.keys()), format_func=lambda x: pages[x])

# ---- PAGE 1: Home ----
if selected == "Home":
    st.markdown('<div class="page-title">Home</div>', unsafe_allow_html=True)
    st.write("Welcome back, Alex! Here's an overview of your projects and recent activity.")
    st.write("Recent Activity, Quick Actions, Notifications... (build these as you wish)")

# ---- PAGE 2: Projects ----
elif selected == "Projects":
    st.markdown('<div class="page-title">Projects</div>', unsafe_allow_html=True)
    # Example grid
    cols = st.columns(2)
    with cols[0]:
        st.image("https://lh3.googleusercontent.com/aida-public/AB6AXuAczTRRgOd4LTPkCtFLHlKltv7pait1rx9noDVi4ajLzPyctROxhrxjnQ2YryUOq_SpGE0YaTsSDGeM0ecoqHK5LMgiEfcRpJb6wHF8xBjey6DX2g2ANNhT7PrQAHCVa9YXEG1hpbS_hjKkPno6JrC2H8xv5rkM_0UyUv6OJMIKz3GzGXuC-WCQjkaowTHejQKcUUfL2t5UJpjVueK20SG-e0-6XkvIW8ETXYv9AWI4fxKi1B44fIg_JV4MNbpWrkvpAn6shNqIMw", width=200)
        st.write("**Project Alpha**\nLast updated 2 days ago\nTeam: Avengers")
    with cols[1]:
        st.image("https://lh3.googleusercontent.com/aida-public/AB6AXuClWHpXaU41l6w3BgRVE08NPEXZC9YG-ZRgkJ2wzPk2nihIpC4nSpREiNP5imbOGAwNG_Zkj5xPJ5dRrucFFD61wZGNIggUvu4rg3nwvYeh8d_4Ci7QK8yKhVTkF1DACcehV4aZvY_9TJJqlSjBg0Fc3DZt06C25k6mtX1zgJ8l8UnPmsrjmrRkm19CwNqngOT4NpKGag8ydP1vz0K_d6VMEo9YaQsnT9KSpzNQlBNe4fV2AcJyJMmY-4RzEnQlMs2bjDzq_aCH3A", width=200)
        st.write("**Project Beta**\nLast updated 1 week ago\nTeam: Justice League")

# ---- PAGE 3: Editor ----
elif selected == "Editor":
    st.markdown('<div class="page-title">Editor: index.html</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Code", "Preview", "History"])
    with tabs[0]:
        code = st.text_area("Edit your code:", height=300, value="<!-- Your HTML code here -->")
        st.button("Run", key="run_code_editor", help="Run or preview your code")
    with tabs[1]:
        st.write("Live Preview will appear here.")
    with tabs[2]:
        st.write("File revision history...")

    # Sidebar: AI Assistant
    st.markdown("---")
    st.markdown("#### AI Assistant")
    st.text_input("Ask a coding question...")
    st.button("Send")

# ---- PAGE 4: Pipelines ----
elif selected == "Pipelines":
    st.markdown('<div class="page-title">Pipelines</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Pipelines", "Templates", "History"])
    with tabs[0]:
        st.write("Pipeline list, create new pipeline, visual pipeline builder, etc.")
    with tabs[1]:
        st.write("Prebuilt pipeline templates...")
    with tabs[2]:
        st.write("Pipeline run history...")

# ---- PAGE 5: Settings ----
elif selected == "Settings":
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    setting_tabs = st.tabs(["Account", "Preferences", "Notifications", "Team"])
    with setting_tabs[0]:
        st.text_input("Name", value="Alex Johnson")
        st.text_input("Email", value="alex.johnson@example.com")
        st.text_input("Username", value="alexj")
        st.text_input("Password", type="password")
        st.button("Update Account")
    with setting_tabs[1]:
        st.write("User preferences here...")
    with setting_tabs[2]:
        st.write("Notification preferences here...")
    with setting_tabs[3]:
        st.write("Team management here...")

# ---- Footer ----
st.markdown('<hr>')
st.markdown(
    '<div style="text-align:center; color:#60758a; font-size:0.95em;">'
    'Inspired by Gemini Canvas & Stitch UI · <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#0c7ff2;">GitHub Repo</a>'
    '</div>',
    unsafe_allow_html=True
)
