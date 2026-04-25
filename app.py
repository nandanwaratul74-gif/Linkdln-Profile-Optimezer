"""
LinkedIn AI Optimizer - Streamlit App
Uses Gemini + Tavily agents to analyze and rewrite LinkedIn profiles.
"""

import os
import streamlit as st
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

from agents.researcher import research_job_role
from agents.analyzer import analyze_profile
from agents.rewriter import rewrite_profile
from agents.judge import judge_profile

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="LinkedIn AI Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

:root {
    --grad: linear-gradient(135deg,#667eea,#764ba2,#f093fb);
    --glass: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.13);
    --text: #fff;
    --muted: rgba(255,255,255,0.6);
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg,#0a0a1a,#1a1a2e,#16213e) !important;
    background-attachment: fixed !important;
}

[data-testid="stSidebar"] {
    background: rgba(10,10,26,0.85) !important;
    border-right: 1px solid var(--border) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

.glass {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
}

.hero h1 {
    font-size: clamp(2.5rem,5vw,4.5rem);
    font-weight: 900;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 1rem;
}

.hero p {
    color: var(--muted);
    font-size: 1.2rem;
    margin: 0;
}

.score-ring {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
}

.score-ring .num {
    font-size: 3rem;
    font-weight: 900;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.score-ring .label {
    color: var(--muted);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px;
    background: rgba(102,126,234,0.2);
    color: #a78bfa;
    border: 1px solid rgba(102,126,234,0.35);
}

.tag.green {
    background: rgba(67,233,123,0.15);
    color: #4ade80;
    border-color: rgba(67,233,123,0.3);
}

.tag.red {
    background: rgba(245,87,108,0.15);
    color: #f87171;
    border-color: rgba(245,87,108,0.3);
}

.section-head {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.stButton > button {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 16px !important;
    color: #fff !important;
    font-weight: 700 !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(102,126,234,0.4) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: #fff !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--glass);
    border-radius: 16px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    color: var(--muted);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: var(--grad) !important;
    color: #fff !important;
}

.verdict-badge {
    font-size: 1.1rem;
    font-weight: 800;
    padding: 8px 24px;
    border-radius: 50px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.v-excellent { background: rgba(67,233,123,0.2); color: #4ade80; border: 1px solid rgba(67,233,123,0.4); }
.v-good      { background: rgba(99,102,241,0.2); color: #818cf8; border: 1px solid rgba(99,102,241,0.4); }
.v-needs     { background: rgba(251,191,36,0.2); color: #fbbf24; border: 1px solid rgba(251,191,36,0.4); }
.v-poor      { background: rgba(245,87,108,0.2); color: #f87171; border: 1px solid rgba(245,87,108,0.4); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

def init_state():
    defaults = {
        "research": None,
        "analysis": None,
        "rewrite": None,
        "judgment": None,
        "ran_once": False,
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    gemini_key = st.text_input(
        "Google API Key",
        value=GOOGLE_API_KEY or "",
        type="password",
        help="Get your key at https://aistudio.google.com"
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        value=TAVILY_API_KEY or "",
        type="password",
        help="Get your key at https://tavily.com"
    )

    st.divider()
    st.markdown("### 📋 About")
    st.markdown("""
    <div style='color:rgba(255,255,255,0.6); font-size:0.9rem; line-height:1.7;'>
    This tool uses an AI agent pipeline:<br><br>
    🔍 <b>Researcher</b> — Finds top profile trends via Tavily<br>
    🧠 <b>Analyzer</b> — Scores your current profile<br>
    ✍️ <b>Rewriter</b> — Rewrites optimized sections<br>
    ⚖️ <b>Judge</b> — Independently scores the result
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.ran_once:
        st.success("✅ Last run: Analysis complete")
    else:
        st.info("Fill in the Profile tab and click Optimize.")

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🚀 LinkedIn AI Optimizer</h1>
    <p>Enterprise AI agent pipeline to supercharge your LinkedIn profile</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["📝 Profile Input", "🤖 AI Analysis", "✨ Rewritten Profile", "⚖️ Judge Scores"])

# ── TAB 1: INPUT ─────────────────────────────
with tab1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🎯 Target Role</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        target_job = st.text_input("Job Title *", placeholder="e.g. Senior Embedded Systems Engineer", key="target_job")
    with col2:
        industry = st.text_input("Industry", placeholder="e.g. Automotive, IoT, Defense")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">👤 Current LinkedIn Profile</div>', unsafe_allow_html=True)

    headline = st.text_input("Headline", placeholder="e.g. Embedded Systems Engineer | RTOS | ARM | C/C++", key="headline")
    about = st.text_area("About / Summary", height=180, placeholder="Paste your current About section here...", key="about")
    skills = st.text_input("Skills (comma-separated)", placeholder="C, C++, RTOS, ARM Cortex, CAN, SPI, I2C, Python...", key="skills")
    experience = st.text_area("Experience (optional)", height=100, placeholder="Paste key experience points...", key="experience")

    st.markdown('</div>', unsafe_allow_html=True)

    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        run_btn = st.button("🚀 Optimize My Profile", use_container_width=True, type="primary")

    if run_btn:
        if not target_job:
            st.error("⚠️ Please enter a Target Job Title.")
        elif not gemini_key or not tavily_key:
            st.error("⚠️ Please enter your API keys in the sidebar.")
        elif not (headline or about or skills):
            st.error("⚠️ Please fill in at least one profile section (Headline, About, or Skills).")
        else:
            with st.status("🤖 Running AI Agent Pipeline...", expanded=True) as status:
                # Step 1: Research
                st.write("🔍 **Researcher Agent** — Searching LinkedIn trends...")
                try:
                    research = research_job_role(target_job, tavily_key)
                    st.session_state.research = research
                    st.write("✅ Research complete")
                except Exception as e:
                    research = f"Research failed: {e}"
                    st.session_state.research = research
                    st.write(f"⚠️ Research warning: {e}")

                # Step 2: Analyze
                st.write("🧠 **Analyzer Agent** — Scoring your profile...")
                try:
                    analysis = analyze_profile(target_job, headline, about, skills, experience, research, gemini_key)
                    st.session_state.analysis = analysis
                    st.write("✅ Analysis complete")
                except Exception as e:
                    st.error(f"Analyzer failed: {e}")
                    st.stop()

                # Step 3: Rewrite
                st.write("✍️ **Rewriter Agent** — Crafting optimized profile...")
                try:
                    rewrite = rewrite_profile(target_job, headline, about, skills, experience, analysis, research, gemini_key)
                    st.session_state.rewrite = rewrite
                    st.write("✅ Rewrite complete")
                except Exception as e:
                    st.error(f"Rewriter failed: {e}")
                    st.stop()

                # Step 4: Judge
                st.write("⚖️ **Judge Agent** — Scoring the result...")
                try:
                    judgment = judge_profile(target_job, rewrite, gemini_key)
                    st.session_state.judgment = judgment
                    st.write("✅ Judgment complete")
                except Exception as e:
                    st.session_state.judgment = None
                    st.write(f"⚠️ Judge warning: {e}")

                # Save history
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "role": target_job,
                    "score": analysis.get("overall_score", "N/A"),
                    "judge": st.session_state.judgment.get("overall", "N/A") if st.session_state.judgment else "N/A",
                })
                st.session_state.ran_once = True

                status.update(label="✅ All agents complete! Check the other tabs.", state="complete")

            st.balloons()

# ── TAB 2: ANALYSIS ──────────────────────────
with tab2:
    analysis = st.session_state.analysis
    if not analysis:
        st.markdown('<div class="glass" style="text-align:center; color:rgba(255,255,255,0.5);">Run the optimizer from the Profile Input tab first.</div>', unsafe_allow_html=True)
    else:
        # Score cards
        cols = st.columns(4)
        metrics = [
            ("Overall", analysis.get("overall_score", 0)),
            ("Headline", analysis.get("headline_score", 0)),
            ("About", analysis.get("about_score", 0)),
            ("Keywords", analysis.get("keyword_score", 0)),
        ]
        for col, (label, score) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div class="score-ring">
                    <div class="num">{score}<span style="font-size:1.2rem">/10</span></div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")
        cols2 = st.columns(3)
        with cols2[0]:
            st.markdown(f"""
            <div class="score-ring">
                <div class="num">{analysis.get("skills_score",0)}<span style="font-size:1.2rem">/10</span></div>
                <div class="label">Skills</div>
            </div>
            """, unsafe_allow_html=True)
        with cols2[1]:
            st.markdown(f"""
            <div class="score-ring">
                <div class="num">{analysis.get("ats_compatibility",0)}<span style="font-size:1.2rem">/10</span></div>
                <div class="label">ATS Score</div>
            </div>
            """, unsafe_allow_html=True)
        with cols2[2]:
            st.markdown(f"""
            <div class="score-ring">
                <div class="num">{analysis.get("about_score",0)}<span style="font-size:1.2rem">/10</span></div>
                <div class="label">About</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">✅ Strengths</div>', unsafe_allow_html=True)
            for s in analysis.get("strengths", []):
                st.markdown(f'<span class="tag green">✓ {s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">🔴 Missing Keywords</div>', unsafe_allow_html=True)
            for k in analysis.get("missing_keywords", []):
                st.markdown(f'<span class="tag red">+ {k}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">⚠️ Weaknesses</div>', unsafe_allow_html=True)
            for w in analysis.get("weaknesses", []):
                st.markdown(f"• {w}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">🎯 Priority Improvements</div>', unsafe_allow_html=True)
            for i, imp in enumerate(analysis.get("priority_improvements", []), 1):
                st.markdown(f"**{i}.** {imp}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">🛠️ Missing Skills & Certifications</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Skills to Add:**")
            for s in analysis.get("missing_skills", []):
                st.markdown(f'<span class="tag">+ {s}</span>', unsafe_allow_html=True)
        with cc2:
            st.markdown("**Certifications:**")
            for c in analysis.get("missing_certifications", []):
                st.markdown(f'<span class="tag">🏆 {c}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 3: REWRITE ───────────────────────────
with tab3:
    rewrite = st.session_state.rewrite
    if not rewrite:
        st.markdown('<div class="glass" style="text-align:center; color:rgba(255,255,255,0.5);">Run the optimizer from the Profile Input tab first.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">🏷️ Optimized Headline</div>', unsafe_allow_html=True)
        st.code(rewrite.get("headline", ""), language=None)

        options = rewrite.get("headline_options", [])
        if options:
            st.markdown("**Alternative Headlines:**")
            for i, opt in enumerate(options, 1):
                st.markdown(f"`{i}.` {opt}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">📝 Optimized About Section</div>', unsafe_allow_html=True)
        about_text = rewrite.get("about", "").replace("\\n", "\n")
        st.text_area("Copy this to LinkedIn:", value=about_text, height=280, key="rewrite_about")
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">💡 Top 15 Skills</div>', unsafe_allow_html=True)
            for skill in rewrite.get("skills", []):
                st.markdown(f'<span class="tag green">✓ {skill}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">🔑 ATS Keywords</div>', unsafe_allow_html=True)
            for kw in rewrite.get("featured_keywords", []):
                st.markdown(f'<span class="tag">🔑 {kw}</span>', unsafe_allow_html=True)

            tip = rewrite.get("recruiter_tip", "")
            if tip:
                st.markdown("---")
                st.info(f"💡 **Recruiter Tip:** {tip}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Export
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">📤 Export</div>', unsafe_allow_html=True)
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "target_role": st.session_state.get("target_job", ""),
            "optimized_profile": rewrite,
            "analysis": st.session_state.analysis,
            "judgment": st.session_state.judgment,
        }
        st.download_button(
            "⬇️ Download Full Report (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name=f"linkedin_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 4: JUDGE ─────────────────────────────
with tab4:
    judgment = st.session_state.judgment
    if not judgment:
        st.markdown('<div class="glass" style="text-align:center; color:rgba(255,255,255,0.5);">Run the optimizer from the Profile Input tab first.</div>', unsafe_allow_html=True)
    else:
        verdict = judgment.get("verdict", "GOOD").upper()
        cls_map = {"EXCELLENT": "v-excellent", "GOOD": "v-good", "NEEDS WORK": "v-needs", "POOR": "v-poor"}
        vcls = cls_map.get(verdict, "v-good")

        st.markdown(f"""
        <div style="text-align:center; margin-bottom:2rem;">
            <div class="score-ring" style="display:inline-flex; padding:2rem 4rem;">
                <div class="num">{judgment.get("overall","?")}<span style="font-size:1.2rem">/10</span></div>
                <div class="label">Judge Score</div>
            </div>
            <br><br>
            <span class="verdict-badge {vcls}">{verdict}</span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        judge_metrics = [
            ("Clarity", "clarity"),
            ("Keywords", "keywords"),
            ("Professionalism", "professionalism"),
            ("ATS Ready", "ats_ready"),
            ("Recruiter Appeal", "recruiter_appeal"),
            ("Uniqueness", "uniqueness"),
        ]
        for i, (label, key) in enumerate(judge_metrics):
            with cols[i % 3]:
                score = judgment.get(key, 7)
                color = "#4ade80" if score >= 8 else "#fbbf24" if score >= 6 else "#f87171"
                st.markdown(f"""
                <div class="score-ring" style="margin-bottom:1rem;">
                    <div class="num" style="color:{color}">{score}</div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">⭐ Best Part</div>', unsafe_allow_html=True)
            st.success(judgment.get("best_part", ""))
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">🔧 Critical Fix</div>', unsafe_allow_html=True)
            st.warning(judgment.get("critical_fix", ""))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">📋 Detailed Feedback</div>', unsafe_allow_html=True)
        st.markdown(judgment.get("detailed_feedback", ""))
        st.markdown('</div>', unsafe_allow_html=True)

        # History
        if st.session_state.history:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-head">🕐 Run History</div>', unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)