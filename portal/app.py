import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from openai import OpenAI
import os
import base64

from supabase_db import (
    register_user,
    login_user,
    post_update,
    get_updates,
    delete_update,
    extract_links
)

from data import DOMAINS, COMPANIES, STATS, PLACEMENT_DIST, DOMAIN_PLACED, CHATBOT_SYSTEM_PROMPT

st.set_page_config(
    page_title="Department of Industrial Engineering Placement Portal 2025–26",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── API Key ────────────────────────────────────────────────────────────────────
AIPIPE_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2NzdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc3OTc0NTQyMiwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4MDM1MDIyMn0.Qj5gxNX9pJst6cCN10NK4dTuQCQ_uA1klsWThBtZTGw",
)
AIPIPE_BASE_URL = "https://aipipe.org/openai/v1"

# ── Session state defaults ─────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None


# ── Theme CSS injection ────────────────────────────────────────────────────────
def inject_theme():
    dark = st.session_state.dark_mode
    if dark:
        bg = "#0F172A"
        surface = "#1E293B"
        surface2 = "#334155"
        border = "#334155"
        text = "#F1F5F9"
        subtext = "#94A3B8"
        accent = "#3B82F6"
        accent_hover = "#2563EB"
        sidebar_bg = "#0F172A"
        sidebar_border = "#1E293B"
        card_bg = "#1E293B"
        input_bg = "#1E293B"
        badge_bg = "#1D4ED8"
        badge_text = "#DBEAFE"
        metric_border = "#3B82F6"
    else:
        bg = "#FFFFFF"
        surface = "#F8FAFC"
        surface2 = "#E2E8F0"
        border = "#E2E8F0"
        text = "#0F172A"
        subtext = "#64748B"
        accent = "#2563EB"
        accent_hover = "#1D4ED8"
        sidebar_bg = "#F8FAFC"
        sidebar_border = "#E2E8F0"
        card_bg = "#FFFFFF"
        input_bg = "#F8FAFC"
        badge_bg = "#DBEAFE"
        badge_text = "#1D4ED8"
        metric_border = "#2563EB"

    st.markdown(f"""
<style>
/* ─── Global ─────────────────────── */
html, body, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}
[data-testid="stAppViewContainer"] {{
    background-color: {bg} !important;
}}
[data-testid="block-container"] {{
    background-color: {bg} !important;
    padding-top: 1.5rem !important;
}}

/* ─── Sidebar ────────────────────── */
[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {sidebar_border} !important;
}}
[data-testid="stSidebar"] * {{
    color: {text} !important;
}}

/* ─── Inputs ─────────────────────── */
input, textarea, select {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border-color: {border} !important;
    border-radius: 8px !important;
}}
div[data-testid="stTextInput"] > div > div > input {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border-color: {border} !important;
}}

/* ─── Buttons ────────────────────── */
.stButton > button {{
    background-color: {"#1E293B" if dark else "#F1F5F9"} !important;
    color: {"#94A3B8" if dark else "#374151"} !important;
    border: 1px solid {"#334155" if dark else "#D1D5DB"} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.2rem !important;
    transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease !important;
}}
.stButton > button:hover {{
    background-color: {"#0F172A" if dark else "#1F2937"} !important;
    color: #FFFFFF !important;
    border-color: {"#0F172A" if dark else "#1F2937"} !important;
}}
.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div {{
    color: #FFFFFF !important;
}}

/* ─── Metrics ────────────────────── */
[data-testid="stMetric"] {{
    background-color: {card_bg} !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: 1px solid {border} !important;
    border-left: 4px solid {metric_border} !important;
}}
[data-testid="stMetricValue"] {{
    color: {accent} !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {subtext} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}

/* ─── Cards ──────────────────────── */
.portal-card {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
.portal-card:hover {{
    border-color: {accent};
    box-shadow: 0 4px 16px rgba(37,99,235,0.08);
}}

/* ─── Tabs ───────────────────────── */
[data-testid="stTab"] {{
    background: transparent !important;
    color: {subtext} !important;
}}
button[data-testid="stTab"][aria-selected="true"] {{
    color: {accent} !important;
    border-bottom-color: {accent} !important;
    font-weight: 700 !important;
}}

/* ─── Selectbox ──────────────────── */
[data-testid="stSelectbox"] > div > div {{
    background-color: {input_bg} !important;
    border-color: {border} !important;
    color: {text} !important;
}}

/* ─── Forms ──────────────────────── */
[data-testid="stForm"] {{
    background-color: {surface} !important;
    border-radius: 12px !important;
    border: 1px solid {border} !important;
    padding: 24px !important;
}}

/* ─── Dataframe ──────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 8px !important;
    border: 1px solid {border} !important;
}}

/* ─── Section header ─────────────── */
.section-header {{
    font-size: 1.4rem;
    font-weight: 800;
    color: {text};
    padding-bottom: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid {accent};
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* ─── Badges ─────────────────────── */
.badge {{
    background: {badge_bg};
    color: {badge_text};
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.03em;
}}

/* ─── Chat bubbles ───────────────── */
.chat-user {{
    background: {accent};
    color: #FFFFFF;
    padding: 10px 16px;
    border-radius: 16px 16px 4px 16px;
    display: inline-block;
    max-width: 80%;
    margin: 4px 0;
    font-size: 0.9rem;
}}
.chat-bot {{
    background: {surface};
    color: {text};
    border: 1px solid {border};
    padding: 10px 16px;
    border-radius: 16px 16px 16px 4px;
    display: inline-block;
    max-width: 85%;
    margin: 4px 0;
    font-size: 0.9rem;
    line-height: 1.5;
}}

/* ─── Nav buttons ────────────────── */
.nav-btn {{
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.88rem;
    color: {subtext};
    transition: all 0.15s ease;
}}
.nav-btn-active {{
    background: {"rgba(59,130,246,0.15)" if dark else "rgba(37,99,235,0.08)"};
    color: {accent};
    font-weight: 700;
    border-left: 3px solid {accent};
    padding-left: 10px;
}}

/* ─── Auth page ──────────────────── */
.auth-box {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 16px;
    padding: 40px 36px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}}

/* ─── General text ───────────────── */
p, h1, h2, h3, h4, h5, h6, label, span, div {{
    color: {text} !important;
}}
.sub-text {{ color: {subtext} !important; }}
a {{ color: {accent} !important; }}

/* ─── Slider ─────────────────────── */
[data-testid="stSlider"] {{ background: transparent !important; }}

/* ─── Radio ──────────────────────── */
[data-testid="stRadio"] label {{ color: {text} !important; }}
</style>
""", unsafe_allow_html=True)


