import streamlit as st

# ----------------- Session State Setup -----------------
if "projects" not in st.session_state:
    st.session_state.projects = [
        {"name": "Demo Project", "desc": "Your first project!", "pinned": False, "history": []}
    ]
if "selected_project" not in st.session_state:
    st.session_state.selected_project = 0
if "code_file_content" not in st.session_state:
    st.session_state.code_file_content = ""
if "github_token" not in st.session_state:
    st.session_state.github_token = ""
if "gitlab_token" not in st.session_state:
    st.session_state.gitlab_token = ""
if "google_logged_in" not in st.session_state:
    st.session_state.google_logged_in = False

# ----------------- CSS Styling -----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans', sans-serif !important; }
.sidebar-title { font-size: 1.5rem; font-weight: 900; margin-bottom: 2.5rem; color: #0c7ff2; }
.page-title { font-size: 2.2rem; font-weight: 900; margin-bottom: 0.2em; color: #111418; }
.card { background: #fff; border-radius: 18px; box-shadow: 0 2px 10px #0001; padding: 1.5em; }
.project-card:hover { box-shadow: 0 4px 20px #0c7ff210; transform: scale(1.01);}
.team-badge { color: #60758a; font-size: 0.9em; background: #e6f2ff; border-radius: 7px; padding: 2px 10px;}
.pinned { color: #f59e0b; }
.pin-btn { background: none; border: none; cursor: pointer; font-size: 1.2em; }
input[type="file"] { color: #111418 !important; }
hr {margin-top: 2em; margin-bottom: 1em;}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined">
""", unsafe_allow_html=True)

# ----------------- Sidebar Navigation -----------------
st.sidebar.markdown('<div class="sidebar-title">Bala Coding Agent</div>', unsafe_allow_html=True)
nav = st.sidebar.radio(
    "Menu", ["Home", "Projects", "Editor", "Pipelines", "Settings"],
    format_func=lambda x: f"🏠 Home" if x=="Home" else
                          f"📁 Projects" if x=="Projects" else
                          f"📝 Editor" if x=="Editor" else
                          f"🚀 Pipelines" if x=="Pipelines" else
                          f"⚙️ Settings"
)

# ----------------- Auth/Login Helpers -----------------
def github_login():
    if st.session_state.github_token:
        st.success("GitHub Connected!")
    else:
        token = st.text_input("GitHub PAT (for private repo features)", type="password", key="githubpat")
        if st.button("Connect to GitHub"):
            if token.strip():
                st.session_state.github_token = token.strip()
                st.success("GitHub Connected!")
            else:
                st.error("Enter your GitHub token")

def gitlab_login():
    if st.session_state.gitlab_token:
        st.success("GitLab Connected!")
    else:
        token = st.text_input("GitLab Personal Access Token", type="password", key="gitlabpat")
        if st.button("Connect to GitLab"):
            if token.strip():
                st.session_state.gitlab_token = token.strip()
                st.success("GitLab Connected!")
            else:
                st.error("Enter your GitLab token")

def google_login():
    if st.session_state.google_logged_in:
        st.success("Google (Gmail) Connected!")
    else:
        if st.button("One-click Google Login"):
            # Insert your Google OAuth here!
            st.session_state.google_logged_in = True
            st.success("Google (Gmail) Connected! (stub)")

# ----------------- Project Management -----------------
def create_project():
    with st.form("new_project_form", clear_on_submit=True):
        pname = st.text_input("Project Name")
        pdesc = st.text_area("Description")
        submitted = st.form_submit_button("Create Project")
        if submitted and pname:
            st.session_state.projects.append({
                "name": pname, "desc": pdesc, "pinned": False, "history": []
            })
            st.success(f"Project '{pname}' created.")

def select_project():
    projects = st.session_state.projects
    names = [f"{p['name']}{' 📌' if p['pinned'] else ''}" for p in projects]
    idx = st.selectbox("Select Project", range(len(names)), format_func=lambda i: names[i], key="projselect")
    st.session_state.selected_project = idx
    p = projects[idx]
    pin, unpin = st.columns([1,1])
    with pin:
        if not p['pinned'] and st.button("📌 Pin", key=f"pin{idx}"):
            p['pinned'] = True
    with unpin:
        if p['pinned'] and st.button("❌ Unpin", key=f"unpin{idx}"):
            p['pinned'] = False
    st.markdown(f"**{p['name']}** — {p['desc']}")

# ----------------- File Upload/Edit -----------------
def code_file_upload():
    file = st.file_uploader("Upload a code file", type=["py","js","html","json","yaml","yml","sh","c","cpp","java","ts","rb","php","cs","go","ipynb"], key="file_upload")
    if file is not None:
        try:
            content = file.read().decode("utf-8")
            st.session_state.code_file_content = content
            st.success("File uploaded!")
        except Exception:
            st.error("Could not read file as text.")
    return st.session_state.code_file_content

# ----------------- Home -----------------
if nav == "Home":
    st.markdown('<div class="page-title">Home</div>', unsafe_allow_html=True)
    st.text_input("🔎 Global Search", placeholder="Find projects, files, or team...", key="search")
    st.markdown("### Quick Actions")
    qcols = st.columns([1,1,1,1])
    with qcols[0]: create_project()
    with qcols[1]: st.button("⬆️ Import Project")
    with qcols[2]: st.button("📂 Open File")
    with qcols[3]: 
        github_login()
        gitlab_login()
        google_login()

    st.markdown("### My Projects")
    for idx, p in enumerate(st.session_state.projects):
        st.markdown(
            f"<div class='card project-card'>"
            f"<b>{p['name']}</b> {'<span class=\"pinned\">📌</span>' if p['pinned'] else ''}<br>"
            f"<span class='team-badge'>History: {len(p['history'])} edits</span><br>"
            f"{p['desc']}"
            "</div>",
            unsafe_allow_html=True
        )

# ----------------- Projects -----------------
elif nav == "Projects":
    st.markdown('<div class="page-title">Projects</div>', unsafe_allow_html=True)
    select_project()
    tabs = st.tabs(["Overview", "Files", "Team", "CI/CD", "Settings"])
    with tabs[0]:
        st.write("Project Overview: status, summary, activity.")
    with tabs[1]:
        st.write("Files (upload, browse, manage).")
    with tabs[2]:
        st.write("Team (invite, manage).")
    with tabs[3]:
        st.write("CI/CD: see pipeline states, run pipeline, etc.")
    with tabs[4]:
        st.write("Project-specific settings.")

# ----------------- Editor -----------------
elif nav == "Editor":
    st.markdown('<div class="page-title">Editor</div>', unsafe_allow_html=True)
    etabs = st.tabs(["Code", "Preview", "History"])
    with etabs[0]:
        code_val = code_file_upload()
        code = st.text_area("Edit your code:", value=code_val, height=320, key="editor_code")
        if st.button("Save to History"):
            idx = st.session_state.selected_project
            p = st.session_state.projects[idx]
            p["history"].append({"code": code, "desc": "Manual save"})
            st.success("Code saved to history.")
        if st.button("Pin Project in Editor"):
            idx = st.session_state.selected_project
            st.session_state.projects[idx]["pinned"] = True
    with etabs[1]:
        st.write("Live Preview will appear here.")
    with etabs[2]:
        idx = st.session_state.selected_project
        p = st.session_state.projects[idx]
        st.write("History (last 5 saves):")
        for h in p["history"][-5:]:
            st.code(h["code"][:200] + ("..." if len(h["code"])>200 else ""), language="python")
            st.write(h.get("desc",""))
    st.markdown("----")
    st.markdown("#### AI Assistant")
    st.text_input("Ask for code correction (GitHub/Gemini):")
    github_login()

# ----------------- Pipelines -----------------
elif nav == "Pipelines":
    st.markdown('<div class="page-title">Pipelines</div>', unsafe_allow_html=True)
    ptabs = st.tabs(["Pipelines", "Templates", "History"])
    with ptabs[0]:
        st.text_input("Pipeline Name")
        gitlab_login()
        ci_cd_prompt = st.text_area("Paste your GitLab CI YAML here for AI correction:")
        if st.button("AI Correct GitLab CI/CD Pipeline"):
            st.info("This is where Gemini/GPT AI correction logic will run (plug in your model).")
    with ptabs[1]:
        st.write("Prebuilt pipeline templates...")
    with ptabs[2]:
        st.write("Pipeline run history...")

# ----------------- Settings -----------------
elif nav == "Settings":
    st.markdown('<div class="page-title">Settings</div>', unsafe_allow_html=True)
    settabs = st.tabs(["Account", "Preferences", "Notifications", "Team"])
    with settabs[0]:
        st.text_input("Name", value="Alex Johnson")
        st.text_input("Email", value="alex.johnson@example.com")
        st.text_input("Username", value="alexj")
        st.text_input("Password", type="password")
        st.button("Update Account")
        google_login()
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
