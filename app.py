import streamlit as st
import os
import json

# --- SETUP: Session state for projects, auth, files, history ---
if "projects" not in st.session_state:
    st.session_state.projects = [{"name": "Demo Project", "desc": "Sample project", "pinned": False, "history": []}]
if "selected_project" not in st.session_state:
    st.session_state.selected_project = 0
if "code_file_content" not in st.session_state:
    st.session_state.code_file_content = ""
if "github_token" not in st.session_state:
    st.session_state.github_token = ""
if "gitlab_token" not in st.session_state:
    st.session_state.gitlab_token = ""
if "gmail_logged_in" not in st.session_state:
    st.session_state.gmail_logged_in = False
if "ci_cd_prompt" not in st.session_state:
    st.session_state.ci_cd_prompt = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = ""

# --- Modern CSS for UI ---
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
# --- GMAIL LOGIN (OAUTH MOCKUP) ---
def gmail_login_button():
    if not st.session_state.gmail_logged_in:
        if st.button("🔗 One-click Gmail Login"):
            # --- TODO: Replace with real OAuth flow for Gmail/Google API ---
            st.session_state.gmail_logged_in = True
            st.success("Logged in with Gmail! (OAuth2 flow placeholder)")
    else:
        st.success("Gmail Connected!")

# --- GITHUB LOGIN ---
def github_login_form():
    if st.session_state.github_token:
        st.success("GitHub Connected!")
    else:
        token = st.text_input("GitHub Personal Access Token", type="password")
        if st.button("Connect GitHub"):
            # --- TODO: Validate via GitHub API ---
            if token.strip():
                st.session_state.github_token = token.strip()
                st.success("GitHub Connected!")
            else:
                st.error("Enter your GitHub token.")

# --- GITLAB LOGIN ---
def gitlab_login_form():
    if st.session_state.gitlab_token:
        st.success("GitLab Connected!")
    else:
        token = st.text_input("GitLab Personal Access Token", type="password", key="gitlab_token")
        if st.button("Connect GitLab"):
            # --- TODO: Validate via GitLab API ---
            if token.strip():
                st.session_state.gitlab_token = token.strip()
                st.success("GitLab Connected!")
            else:
                st.error("Enter your GitLab token.")

# --- PROJECT MANAGEMENT ---
def new_project_form():
    with st.form("new_project_form", clear_on_submit=True):
        pname = st.text_input("New Project Name")
        pdesc = st.text_area("Description")
        submitted = st.form_submit_button("Create Project")
        if submitted and pname:
            st.session_state.projects.append({
                "name": pname, "desc": pdesc, "pinned": False, "history": []
            })
            st.success(f"Project '{pname}' created.")

def project_selector():
    proj_names = [f"{p['name']} {'📌' if p['pinned'] else ''}" for p in st.session_state.projects]
    idx = st.selectbox("Select Project", range(len(proj_names)), format_func=lambda i: proj_names[i])
    st.session_state.selected_project = idx
    p = st.session_state.projects[idx]
    pin, unpin = st.columns(2)
    with pin:
        if st.button("📌 Pin", key=f"pin_{idx}"):
            st.session_state.projects[idx]["pinned"] = True
    with unpin:
        if st.button("❌ Unpin", key=f"unpin_{idx}"):
            st.session_state.projects[idx]["pinned"] = False
    st.markdown(f"**{p['name']}** — {p['desc']}")

# --- FILE UPLOAD / EDIT ---
def safe_file_upload():
    file = st.file_uploader("Upload a code file", type=["py","js","html","json","yaml","yml","sh","c","cpp","java","ts","rb","php","cs","go","ipynb"], key="upload_file_editor")
    content = ""
    if file:
        try:
            content = file.read().decode("utf-8")
            st.session_state.code_file_content = content
            st.success("File uploaded!")
        except Exception:
            st.error("Could not read file as text.")
    return st.session_state.code_file_content

# --- HOMEPAGE ---
if nav == "Home":
    st.markdown('<div class="page-title">Home</div>', unsafe_allow_html=True)
    st.text_input("🔎 Global Search", placeholder="Find projects, files, team...", key="global_search")
    st.markdown("### Quick Actions")
    qcols = st.columns([1,1,1,1])
    with qcols[0]: new_project_form()
    with qcols[1]: st.button("⬆️ Import Project", help="Import from repo")
    with qcols[2]: st.button("📂 Open File", help="Browse files")
    with qcols[3]: gmail_login_button()
    st.markdown("### My Projects")
    for idx, p in enumerate(st.session_state.projects):
        st.markdown(
            f"<div class='card project-card'>"
            f"<b>{p['name']}</b> {'<span class=\"pinned\">📌</span>' if p['pinned'] else ''}<br>"
            f"<span class='team-badge'>History: {len(p['history'])} edits</span><br>"
            f"{p['desc']}<br>"
            f"<button class='pin-btn' onclick='window.location.reload();'>{'Unpin' if p['pinned'] else 'Pin'}</button>"
            "</div>",
            unsafe_allow_html=True
        )

# --- PROJECT DASHBOARD ---
elif nav == "Projects":
    st.markdown('<div class="page-title">Project Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="breadcrumb">Projects / Dashboard</div>', unsafe_allow_html=True)
    project_selector()
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
        st.write("Project files browser here...")
    with tabs[2]:
        st.write("Team management UI here... [Invite Member]")
    with tabs[3]:
        st.write("CI/CD pipeline, logs, run controls, and visualizations here...")
    with tabs[4]:
        st.write("Project-specific settings...")

# --- FILE EDITOR PAGE ---
elif nav == "Editor":
    st.markdown('<div class="page-title">Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="breadcrumb">Projects / Editor</div>', unsafe_allow_html=True)
    etabs = st.tabs(["Code", "Preview", "History"])
    with etabs[0]:
        code_val = safe_file_upload()
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

    # Sticky header mock, draggable panels mock (Streamlit doesn't support drag-resize natively)
    st.markdown("<div class='sticky'>File: index.html | [Save] [Upload] [Revisions] [Pin]</div>", unsafe_allow_html=True)
    st.markdown("----")
    st.markdown("#### AI Assistant")
    prompt = st.text_input("Ask for code correction (GitHub/Gemini):")
    github_login_form()
    if st.button("Correct Code Now (GitHub + AI)"):
        # --- TODO: Add Gemini/GitHub code correction logic here! ---
        st.session_state.ai_feedback = "Corrected code would be shown here."
        st.success(st.session_state.ai_feedback)

# --- PIPELINES PAGE ---
elif nav == "Pipelines":
    st.markdown('<div class="page-title">Pipelines</div>', unsafe_allow_html=True)
    ptabs = st.tabs(["Pipelines", "Templates", "History"])
    with ptabs[0]:
        st.markdown("#### Create/Manage Pipeline")
        st.text_input("Pipeline Name")
        gitlab_login_form()
        ci_cd_prompt = st.text_area("Paste your GitLab CI YAML here for AI correction:", key="cicd_yaml")
        if st.button("AI Correct GitLab CI/CD Pipeline"):
            # --- TODO: Replace with Gemini AI logic for YAML correction ---
            st.session_state.ci_cd_prompt = "Corrected YAML and explanation would go here."
            st.success(st.session_state.ci_cd_prompt)
        st.markdown("#### Visual Pipeline (mock)")
        st.info("Interactive pipeline graph would go here.")
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
        gmail_login_button()
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
