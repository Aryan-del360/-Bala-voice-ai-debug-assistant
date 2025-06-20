import streamlit as st

# --- Custom CSS for Modern Design, Icons, Animations ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans', sans-serif !important; }
.sidebar-title { font-size: 1.5rem; font-weight: 900; margin-bottom: 2.5rem; color: #0c7ff2; }
.page-title { font-size: 2.2rem; font-weight: 900; margin-bottom: 0.2em; color: #111418; }
.breadcrumb { font-size: 1em; color: #60758a; margin-bottom: 1.5em; }
.card { background: #fff; border-radius: 18px; box-shadow: 0 2px 10px #0001; padding: 1.5em; }
.project-card:hover { box-shadow: 0 4px 20px #0c7ff210; transform: scale(1.01); }
.project-image { border-radius: 12px 12px 0 0; }
.icon-btn { background: #f0f2f5; border-radius: 50%; padding: 0.7em; border: none; transition: background 0.15s; }
.icon-btn:hover { background: #e6f2ff; }
.quick-tip { font-size: 0.99em; color: #60758a; }
.sticky { position: sticky; top: 0; z-index: 9; background: white; }
.tab-header { font-size: 1.12rem; font-weight: 700; margin-right: 1.5em; }
.progress-bar-bg { background: #dbe0e6; border-radius: 7px; height: 15px; width: 100%; }
.progress-bar-fill { background: #0c7ff2; border-radius: 7px; height: 15px; transition: width 0.5s; }
.minimap { background: #f0f2f5; border-left: 2px solid #dbe0e6; font-size: 0.8em; color: #60758a; height: 220px; overflow: auto; }
.draggable { cursor: col-resize; }
@media (max-width: 900px) { .project-grid { grid-template-columns: 1fr 1fr !important; } }
@media (max-width: 600px) { .project-grid { grid-template-columns: 1fr !important; } }
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined">
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown('<div class="sidebar-title">Bala Coding Agent</div>', unsafe_allow_html=True)
nav = st.sidebar.radio(
    "Menu", ["Home", "Projects", "Editor", "Pipelines", "Settings"],
    format_func=lambda x: f"🏠 Home" if x=="Home" else
                          f"📁 Projects" if x=="Projects" else
                          f"📝 Editor" if x=="Editor" else
                          f"🚀 Pipelines" if x=="Pipelines" else
                          f"⚙️ Settings"
)

# --- HOMEPAGE ---
if nav == "Home":
    st.markdown('<div class="page-title">Home</div>', unsafe_allow_html=True)
    # Global Search Bar
    st.text_input("🔎  Global Search", placeholder="Find projects, files, or team members...", key="global_search")
    # Quick Action Buttons
    qcols = st.columns([1,1,1,1])
    with qcols[0]: st.button("➕ New Project", help="Create a project")
    with qcols[1]: st.button("⬆️ Import Project", help="Import from repo")
    with qcols[2]: st.button("📂 Open File", help="Browse files")
    with qcols[3]: st.button("👥 Invite", help="Invite teammate")
    st.markdown("### My Projects")
    # Project Grid
    st.markdown("""<div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1.5em;' class='project-grid'>""", unsafe_allow_html=True)
    for p in [
        ("Project Alpha", "2 days ago", "Avengers", "https://lh3.googleusercontent.com/aida-public/AB6AXuAczTRRgOd4LTPkCtFLHlKltv7pait1rx9noDVi4ajLzPyctROxhrxjnQ2YryUOq_SpGE0YaTsSDGeM0ecoqHK5LMgiEfcRpJb6wHF8xBjey6DX2g2ANNhT7PrQAHCVa9YXEG1hpbS_hjKkPno6JrC2H8xv5rkM_0UyUv6OJMIKz3GzGXuC-WCQjkaowTHejQKcUUfL2t5UJpjVueK20SG-e0-6XkvIW8ETXYv9AWI4fxKi1B44fIg_JV4MNbpWrkvpAn6shNqIMw"),
        ("Project Beta", "1 week ago", "Justice League", "https://lh3.googleusercontent.com/aida-public/AB6AXuClWHpXaU41l6w3BgRVE08NPEXZC9YG-ZRgkJ2wzPk2nihIpC4nSpREiNP5imbOGAwNG_Zkj5xPJ5dRrucFFD61wZGNIggUvu4rg3nwvYeh8d_4Ci7QK8yKhVTkF1DACcehV4aZvY_9TJJqlSjBg0Fc3DZt06C25k6mtX1zgJ8l8UnPmsrjmrRkm19CwNqngOT4NpKGag8ydP1vz0K_d6VMEo9YaQsnT9KSpzNQlBNe4fV2AcJyJMmY-4RzEnQlMs2bjDzq_aCH3A"),
        ("Project Gamma", "3 weeks ago", "X-Men", "https://lh3.googleusercontent.com/aida-public/AB6AXuB3OTJVCS-puQLQLbk4blPwksvbn6Sz-8lhmj0REjgqxZSeRwPphvbIs5NmM5VE-5I8wtNrCg-ILwDp51dv2o2AwxzzWoNuwADG5CGaGkawQPhw-CTlSbJEpuSLGsdNy3xxSLdC8ok6UouPDZJM915BK5BWQM5QF4v-0MlaTH6I2Ii3i5v_u59wxuZDdrnk8JQBuldwUMNPdJn86xlsC17OaAM6eoyyGer-y9PrAh65ujxamR4-RBQ-49EN9TXPst8x519svwAzSg"),
        ("Project Delta", "1 month ago", "Titans", "https://lh3.googleusercontent.com/aida-public/AB6AXuCHeiPGT4MrO98wXxyVZw9ZuvbMj0wdcoAeQqu2Iq3WEb2OdOtVzqsXbcyrX5kTaMaRtJLEcMxwQRaqapKTOMCAZ16WjeOdCKefj9KHv-1OA0GHwrVf93dqXN-tHZQ8x1f79QXG0kY_gWjMY8vKICj9FaswCmfQA5W7k8chsJS1BgurI9Lof3hKX1lxjEvMvzuh8UuFvTGBiIU7ABFalnJsSMJcE0sjWSEJv5w3zwCvWWPwjYhnNKNT6h4JXSJbQ2wbshb5Yg1GtQ"),
    ]:
        st.markdown(
            f"<div class='card project-card'>"
            f"<img src='{p[3]}' class='project-image' style='width:100%;height:130px;object-fit:cover;margin-bottom:0.7em;'/>"
            f"<b>{p[0]}</b><br>"
            f"<span style='color:#60758a;font-size:0.96em;'>Last updated {p[1]}</span><br>"
            f"<span class='team-badge'>{p[2]}</span></div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Recent Activity
    st.markdown("### Recent Activity")
    for text in [
        "Alex merged a merge request (2h ago)",
        "Sarah updated an issue (5h ago)",
        "System created a pipeline (1d ago)",
        "David assigned an issue (2d ago)"
    ]:
        st.write(f"• {text}")

    # Notifications
    st.markdown("### Notifications")
    st.info("🔔 Project Alpha pipeline failed — 3h ago")
    st.success("✅ New comment on issue #123 — Yesterday")

    st.markdown("<div class='quick-tip'>Tip: Use the sidebar to explore your workspace!</div>", unsafe_allow_html=True)

# --- PROJECT DASHBOARD ---
elif nav == "Projects":
    st.markdown('<div class="page-title">Project X</div>', unsafe_allow_html=True)
    st.markdown('<div class="breadcrumb">Projects / Project X / Overview</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Overview", "Files", "Team", "CI/CD", "Settings"])
    with tabs[0]:
        st.markdown("#### Project Status")
        c1, c2, c3 = st.columns(3)
        with c1: st.success("Build Status: Success (+5%)")
        with c2: st.success("Code Coverage: 95% (+2%)")
        with c3: st.success("Deployment: Deployed (+10%)")
        st.markdown("---")
        st.write("Recent project activity and summary goes here.")

    with tabs[1]:
        st.markdown('<div class="sticky">', unsafe_allow_html=True)
        st.write("Action Toolbar: [Add File] [Upload] [New Folder]")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("Project files browser here...")

    with tabs[2]:
        st.write("Team management UI here... [Invite Member]")

    with tabs[3]:
        st.write("CI/CD pipeline, logs, run controls, and visualizations here...")

    with tabs[4]:
        st.write("Project-specific settings...")

# --- FILE EDITOR PAGE ---
elif nav == "Editor":
    st.markdown('<div class="page-title">index.html</div>', unsafe_allow_html=True)
    st.markdown('<div class="breadcrumb">Projects / My Awesome Project / index.html</div>', unsafe_allow_html=True)
    etabs = st.tabs(["Code", "Preview", "History"])
    with etabs[0]:
        cols = st.columns([6,1])
        code = cols[0].text_area("Edit your code:", height=320, value="<!-- Your HTML code here -->")
        with cols[1]:
            st.markdown("<div class='minimap'>Minimap view of code</div>", unsafe_allow_html=True)
        st.button("Run", key="run_code_editor", help="Run or preview your code")
    with etabs[1]:
        st.write("Live Preview will appear here.")
    with etabs[2]:
        st.write("File revision history...")

    # Draggable Panels/Sticky Header mock
    st.markdown("<div class='sticky'>File: index.html | [Save] [Upload] [Revisions] [Delete]</div>", unsafe_allow_html=True)
    st.markdown("----")
    st.markdown("#### AI Assistant")
    st.text_input("Ask a coding question...", key="aiassistant")
    st.button("Send", key="sendai")

# --- PIPELINES PAGE ---
elif nav == "Pipelines":
    st.markdown('<div class="page-title">Pipelines</div>', unsafe_allow_html=True)
    ptabs = st.tabs(["Pipelines", "Templates", "History"])
    with ptabs[0]:
        st.markdown("#### Create/Manage Pipeline")
        st.text_input("Pipeline Name")
        st.selectbox("Source Code Repository", ["Select repository", "GitHub", "GitLab", "Bitbucket"])
        st.button("Connect to GitLab")
        st.markdown("#### **Pipeline Visual Graph** (coming soon)")
        # Example: use color for stage status
        cols = st.columns(4)
        stages = [("Trigger", "#0c7ff2", "Push to main"), ("Build", "#22c55e", "Success"), ("Test", "#3b82f6", "Running..."), ("Deploy", "#60758a", "Pending")]
        for i, (stage, color, status) in enumerate(stages):
            with cols[i]:
                st.markdown(
                    f"<div style='border:2px solid {color};border-radius:12px;padding:1em 0.6em;background:#f6fafd;margin-bottom:0.5em;text-align:center;'>"
                    f"<span class='material-icons-outlined' style='color:{color};font-size:2.3em;'>bolt</span><br>"
                    f"<b style='color:{color};'>{stage}</b><br><span>{status}</span></div>",
                    unsafe_allow_html=True
                )
        st.button("Run Pipeline")
    with ptabs[1]:
        st.write("Prebuilt pipeline templates...")
    with ptabs[2]:
        st.write("Pipeline run history...")

# --- SETTINGS PAGE ---
elif nav == "Settings":
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="breadcrumb">Settings / Account</div>', unsafe_allow_html=True)
    st.markdown("#### Profile Progress")
    st.markdown('<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:75%"></div></div>', unsafe_allow_html=True)
    st.caption("Profile Setup: 75%")
    st.markdown('<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:25%"></div></div>', unsafe_allow_html=True)
    st.caption("Team Setup: 25%")
    settabs = st.tabs(["Account", "Preferences", "Notifications", "Team"])
    with settabs[0]:
        st.text_input("Name", value="Alex Johnson")
        st.text_input("Email", value="alex.johnson@example.com")
        st.text_input("Username", value="alexj")
        st.text_input("Password", type="password")
        st.button("Update Account")
    with settabs[1]:
        st.write("User preferences here...")
    with settabs[2]:
        st.write("Notification preferences here...")
    with settabs[3]:
        st.write("Team management here...")

st.markdown('<hr>')
st.markdown(
    '<div style="text-align:center; color:#60758a; font-size:0.95em;">'
    'Inspired by Gemini Canvas & Stitch UI · <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#0c7ff2;">GitHub Repo</a>'
    '</div>',
    unsafe_allow_html=True
)
