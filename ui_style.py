"""Visual identity of ScamRadar: CSS and small HTML helpers (no user text is ever rendered as raw HTML)."""
import html
import streamlit as st

NAVY, PANEL, BORDER = "#0b1120", "#111a2e", "#1f2b47"
CYAN, BLUE, PURPLE = "#22d3ee", "#3b82f6", "#8b5cf6"
RED, GREEN, AMBER = "#ef4444", "#22c55e", "#f59e0b"
MUTED = "#94a3b8"

CSS = f"""
<style>
.stApp {{
  background:
    radial-gradient(1100px 520px at 8% -8%, rgba(59,130,246,.16), transparent 60%),
    radial-gradient(900px 480px at 100% 0%, rgba(139,92,246,.13), transparent 60%),
    {NAVY};
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 3.6rem; padding-bottom: 3rem; max-width: 1180px; }}
h1, h2, h3, h4 {{ letter-spacing: -0.01em; }}
p, li, label, .stMarkdown {{ color: #dbe3f0; }}
a {{ color: {CYAN}; }}

.sr-brand {{ display:flex; align-items:center; gap:.7rem; margin-bottom:.4rem; }}
.sr-brand .name {{ font-size:1.35rem; font-weight:700; color:#f1f5f9; }}
.sr-badge {{ display:inline-block; padding:.18rem .65rem; border:1px solid rgba(34,211,238,.45); color:{CYAN};
             background:rgba(34,211,238,.08); border-radius:999px; font-size:.75rem; letter-spacing:.06em; text-transform:uppercase; }}
.sr-badge.warn {{ border-color:rgba(245,158,11,.5); color:{AMBER}; background:rgba(245,158,11,.08); }}

.sr-hero {{ padding: 1.2rem 0 .4rem 0; }}
.sr-hero h1 {{ font-size: 3rem; line-height:1.08; margin:.5rem 0 .6rem 0; color:#f8fafc; }}
.sr-hero h1 span {{ background: linear-gradient(90deg,{CYAN},{BLUE} 55%,{PURPLE}); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.sr-hero p {{ color:{MUTED}; font-size:1.06rem; max-width: 760px; }}
.sr-tagline {{ color:{CYAN}; font-weight:600; letter-spacing:.02em; }}

.sr-card {{ background:linear-gradient(180deg,#131d35,#0f1729); border:1px solid {BORDER}; border-radius:16px; padding:1.15rem 1.3rem; height:100%; }}
.sr-card h4 {{ margin:.1rem 0 .35rem 0; color:#f1f5f9; font-size:1.02rem; }}
.sr-card p {{ color:{MUTED}; margin:0; font-size:.93rem; }}
.sr-icon {{ width:38px; height:38px; border-radius:11px; display:flex; align-items:center; justify-content:center;
            background:linear-gradient(135deg,rgba(34,211,238,.18),rgba(139,92,246,.18)); border:1px solid rgba(34,211,238,.25); margin-bottom:.7rem; }}
.sr-icon svg {{ width:20px; height:20px; stroke:{CYAN}; fill:none; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}

.sr-metric {{ background:linear-gradient(180deg,#131d35,#0f1729); border:1px solid {BORDER}; border-radius:16px; padding:1rem 1.2rem; }}
.sr-metric .label {{ color:{MUTED}; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }}
.sr-metric .value {{ font-size:2rem; font-weight:700; color:#f8fafc; line-height:1.15; }}
.sr-metric .sub {{ color:{MUTED}; font-size:.78rem; }}
.sr-metric.red .value {{ color:{RED}; }} .sr-metric.green .value {{ color:{GREEN}; }} .sr-metric.cyan .value {{ color:{CYAN}; }}

.sr-panel-title {{ font-size:1.05rem; font-weight:600; color:#f1f5f9; margin-bottom:.2rem; }}
.sr-panel-sub {{ color:{MUTED}; font-size:.9rem; margin-bottom:.6rem; }}

.stTextArea textarea {{ background:#0d1526 !important; border:1px solid #243255 !important; border-radius:12px !important; color:#e5e7eb !important; font-size:1rem; }}
.stTextArea textarea:focus {{ border-color:{CYAN} !important; box-shadow:0 0 0 1px {CYAN} !important; }}
.stButton > button {{ border-radius:11px; font-weight:600; padding:.55rem 1.3rem; border:1px solid #2a3a62; }}
.stButton > button[kind="primary"] {{ background:linear-gradient(90deg,{BLUE},{PURPLE}); border:none; color:white; }}
.stButton > button[kind="primary"]:hover {{ filter:brightness(1.1); }}

.sr-result {{ border-radius:18px; padding:1.3rem 1.5rem; margin-top:1rem; border:1px solid; }}
.sr-result.bad {{ background:linear-gradient(180deg,#2a1319,#1a0f15); border-color:rgba(239,68,68,.55); }}
.sr-result.good {{ background:linear-gradient(180deg,#0f2a1e,#0e1a17); border-color:rgba(34,197,94,.5); }}
.sr-result .title {{ font-size:1.5rem; font-weight:700; margin:0; }}
.sr-result.bad .title {{ color:#fca5a5; }} .sr-result.good .title {{ color:#86efac; }}
.sr-result .lead {{ color:#cbd5e1; margin:.25rem 0 .9rem 0; }}
.sr-bar {{ height:10px; background:#1e293b; border-radius:999px; overflow:hidden; margin:.3rem 0 .2rem 0; }}
.sr-bar > div {{ height:100%; border-radius:999px; }}
.sr-chip {{ display:inline-block; padding:.2rem .65rem; margin:.15rem .25rem .15rem 0; border-radius:999px; font-size:.82rem;
            background:rgba(148,163,184,.12); border:1px solid rgba(148,163,184,.25); color:#e2e8f0; }}
.sr-chip.red {{ background:rgba(239,68,68,.12); border-color:rgba(239,68,68,.35); color:#fecaca; }}
.sr-section {{ color:{MUTED}; font-size:.78rem; text-transform:uppercase; letter-spacing:.09em; margin:.9rem 0 .25rem 0; }}
.sr-disclaimer {{ border:1px solid rgba(245,158,11,.4); background:rgba(245,158,11,.07); border-radius:12px; padding:.8rem 1rem; color:#fde68a; font-size:.9rem; margin-top:1rem; }}
.sr-note {{ border:1px solid rgba(139,92,246,.4); background:rgba(139,92,246,.08); border-radius:12px; padding:.75rem 1rem; color:#ddd6fe; font-size:.9rem; margin:.6rem 0; }}
.sr-step {{ display:flex; gap:1rem; align-items:flex-start; }}
.sr-step .num {{ min-width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; color:#0b1120;
                 background:linear-gradient(135deg,{CYAN},{BLUE}); }}
[data-testid="stSidebar"] {{ background:#0a0f1d; border-right:1px solid {BORDER}; }}
hr {{ border-color:{BORDER}; }}
.stTabs [data-baseweb="tab"] {{ color:{MUTED}; }}
.stTabs [aria-selected="true"] {{ color:{CYAN}; }}
</style>
"""