# ── AI Client ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _logo_b64() -> str:
    logo_path = os.path.join(os.path.dirname(__file__), "anna_logo_clean.png")
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_ai_client():
    return OpenAI(api_key=AIPIPE_KEY, base_url=AIPIPE_BASE_URL)


# ── Auth Pages ─────────────────────────────────────────────────────────────────
def show_login_page():
    inject_theme()
    dark = st.session_state.dark_mode
    card_bg   = "#1E293B" if dark else "#FFFFFF"
    border_c  = "#334155" if dark else "#E2E8F0"
    sub_c     = "#94A3B8" if dark else "#64748B"
    head_c    = "#F1F5F9" if dark else "#0F172A"

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        # ── Header card ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='background:{card_bg}; border:1.5px solid {border_c};
                    border-radius:16px 16px 0 0; padding:22px 28px 16px;
                    border-bottom:none; display:flex; align-items:center; gap:16px;'>
            <img src="data:image/png;base64,{{logo_b64}}" width="56"
                 style="border-radius:8px; flex-shrink:0;" />
            <div>
                <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.08em;
                            text-transform:uppercase; color:{sub_c}; margin-bottom:2px;'>
                    Anna University · CEG
                </div>
                <div style='font-size:1.18rem; font-weight:800; color:{head_c}; line-height:1.25;'>
                    Department of Industrial Engineering
                </div>
                <div style='font-size:1rem; font-weight:700; color:#2563EB; line-height:1.3;'>
                    Placement Portal 2026
                </div>
            </div>
        </div>
        <div style='background:{card_bg}; border:1.5px solid {border_c};
                    border-radius:0 0 16px 16px; padding:6px 28px 26px; border-top:none;
                    box-shadow:0 4px 24px rgba(0,0,0,0.10);'>
        """.replace("{logo_b64}", _logo_b64()), unsafe_allow_html=True)

        tab_l, tab_r = st.tabs(["🔐  Login", "📝  Register"])

        with tab_l:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                reg = st.text_input("Registration Number / Username", placeholder="10-digit reg. no.", max_chars=20)
                pwd = st.text_input("Password", type="password", placeholder="Your password")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                if st.form_submit_button("Login →", use_container_width=True):
                    ok, msg, user = login_user(reg.strip(), pwd)
                    if ok:
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.success(f"Welcome back, {user['name'].split()[0]}!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_r:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            with st.form("reg_form"):
                name  = st.text_input("Full Name", placeholder="e.g. Arjun Sharma")
                reg_r = st.text_input("Registration Number", placeholder="10-digit number", max_chars=10)
                email_r  = st.text_input("Email (optional)", placeholder="you@student.annauniv.edu")
                domain_r = st.selectbox("Preferred Domain", [""] + [d["name"] for d in DOMAINS])
                pwd_r  = st.text_input("Password", type="password", placeholder="Min 6 characters")
                cpwd_r = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                if st.form_submit_button("Create Account →", use_container_width=True):
                    if pwd_r != cpwd_r:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = register_user(reg_r.strip(), name, pwd_r, email_r, domain_r)
                        if ok:
                            st.success(f"✅ {msg}  Switch to the Login tab to sign in.")
                        else:
                            st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def sidebar():
    user = st.session_state.user
    dark = st.session_state.dark_mode
    accent = "#3B82F6" if dark else "#2563EB"
    subtext = "#94A3B8" if dark else "#64748B"

    with st.sidebar:
        # ── Logo & branding ──
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        _, logo_center, _ = st.columns([1, 3, 1])
        with logo_center:
            logo_path = os.path.join(os.path.dirname(__file__), "anna_logo_clean.png")
            st.image(logo_path)
        st.markdown(f"""
        <div style='font-size:0.7rem; color:{"#64748B" if dark else "#94A3B8"};
             text-align:center; margin:6px 0 14px; padding:0 4px; line-height:1.4;'>
            Department of Industrial Engineering<br>Placement Portal 2026
        </div>
        <hr style='border:none; border-top:1px solid {"#1E293B" if dark else "#E2E8F0"}; margin:0 0 14px;'>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='border-radius:10px; padding:10px 14px; margin-bottom:18px;
                    border:1px solid {"#334155" if dark else "#E2E8F0"};
                    background:{"#1E293B" if dark else "#F1F5F9"};'>
            <div style='font-weight:700; font-size:0.9rem;'>👤 {user['name']}</div>
            <div class='sub-text' style='font-size:0.78rem;'>{user['reg_no']}</div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("🏠", "Dashboard", "dashboard"),
            ("🏢", "Companies", "companies"),
            ("🗂️", "Domains", "domains"),
            ("📊", "Insights", "insights"),
            ("🤖", "AI Assistant", "chatbot"),
            ("📢", "Updates", "updates"),
            ("⚙️", "Settings", "settings"),
        ]
        for icon, label, key in pages:
            active = st.session_state.page == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            ):
                st.session_state.page = key
                st.rerun()

        st.markdown("<br>" * 3, unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.chat_history = []
            st.session_state.page = "dashboard"
            st.rerun()


# ── Helpers ────────────────────────────────────────────────────────────────────
def section(title: str):
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)


