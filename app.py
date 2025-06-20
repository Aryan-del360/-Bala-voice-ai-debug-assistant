import streamlit as st

github_token = st.secrets["GITHUB_TOKEN"]
gitlab_token = st.secrets["GITLAB_TOKEN"]

# For Gmail OAuth (example)
gmail_client_id = st.secrets["GMAIL_CLIENT_ID"]
gmail_client_secret = st.secrets["GMAIL_CLIENT_SECRET"]
gmail_refresh_token = st.secrets["GMAIL_REFRESH_TOKEN"]

# ------------------ Custom CSS for Vibrant UI ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background: linear-gradient(120deg, #6b47ff 0%, #0c7ff2 100%);}
.sidebar {background: #fff !important;}
.sidebar-title { font-size: 2.1rem; font-weight: 900; margin-bottom: 1.5rem; color: #0c7ff2;}
.nav-link { display: flex; align-items: center; font-size: 1.15rem; font-weight: 700; color: #222; border-radius: 10px; margin: 0.4em 0; padding: 0.7em 1em; transition: background 0.18s;}
.nav-link:hover, .nav-link.selected { background: #e0e7ff; color: #6b47ff;}
.fab { position: fixed; bottom: 34px; right: 34px; background: linear-gradient(90deg, #0c7ff2, #6b47ff); color: #fff; border-radius: 50%; width: 62px; height: 62px; font-size: 2.1em; box-shadow: 0 7px 25px #6b47ff44; border: none; cursor: pointer; z-index: 9;}
.card { background: #fff; border-radius: 18px; box-shadow: 0 2px 16px #0001; padding: 1.5em; margin-bottom: 1.2em;}
.project-badge { background: #22d3ee22; color: #0891b2; font-weight: 600; border-radius: 7px; padding: 0.2em 0.7em; margin-left: 0.6em;}
.action-btn { background: linear-gradient(90deg, #0c7ff2, #6b47ff); color: #fff; border-radius: 8px; border: none; font-weight: 700; padding: 0.45em 1.7em; margin: 0.2em 0.5em; transition: transform 0.11s;}
.action-btn:hover { transform: scale(1.08);}
.status-badge { padding: 0.2em 0.8em; border-radius: 8px; color: #fff; font-weight: 700; font-size: 0.92em;}
.status-success { background: #22c55e;}
.status-fail { background: #f87171;}
.status-running { background: #fbbf24; color: #18181b;}
.progress-bar-bg { background: #e5e7eb; border-radius: 7px; height: 13px;}
.progress-bar-fill { background: linear-gradient(90deg, #0c7ff2, #6b47ff); border-radius: 7px; height: 13px; transition: width 0.5s;}
.avatar { border-radius: 50%; width: 40px; height: 40px; object-fit: cover; margin-right: 0.7em;}
hr {margin-top: 1.2em; margin-bottom: 1.2em;}
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar Navigation ------------------
st.sidebar.markdown('<div class="sidebar-title">Bala Agent</div>', unsafe_allow_html=True)
nav = st.sidebar.radio(
    "", ["Home", "Projects", "Editor", "Pipelines", "Integrations", "Settings"],
    format_func=lambda x: f"🏠 {x}" if x == "Home" else f"📁 {x}" if x == "Projects" else f"📝 {x}" if x == "Editor" else f"🚀 {x}" if x == "Pipelines" else f"🔗 {x}" if x == "Integrations" else f"⚙️ {x}"
)

# ------------------ Top Bar ------------------
st.markdown("""
<div style='display: flex; align-items: center; justify-content: space-between; background: #fff9; padding: 1.2em 2em; border-radius: 0 0 17px 17px; box-shadow: 0 2px 8px #0c7ff215; margin-bottom: 1em;'>
    <input style="flex:1; font-size:1.1em; border-radius:7px; border:1px solid #dbe0e6; padding:0.5em 1em; margin-right:2em;" placeholder="🔎 Search projects, files, team..."/>
    <button class="action-btn">➕ New Project</button>
    <button class="action-btn">⬆️ Import</button>
    <button class="action-btn">📤 Upload File</button>
</div>
""", unsafe_allow_html=True)

# ------------------ Home/Dashboard ------------------
if nav == "Home":
    st.markdown("<h1 style='color:#0c7ff2'>Welcome to Bala Coding Agent!</h1>", unsafe_allow_html=True)
    # Example dynamic project cards
    cols = st.columns(3)
    for i, (name, badge, status) in enumerate([("Alpha", "Avengers", "success"), ("Beta", "Justice League", "fail"), ("Gamma", "X-Men", "running")]):
        with cols[i]:
            st.markdown(
                f"<div class='card'><b>{name}</b> <span class='project-badge'>{badge}</span><br>"
                f"<span class='status-badge status-{status}'>"
                f"{'Success' if status=='success' else 'Failure' if status=='fail' else 'Running'}</span></div>",
                unsafe_allow_html=True
            )
    st.markdown("<hr>", unsafe_allow_html=True)

# ------------------ Project Dashboard ------------------
elif nav == "Projects":
    st.markdown("<h2 style='color:#6b47ff'>Project Dashboard</h2>", unsafe_allow_html=True)
    st.button("➕ New Project", key="newprojbtn", help="Create a new project", use_container_width=True)
    st.markdown("<div class='card'>[Dynamic Project List with actions here]</div>", unsafe_allow_html=True)

# ------------------ Editor with Minimap and Git Integration ------------------
elif nav == "Editor":
    st.markdown("<h2 style='color:#6b47ff'>Editor</h2>", unsafe_allow_html=True)
    st.markdown("**Current Project:** Alpha (pulls from GitHub/GitLab)")
    col1, col2 = st.columns([4,1])
    with col1:
        code = st.text_area("Edit your code", height=350, value="# Write Python here")
    with col2:
        st.markdown("<div style='background:#eef2ff; border-radius:10px; min-height:320px; padding:0.7em;'>[Minimap]</div>", unsafe_allow_html=True)
    st.button("💾 Save", use_container_width=True)
    st.button("⬆️ Push to Repo", use_container_width=True)
    st.button("⬇️ Pull from Repo", use_container_width=True)

# ------------------ Pipelines ------------------
elif nav == "Pipelines":
    st.markdown("<h2 style='color:#6b47ff'>CI/CD Pipelines</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <b>Visual Pipeline:</b><br>
        <span class='status-badge status-success'>Build</span>
        <span class='status-badge status-running'>Test</span>
        <span class='status-badge status-fail'>Deploy</span>
        <br><br>
        <textarea style='width:100%;height:6em;border-radius:7px;'># Paste/Edit your GitLab CI YAML here</textarea>
        <br>
        <button class='action-btn'>🤖 AI Auto-Correct</button>
    </div>
    """, unsafe_allow_html=True)

# ------------------ Integrations ------------------
elif nav == "Integrations":
    st.markdown("<h2 style='color:#6b47ff'>Integrations</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <b>Gmail:</b> <button class='action-btn'>Login with Google</button><br>
        <b>GitHub:</b> <button class='action-btn'>Connect GitHub</button><br>
        <b>GitLab:</b> <button class='action-btn'>Connect GitLab</button><br>
        <i>Once connected, you can pull/push code and pipelines directly from/to your repos!</i>
    </div>
    """, unsafe_allow_html=True)

# ------------------ Settings ------------------
elif nav == "Settings":
    st.markdown("<h2 style='color:#6b47ff'>Settings</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <b>Profile:</b><br>
        Name: <input style='margin-left:1em;'><br>
        Email: <input style='margin-left:1em;'><br>
        <b>Preferences, Notifications, Team Setup, etc. here</b>
        <hr>
        <div class='progress-bar-bg'><div class='progress-bar-fill' style='width: 75%;'></div></div>
        <span>Profile Completion: 75%</span>
    </div>
    """, unsafe_allow_html=True)

# Floating Action Button (New Project)
st.markdown("<button class='fab' title='New Project'>+</button>", unsafe_allow_html=True)

st.markdown(
    "<hr><div style='text-align:center; color:#6b47ff; font-size:1em;'>"
    "Bala Coding Agent &copy; 2025 · <a href='https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