ICONS = {
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 4.5-3.2 8.2-8 9-4.8-.8-8-4.5-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/></svg>',
    "radar": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12L18 6"/></svg>',
    "text": '<svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg>',
    "chart": '<svg viewBox="0 0 24 24"><path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-7"/></svg>',
    "lock": '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>',
    "layers": '<svg viewBox="0 0 24 24"><path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
}


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def brand(small=False) -> str:
    size = 30 if small else 38
    return (f'<div class="sr-brand"><svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="48" y2="48"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient></defs>'
            f'<path d="M24 4l16 6v12c0 9.4-6.6 17.2-16 20-9.4-2.8-16-10.6-16-20V10l16-6z" stroke="url(#g)" stroke-width="2.6"/>'
            f'<circle cx="24" cy="23" r="9" stroke="url(#g)" stroke-width="2"/><circle cx="24" cy="23" r="3" fill="url(#g)"/>'
            f'<path d="M24 23l7-7" stroke="url(#g)" stroke-width="2" stroke-linecap="round"/></svg>'
            f'<span class="name">ScamRadar</span></div>')


def feature_card(icon: str, title: str, text: str) -> str:
    return f'<div class="sr-card"><div class="sr-icon">{ICONS[icon]}</div><h4>{esc(title)}</h4><p>{esc(text)}</p></div>'


def metric_card(label: str, value, sub: str = "", tone: str = "") -> str:
    return (f'<div class="sr-metric {tone}"><div class="label">{esc(label)}</div><div class="value">{esc(value)}</div>'
            f'<div class="sub">{esc(sub)}</div></div>')


def chips(items, tone="") -> str:
    return "".join(f'<span class="sr-chip {tone}">{esc(i)}</span>' for i in items)