def plot_layout(fig):
    dark = st.session_state.dark_mode
    bg = "#0F172A" if dark else "#FFFFFF"
    paper = "#1E293B" if dark else "#F8FAFC"
    font_color = "#F1F5F9" if dark else "#0F172A"
    grid = "#334155" if dark else "#E2E8F0"
    fig.update_layout(
        plot_bgcolor=bg, paper_bgcolor=paper,
        font_color=font_color,
        xaxis=dict(gridcolor=grid, zerolinecolor=grid),
        yaxis=dict(gridcolor=grid, zerolinecolor=grid),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


# ── Pages ──────────────────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown(
        "<h2 style='text-align:center; font-weight:800; color:#0B1F5E !important; font-size:40px '>Industrial Engineering, Anna University</h2>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <p style='
            text-align:center;
            font-size:20px;
            font-style:italic;
            color:#64748B;
        '>
        “Dream is not that which you see while sleeping,<br>
        it is something that does not let you sleep.”
        </p>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    # ================= KPI CARDS =================
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("🎓 Students Registered", STATS["registered"])
    c2.metric("✅ Students Placed", STATS["placed"])
    c3.metric("📈 Placement Rate", f"{STATS['placement_rate']}%")
    c4.metric("🏢 Total Companies", STATS["companies_count"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c5, c6, c7, c8 = st.columns(4)
    
    c5.metric("💰 Average Package", f"₹{STATS['avg_package_lpa']} LPA")
    c6.metric("🚀 Highest Package", f"₹{STATS['max_package_lpa']} LPA")
    c7.metric("📉 Minimum Package", f"₹{STATS['min_package_lpa']} LPA")
    c8.metric("🗂️ Domains Covered", STATS["domains_count"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)

    dark = st.session_state.dark_mode
    accent = "#3B82F6" if dark else "#2563EB"
    sub_c = "#94A3B8" if dark else "#64748B"

    with col_l:
        st.markdown("**📦 Placement Distribution**")
        df = pd.DataFrame(PLACEMENT_DIST)
        fig = px.bar(df, x="package_range", y="count", text="count",
                     color="count", color_continuous_scale=["#93C5FD", accent],
                     labels={"package_range": "Package Range", "count": "Students"})
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(plot_layout(fig), use_container_width=True)
        st.markdown(f"<p style='text-align:center; font-style:italic; font-size:0.78rem; color:{sub_c}; margin-top:-14px;'><b>Figure 1:</b> Number of students placed in each year's placement cycle.</p>", unsafe_allow_html=True)

    with col_r:
        st.markdown("**🗂️ Placements by Domain**")
        df2 = pd.DataFrame(DOMAIN_PLACED)
        fig2 = px.pie(df2, names="domain", values="placed", hole=0.45,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(plot_layout(fig2), use_container_width=True)
        st.markdown(f"<p style='text-align:center; font-style:italic; font-size:0.78rem; color:{sub_c}; margin-top:-14px;'><b>Figure 2:</b> Proportion of placed students across each industrial domain.</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🗂️ Quick Domain Browse** — *click a card to see companies*")

    dark = st.session_state.dark_mode
    card_bg  = "#1E293B" if dark else "#FFFFFF"
    border   = "#334155" if dark else "#E2E8F0"
    text_col = "#F1F5F9" if dark else "#0F172A"
    sub_col  = "#94A3B8" if dark else "#64748B"

    # Render 2 rows of 4 cards
    rows = [DOMAINS[:4], DOMAINS[4:]]
    for row in rows:
        cols = st.columns(4)
        for col, d in zip(cols, row):
            count = len([c for c in COMPANIES if c["domain_id"] == d["id"]])
            with col:
                st.markdown(f"""
                <div style='background:{card_bg}; border:1px solid {border}; border-radius:12px;
                     padding:14px 10px 10px; text-align:center; margin-bottom:8px;
                     box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
                    <div style='font-size:1.7rem;'>{d['icon']}</div>
                    <div style='font-weight:700; font-size:0.82rem; margin:6px 0 2px; color:{text_col};
                         line-height:1.3;'>{d['name']}</div>
                    <div style='font-size:0.75rem; color:{sub_col};'>{count} companies</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View {d['name']}", key=f"dc_{d['id']}", use_container_width=True):
                    st.session_state.selected_domain = d["name"]
                    st.session_state.page = "domains"
                    st.rerun()


def show_companies():
    section("🏢 All Companies")

    col_s, col_f = st.columns([2, 1])
    with col_s:
        search = st.text_input("🔍 Search", placeholder="Company name or role…")
    with col_f:
        domain_f = st.selectbox("Domain", ["All Domains"] + [d["name"] for d in DOMAINS])

    filtered = COMPANIES
    if search:
        s = search.lower()
        filtered = [c for c in filtered if s in c["name"].lower() or s in c["roles"].lower()]
    if domain_f != "All Domains":
        filtered = [c for c in filtered if c["domain"] == domain_f]

    st.markdown(f"<p class='sub-text' style='margin-bottom:12px;'>Showing <b>{len(filtered)}</b> companies</p>",
                unsafe_allow_html=True)

    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(filtered):
                c = filtered[i + j]
                with col:
                    st.markdown(f"""
                    <div class='portal-card'>
                        <div>
                            <div style='font-weight:700; font-size:0.97rem;'>{c['name']}</div>
                            <span class='badge' style='margin-top:4px; display:inline-block;'>{c['domain']}</span>
                        </div>
                        <div class='sub-text' style='margin-top:10px; font-size:0.83rem;'>
                            💼 {c['roles']}<br>📍 {c['location']}
                        </div>
                        <div style='margin-top:8px;'>
                            <a href='{c['website']}' target='_blank'
                               style='font-size:0.82rem; font-weight:600; text-decoration:none;'>
                                🌐 Visit Website →
                            </a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


def show_domains():
    section("🗂️ Browse by Domain")

    domain_names = [d["name"] for d in DOMAINS]
    preselect = st.session_state.selected_domain
    default_idx = domain_names.index(preselect) if preselect in domain_names else 0
    st.session_state.selected_domain = None  # clear after use
    selected = st.radio("Domain", domain_names,
                        index=default_idx,
                        horizontal=True, label_visibility="collapsed")
    domain_obj = next((d for d in DOMAINS if d["name"] == selected), None)
    if not domain_obj:
        return

    cos = [c for c in COMPANIES if c["domain"] == selected]

    st.markdown(f"""
    <div class='portal-card' style='margin:16px 0; border-left: 4px solid #2563EB;'>
        <div style='font-size:1.8rem;'>{domain_obj['icon']}</div>
        <div style='font-weight:800; font-size:1.1rem; margin:6px 0 2px 0;'>{domain_obj['name']}</div>
        <div class='sub-text' style='font-size:0.87rem;'>{domain_obj['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, _ = st.columns([1, 2])
    c1.metric("Companies", len(cos))

    st.markdown("<br>", unsafe_allow_html=True)
    for c in cos:
        st.markdown(f"""
        <div class='portal-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='font-weight:700; font-size:0.97rem;'>{c['name']}</div>
                    <div class='sub-text' style='font-size:0.83rem; margin-top:4px;'>
                        💼 {c['roles']} &nbsp;|&nbsp; 📍 {c['location']}
                    </div>
                </div>
                <a href='{c['website']}' target='_blank'
                   style='font-size:0.82rem; font-weight:600; text-decoration:none; white-space:nowrap;'>
                    🌐 Website
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_insights():
    section("📊 Placement Insights")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered", STATS["registered"])
    c2.metric("Placed", STATS["placed"])
    c3.metric("Rate", f"{STATS['placement_rate']}%")
    c4.metric("Companies", STATS["companies_count"])

    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📦 Package Distribution", "🗂️ Domain Analysis"])

    accent = "#3B82F6" if st.session_state.dark_mode else "#2563EB"

    dark = st.session_state.dark_mode
    sub_c = "#94A3B8" if dark else "#64748B"

    def fig_caption(n, text):
        st.markdown(f"<p style='text-align:center; font-style:italic; font-size:0.78rem; color:{sub_c}; margin-top:-14px; margin-bottom:10px;'><b>Figure {n}:</b> {text}</p>", unsafe_allow_html=True)

    with t1:
        col_a, col_b = st.columns(2)
        with col_a:
            df = pd.DataFrame(PLACEMENT_DIST)
            fig = px.bar(df, x="package_range", y="count", text="count",
                         color="count", color_continuous_scale=["#93C5FD", accent],
                         title="Students by Placement Batch",
                         labels={"package_range": "Batch / Range", "count": "Students"})
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plot_layout(fig), use_container_width=True)
            fig_caption(1, "Number of students placed across different cohorts in the 2025–26 drive.")
        with col_b:
            df_s = pd.DataFrame({"Status": ["Placed", "Awaiting"],
                                  "Count": [STATS["placed"], STATS["registered"] - STATS["placed"]]})
            fig_pie = px.pie(df_s, names="Status", values="Count", hole=0.55,
                             color_discrete_sequence=[accent, "#E2E8F0"],
                             title="Overall Placement Rate")
            st.plotly_chart(plot_layout(fig_pie), use_container_width=True)
            fig_caption(2, "Share of registered students (43) who have secured placements so far.")

    with t2:
        col_a, col_b = st.columns(2)
        with col_a:
            df_dom = pd.DataFrame(DOMAIN_PLACED).sort_values("placed")
            fig_h = px.bar(df_dom, x="placed", y="domain", orientation="h", text="placed",
                           color="placed", color_continuous_scale=["#93C5FD", accent],
                           title="Placed Students by Domain")
            fig_h.update_traces(textposition="outside", marker_line_width=0)
            fig_h.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plot_layout(fig_h), use_container_width=True)
            fig_caption(3, "Horizontal bar chart showing placements per domain, sorted ascending.")
        with col_b:
            radar_df = pd.DataFrame([
                {"domain": d["name"].split("/")[0].strip(),
                 "companies": len([c for c in COMPANIES if c["domain_id"] == d["id"]])}
                for d in DOMAINS
            ])
            fig_r = go.Figure(go.Scatterpolar(
                r=radar_df["companies"].tolist(),
                theta=radar_df["domain"].tolist(),
                fill="toself",
                fillcolor="rgba(37,99,235,0.15)",
                line=dict(color=accent),
            ))
            fig_r.update_layout(
                polar=dict(bgcolor="#1E293B" if dark else "#F8FAFC",
                           radialaxis=dict(visible=True, color="#94A3B8" if dark else "#64748B"),
                           angularaxis=dict(color="#F1F5F9" if dark else "#0F172A")),
                paper_bgcolor="#1E293B" if dark else "#F8FAFC",
                font_color="#F1F5F9" if dark else "#0F172A",
                title="Companies per Domain",
                showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)
            fig_caption(4, "Radar chart showing the count of participating companies across each domain.")



def show_chatbot():
    section("🤖 AI Placement Assistant")

    st.markdown("""
    <div class='portal-card' style='margin-bottom:20px; border-left: 4px solid #2563EB;'>
        <b>PlaceBot</b> — Powered by GPT-4.1-mini via AIPipe &nbsp;
        <span class='badge'>Online</span><br>
        <span class='sub-text' style='font-size:0.83rem;'>
            Ask about placements, companies, packages, career advice, or anything else!
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_tips = st.columns([2.3, 1])

    with col_tips:
        st.markdown("**💡 Try asking…**")
        suggestions = [
            "How many students got placed?",
            "Which domain has the most companies?",
            "Tips for interview preparation",
            "What is the placement rate?",
            "Companies in IT/Software domain",
            "Career advice for freshers",
            "How to prepare for campus placements?",
            "Which domains are best for industrial engineers?",
            "What skills do companies look for?",
        ]
        for s in suggestions:
            if st.button(s, key=f"sug_{s[:20]}", use_container_width=True):
                _send_message(s)
                st.rerun()

        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    with col_chat:
        chat_box = st.container(height=460)
        with chat_box:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style='text-align:center; padding:80px 20px;'>
                    <div style='font-size:3rem;'>🤖</div>
                    <div style='font-weight:700; font-size:1rem; margin-top:12px;'>Hi! I'm PlaceBot</div>
                    <div class='sub-text' style='font-size:0.85rem; margin-top:4px;'>
                        Ask me about placements, companies, packages, or any career question!
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style='display:flex; justify-content:flex-end; margin:6px 0;'>
                            <div class='chat-user'>{msg['content']}</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='display:flex; justify-content:flex-start; margin:6px 0;'>
                            <div class='chat-bot'>🤖&nbsp; {msg['content']}</div>
                        </div>""", unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            col_i, col_b = st.columns([5, 1])
            with col_i:
                user_input = st.text_input(
                    "msg", label_visibility="collapsed",
                    placeholder="Type your question here…"
                )
            with col_b:
                send = st.form_submit_button("Send →", use_container_width=True)
            if send and user_input.strip():
                _send_message(user_input.strip())
                st.rerun()


def _send_message(text: str):
    st.session_state.chat_history.append({"role": "user", "content": text})
    client = get_ai_client()
    messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]
    messages += [{"role": m["role"], "content": m["content"]}
                 for m in st.session_state.chat_history]
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=700,
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"Sorry, something went wrong: {str(e)}"
    st.session_state.chat_history.append({"role": "assistant", "content": answer})


def show_updates():
    section("📢 Updates Board")

    dark = st.session_state.dark_mode
    user = st.session_state.user
    is_admin = user.get("is_admin", False)

    # colour tokens
    bubble_bg   = "#1A4731" if dark else "#DCF8C6"
    bubble_text = "#E2F5E8" if dark else "#0F172A"
    card_bg     = "#1E293B" if dark else "#FFFFFF"
    border_c    = "#334155" if dark else "#E2E8F0"
    sub_c       = "#94A3B8" if dark else "#64748B"
    link_c      = "#60A5FA" if dark else "#2563EB"
    del_c       = "#EF4444"

    # collect updates from DB
    all_updates = get_updates()
    
    latest_update_id = all_updates[0]["id"] if all_updates else 0
    if "last_seen_update" not in st.session_state:
        st.session_state.last_seen_update = latest_update_id
    elif latest_update_id > st.session_state.last_seen_update:
        st.toast("🚨 New placement update available!")
        st.session_state.last_seen_update = latest_update_id

    
    # ── Admin post area ──────────────────────────────────────────────────────
    if is_admin:
        st.markdown(f"""
        <div style='background:{card_bg}; border:1.5px solid #2563EB; border-radius:12px;
                    padding:18px 22px; margin-bottom:24px;'>
            <div style='font-weight:700; font-size:1rem; margin-bottom:6px;'>📝 Post a New Update</div>
            <div style='font-size:0.83rem; color:{sub_c};'>Visible to all students. You can include URLs — they'll be detected automatically.</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("post_update_form", clear_on_submit=True):
            msg = st.text_area("Message", placeholder="e.g. Infosys drive on June 5 at 10 AM. Register at https://campus.infosys.com", height=100, label_visibility="collapsed")
            col_btn, _ = st.columns([1, 4])
            with col_btn:
                submitted = st.form_submit_button("📤 Post", use_container_width=True)
            if submitted:
                if msg.strip():
                    if post_update(msg.strip()):
                        st.toast("🚨 New placement update posted!")
                        st.success("Update posted!")
                        st.rerun()
                    else:
                        st.error("Failed to post. Please try again.")
                else:
                    st.warning("Please enter a message before posting.")

    # ── Search / filter bar ──────────────────────────────────────────────────
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_q = st.text_input("🔍 Search updates…", placeholder="company name, keyword, URL…", label_visibility="collapsed")
    with col_sort:
        sort_order = st.selectbox("Order", ["Newest first", "Oldest first"], label_visibility="collapsed")

    # filter + sort
    visible = all_updates
    if search_q.strip():
        q_low = search_q.strip().lower()
        visible = [u for u in visible if q_low in u["message"].lower()]
    if sort_order == "Oldest first":
        visible = list(reversed(visible))

    # ── Update count badge ───────────────────────────────────────────────────
    st.markdown(f"<p style='font-size:0.8rem; color:{sub_c}; margin:8px 0 14px;'>{len(visible)} update(s) shown</p>", unsafe_allow_html=True)

    # ── Chat-bubble timeline ─────────────────────────────────────────────────
    if not visible:
        st.markdown(f"""
        <div style='text-align:center; padding:60px 20px; color:{sub_c};'>
            <div style='font-size:2.8rem;'>📭</div>
            <div style='margin-top:10px; font-size:0.95rem;'>No updates yet. Check back soon!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for upd in visible:
            msg_text  = upd["message"]
            ts        = upd.get("created_at", "")[:16].replace("T", "  ")
            uid       = upd["id"]
            links     = extract_links(msg_text)

            # build display HTML — hyperlink any URLs in the message
            import re
            display_msg = re.sub(
                r'(https?://[^\s]+)',
                lambda m: f'<a href="{m.group(1)}" target="_blank" style="color:{link_c}; word-break:break-all;">{m.group(1)}</a>',
                msg_text
            )

            # Pill tags for extracted links
            link_pills = ""
            if links:
                pills_html = " ".join(
                    f'<a href="{l}" target="_blank" style="display:inline-block; background:{"#1D3461" if dark else "#DBEAFE"}; color:{link_c}; border-radius:20px; padding:2px 10px; font-size:0.73rem; margin:2px 2px 0 0; text-decoration:none;">🔗 Link</a>'
                    for l in links
                )
                link_pills = f"<div style='margin-top:8px;'>{pills_html}</div>"

            st.markdown(f"""
            <div style='display:flex; justify-content:flex-start; margin:10px 0;'>
                <div style='max-width:80%; background:{bubble_bg}; color:{bubble_text};
                            border-radius:0 16px 16px 16px; padding:14px 18px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.12);'>
                    <div style='font-size:0.72rem; font-weight:700; color:{"#4ADE80" if dark else "#15803D"}; margin-bottom:6px; letter-spacing:0.04em;'>
                        📣 ADMIN · {ts}
                    </div>
                    <div style='font-size:0.92rem; line-height:1.55;'>{display_msg}</div>
                    {link_pills}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Admin delete button
            if is_admin:
                del_col, _ = st.columns([1, 9])
                with del_col:
                    if st.button("🗑 Delete", key=f"del_{uid}", help="Delete this update"):
                        delete_update(uid)
                        st.rerun()

    # ── Side info panel ──────────────────────────────────────────────────────
    # (shown as an expander to keep the page clean)


def show_settings():
    section("⚙️ Settings")

    user = st.session_state.user

    st.markdown("### 👤 My Profile")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class='portal-card'>
            <div style='font-size:0.78rem; font-weight:600; text-transform:uppercase;
                        letter-spacing:0.06em;' class='sub-text'>Name</div>
            <div style='font-size:1rem; font-weight:700; margin-top:2px;'>{user['name']}</div>
        </div>
        <div class='portal-card'>
            <div style='font-size:0.78rem; font-weight:600; text-transform:uppercase;
                        letter-spacing:0.06em;' class='sub-text'>Registration No.</div>
            <div style='font-size:1rem; font-weight:700; margin-top:2px;'>{user['reg_no']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        email_display = user.get("email") or "Not provided"
        domain_display = user.get("domain") or "Not selected"
        st.markdown(f"""
        <div class='portal-card'>
            <div style='font-size:0.78rem; font-weight:600; text-transform:uppercase;
                        letter-spacing:0.06em;' class='sub-text'>Email</div>
            <div style='font-size:1rem; font-weight:700; margin-top:2px;'>{email_display}</div>
        </div>
        <div class='portal-card'>
            <div style='font-size:0.78rem; font-weight:600; text-transform:uppercase;
                        letter-spacing:0.06em;' class='sub-text'>Preferred Domain</div>
            <div style='font-size:1rem; font-weight:700; margin-top:2px;'>{domain_display}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎨 Appearance")

    col_toggle, _ = st.columns([1, 2])
    with col_toggle:
        st.markdown("""
        <div class='portal-card' style='padding:20px 24px;'>
            <div style='font-weight:700; margin-bottom:10px;'>Theme Mode</div>
        """, unsafe_allow_html=True)
        mode = st.radio(
            "Theme",
            ["☀️  Light Mode", "🌙  Dark Mode"],
            index=1 if st.session_state.dark_mode else 0,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if mode == "🌙  Dark Mode" and not st.session_state.dark_mode:
            st.session_state.dark_mode = True
            st.rerun()
        elif mode == "☀️  Light Mode" and st.session_state.dark_mode:
            st.session_state.dark_mode = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Portal Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Companies", STATS["companies_count"])
    c2.metric("Total Domains", STATS["domains_count"])
    c3.metric("Batch Year", STATS["batch"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='portal-card' style='border-left: 4px solid #2563EB;'>
        <div style='font-weight:700; margin-bottom:4px;'>About this Portal</div>
        <div class='sub-text' style='font-size:0.85rem;'>
            {STATS['dept']} · {STATS['college']}<br>
            Placement Drive {STATS['batch']} · Built with Streamlit + GPT-4.1-mini
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if st.session_state.user is None:
        show_login_page()
        return

    inject_theme()
    sidebar()

    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "companies":
        show_companies()
    elif page == "domains":
        show_domains()
    elif page == "insights":
        show_insights()
    elif page == "chatbot":
        show_chatbot()
    elif page == "updates":
        show_updates()
    elif page == "settings":
        show_settings()


if __name__ == "__main__":
    main()
