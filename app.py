import streamlit as st

# --------- Session State Initialization ---------
if "projects" not in st.session_state:
    st.session_state.projects = []
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "github_token" not in st.session_state:
    st.session_state.github_token = ""
if "gitlab_token" not in st.session_state:
    st.session_state.gitlab_token = ""
if "gmail_logged_in" not in st.session_state:
    st.session_state.gmail_logged_in = False
if "editor_content" not in st.session_state:
    st.session_state.editor_content = ""
if "editor_history" not in st.session_state:
    st.session_state.editor_history = []
if "ci_cd_yaml" not in st.session_state:
    st.session_state.ci_cd_yaml = ""
if "ci_cd_history" not in st.session_state:
    st.session_state.ci_cd_history = []
if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "Home"

# --------- CSS Styling for Modern UI ---------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans', sans-serif !important; }
.sidebar-title { font-size: 1.6rem; font-weight: 900; margin-bottom: 2.5rem; color: #0c7ff2; }
.top-bar { display: flex; align-items: center; gap: 1.5em; background: #fff; padding: 1em 2em; border-radius: 0 0 18px 18px; box-shadow: 0 2px 8px #0c7ff210; margin-bottom: 1em;}
.top-bar input { flex: 1; padding: 0.5em 1em; border-radius: 7px; border: 1px solid #dbe0e6; }
.project-card { background: #fff; border-radius: 18px; box-shadow: 0 2px 10px #0001; padding: 1.2em; transition: box-shadow 0.2s;}
.project-card.selected, .project-card:hover { box-shadow: 0 4px 20px #0c7ff220; border: 1.5px solid #0c7ff2; }
.pin-btn { background: none; border: none; cursor: pointer; font-size: 1.2em; color: #f59e0b; float: right;}
.tab-header { font-size: 1.1rem; font-weight: 600; color: #0c7ff2; margin-bottom: 1em; }
.progress-bar-bg { background: #dbe0e6; border-radius: 7px; height: 13px; }
.progress-bar-fill { background: #0c7ff2; border-radius: 7px; height: 13px; transition: width 0.5s;}
.action-btn { background: #0c7ff2; color: #fff; border-radius: 8px; padding: 0.3em 1.2em; font-weight: 700; border: none; margin: 0.2em;}
.action-btn:hover { background: #095dbf;}
input[type="file"] { color: #111418 !important; }
hr {margin-top: 2em; margin-bottom: 1em;}
</style>
""", unsafe_allow_html=True)

# --------- Top Bar: Global Search & Quick Actions ---------
with st.container():
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)
    search = st.text_input("🔎 Search projects/files/team...", key="search_global", label_visibility="collapsed", placeholder="Search projects, files, team...")
    st.button("➕ New Project", on_click=lambda: st.session_state.update(ui_mode="NewProject"), use_container_width=False)
    st.button("📁 Select Project", on_click=lambda: st.session_state.update(ui_mode="SelectProject"), use_container_width=False)
    st.button("📤 Upload File", on_click=lambda: st.session_state.update(ui_mode="Editor"), use_container_width=False)
    st.button("📌 Pinned", on_click=lambda: st.session_state.update(ui_mode="Pinned"), use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Sidebar Navigation ---------
st.sidebar.markdown('<div class="sidebar-title">Bala Coding Agent</div>', unsafe_allow_html=True)
ui_page = st.sidebar.radio(
    "Navigate", ["Home", "Projects", "Editor", "CI/CD", "Integrations", "Settings"],
    index=["Home", "Projects", "Editor", "CI/CD", "Integrations", "Settings"].index(st.session_state.get("ui_mode", "Home"))
)
st.session_state.ui_mode = ui_page

# --------- Gmail / GitHub / GitLab Login Buttons ---------
def show_integrations():
    st.header("Integrations")
    st.subheader("Gmail (Google) Login")
    if st.session_state.gmail_logged_in:
        st.success("Gmail connected!")
    elif st.button("🔗 Login with Gmail"):
        # TODO: Insert OAuth logic here
        st.session_state.gmail_logged_in = True
        st.success("Gmail connected (stub).")
    st.subheader("GitHub Login")
    if st.session_state.github_token:
        st.success("GitHub connected.")
    else:
        token = st.text_input("GitHub Token", type="password", key="github_token_input")
        if st.button("Connect GitHub"):
            st.session_state.github_token = token.strip()
            st.success("GitHub connected (stub).")
    st.subheader("GitLab Login")
    if st.session_state.gitlab_token:
        st.success("GitLab connected.")
    else:
        token = st.text_input("GitLab Token", type="password", key="gitlab_token_input")
        if st.button("Connect GitLab"):
            st.session_state.gitlab_token = token.strip()
            st.success("GitLab connected (stub).")

# --------- Project Management ---------
def list_projects(pinned_only=False):
    projs = [p for p in st.session_state.projects if p.get("pinned")] if pinned_only else st.session_state.projects
    grid = st.columns(3)
    for i, p in enumerate(projs):
        with grid[i % 3]:
            sel = st.button("Open", key=f"open_proj_{i}", help="Open this project")
            pin = st.button("📌" if not p["pinned"] else "Unpin", key=f"pin_proj_{i}")
            if pin:
                p["pinned"] = not p["pinned"]
            if sel:
                st.session_state.selected_project = i
                st.session_state.ui_mode = "Projects"
            st.markdown(
                f"<div class='project-card{' selected' if st.session_state.selected_project==i else ''}'>"
                f"<b>{p['name']}</b> {'📌' if p['pinned'] else ''}<br>"
                f"<span class='team-badge'>Edits: {len(p['history'])}</span><br>{p['desc']}</div>",
                unsafe_allow_html=True
            )

def create_new_project():
    with st.form("new_proj_form"):
        pname = st.text_input("Project Name")
        pdesc = st.text_area("Description")
        pin = st.checkbox("Pin project")
        submit = st.form_submit_button("Create Project")
        if submit and pname:
            st.session_state.projects.append({"name": pname, "desc": pdesc, "pinned": pin, "history": []})
            st.success(f"Created project '{pname}'")
            st.session_state.ui_mode = "Projects"

def select_project():
    if not st.session_state.projects:
        st.info("No projects. Create a new one.")
        return
    idx = st.selectbox("Select Project", list(range(len(st.session_state.projects))),
                       format_func=lambda i: st.session_state.projects[i]["name"])
    st.session_state.selected_project = idx
    st.session_state.ui_mode = "Projects"

# --------- Editor ---------
def editor_page():
    st.header("Editor")
    uploaded = st.file_uploader("Upload code file", type=["py","js","html","json","yaml","yml","sh","c","cpp","java","ts","rb","php","cs","go","ipynb"])
    if uploaded:
        try:
            content = uploaded.read().decode("utf-8")
            st.session_state.editor_content = content
            st.success("File uploaded!")
        except Exception:
            st.error("Could not read as text.")
    code = st.text_area("Edit your code:", value=st.session_state.editor_content, height=300)
    if st.button("Save to Project History"):
        idx = st.session_state.selected_project
        if idx is not None:
            st.session_state.projects[idx]["history"].append(code)
            st.session_state.editor_history.append(code)
            st.success("Saved to project history.")
    if st.button("Pin this Project", key="pin_editor"):
        idx = st.session_state.selected_project
        if idx is not None:
            st.session_state.projects[idx]["pinned"] = True
            st.success("Project pinned.")

    st.markdown("#### History")
    idx = st.session_state.selected_project
    if idx is not None:
        for i, h in enumerate(st.session_state.projects[idx].get("history", [])[-5:][::-1]):
            st.code(h[:200]+("..." if len(h)>200 else ""), language="python")

# --------- CI/CD Page ---------
def cicd_page():
    st.header("CI/CD Pipeline")
    st.info("Connect GitLab above for full features.")
    yaml = st.text_area("Paste your GitLab CI/CD YAML for AI correction",
                        value=st.session_state.ci_cd_yaml, height=150)
    if st.button("AI Correct Pipeline"):
        # TODO: Replace with Gemini/LLM integration
        st.session_state.ci_cd_history.append({"input": yaml, "output": "AI-corrected YAML here."})
        st.success("Pipeline corrected! (stub)")
    st.markdown("#### History")
    for h in st.session_state.ci_cd_history[-5:][::-1]:
        st.code(h["input"], language="yaml")
        st.success(h["output"])

# --------- Main UI Routing ---------
if ui_page == "Home":
    st.header("Welcome to Bala Coding Agent!")
    st.caption("Search, jump to projects, upload files, or use integrations from above. All features are dynamic. Use the sidebar to switch modules.")
    list_projects()
elif ui_page == "Pinned":
    st.header("Pinned Projects")
    list_projects(pinned_only=True)
elif ui_page == "NewProject":
    st.header("New Project")
    create_new_project()
elif ui_page == "SelectProject":
    st.header("Select Project")
    select_project()
elif ui_page == "Projects":
    idx = st.session_state.selected_project
    if idx is None or idx >= len(st.session_state.projects):
        st.info("No project selected.")
    else:
        p = st.session_state.projects[idx]
        st.header(f"{p['name']} Dashboard")
        tabs = st.tabs(["Overview", "Files", "Team", "CI/CD", "History"])
        with tabs[0]:
            st.write(p['desc'])
            st.success(f"Pinned: {'Yes' if p['pinned'] else 'No'}")
        with tabs[1]:
            st.write("Upload, browse, and edit files in Editor section.")
        with tabs[2]:
            st.write("Team management (invite, roles) coming soon.")
        with tabs[3]:
            cicd_page()
        with tabs[4]:
            st.write("Recent saves:")
            for h in p["history"][-5:][::-1]:
                st.code(h[:200]+("..." if len(h)>200 else ""), language="python")

elif ui_page == "Editor":
    editor_page()
elif ui_page == "CI/CD":
    cicd_page()
elif ui_page == "Integrations":
    show_integrations()
elif ui_page == "Settings":
    st.header("Settings")
    st.write("Profile, preferences, notifications, integrations.")
    show_integrations()

st.markdown('<hr>')
st.markdown(
    '<div style="text-align:center; color:#60758a; font-size:0.95em;">'
    'Inspired by Gemini Canvas & Stitch UI · <a href="https://github.com/Aryan-del360/-Bala-voice-ai-debug-assistant" target="_blank" style="color:#0c7ff2;">GitHub Repo</a>'
    '</div>',
    unsafe_allow_html=True
)
