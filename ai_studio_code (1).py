import streamlit as st
import time
from openai import OpenAI  # Import OpenAI for AI functionalities
import os

# ==========================================
# PAGE CONFIG & CSS (Modern, Minimalistic UI)
# ==========================================
st.set_page_config(page_title="ET ThinkFeed | AI News", page_icon="📰", layout="wide")

st.markdown("""
    <style>
    /* Modern minimalist typography and styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: #f4f1e8; /* Newspaper paper color */
        background-image: 
            radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 0);
        background-size: 20px 20px;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E3A8A;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .news-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: transform 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-image: 
            linear-gradient(90deg, transparent 49%, rgba(0,0,0,0.02) 50%, transparent 51%),
            linear-gradient(transparent 49%, rgba(0,0,0,0.02) 50%, transparent 51%);
        background-size: 20px 20px, 20px 20px;
    }
    .news-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #2563EB, #9333EA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }
    .page-container {
        background: #f4f1e8;
        background-image: 
            radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 0);
        background-size: 20px 20px;
        min-height: 100vh;
        padding: 20px;
        animation: pageFlipIn 0.8s ease-out;
    }
    @keyframes pageFlipIn {
        0% {
            transform: rotateY(-90deg) scale(0.8);
            opacity: 0;
        }
        50% {
            transform: rotateY(-45deg) scale(0.9);
            opacity: 0.5;
        }
        100% {
            transform: rotateY(0deg) scale(1);
            opacity: 1;
        }
    }
    </style>
    <style>
    /* ET Economic Times color palette */
    html, body, [class*="css"] {
        background: #f5f6fa;
    }
    .et-logo {
        display: inline-block;
        background: #d71920;
        color: #fff;
        font-weight: 900;
        font-size: 2.2rem;
        font-family: 'Inter', sans-serif;
        border-radius: 4px;
        padding: 0.1em 0.45em 0.1em 0.45em;
        margin-right: 0.25em;
        letter-spacing: 0.01em;
        vertical-align: middle;
    }
    .thinkfeed-title {
        display: inline-block;
        font-size: 2.2rem;
        font-weight: 700;
        color: #222;
        letter-spacing: 0.01em;
        vertical-align: middle;
    }
    .et-section {
        background: #fff;
        background-image: 
            linear-gradient(90deg, transparent 49%, rgba(0,0,0,0.01) 50%, transparent 51%),
            linear-gradient(transparent 49%, rgba(0,0,0,0.01) 50%, transparent 51%);
        background-size: 20px 20px, 20px 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1.2rem;
        padding: 1.2rem 1.5rem 1.2rem 1.5rem;
        box-shadow: 0 2px 8px 0 rgba(0,0,0,0.03);
    }
    .et-featured {
        background: #fff4f4;
        border-left: 4px solid #d71920;
        padding: 0.7em 1em;
        margin-bottom: 1em;
        border-radius: 4px;
        font-weight: 600;
        color: #b71c1c;
    }
    </style>
""", unsafe_allow_html=True)

# --- PAGE FLIP ANIMATION OVERLAY ---
st.markdown("""
    <style>
    .page-flip-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        width: 100vw; height: 100vh;
        background: #f4f1e8;
        background-image: radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 0);
        background-size: 20px 20px;
        z-index: 9999;
        pointer-events: none;
        opacity: 0;
        transform: rotateY(-90deg) scale(0.8);
        transition: none;
    }
    .page-flip-overlay.active {
        animation: pageFlipIn 0.8s cubic-bezier(.77,0,.18,1) forwards;
    }
    @keyframes pageFlipIn {
        0% {
            opacity: 0;
            transform: rotateY(-90deg) scale(0.8);
        }
        50% {
            opacity: 0.5;
            transform: rotateY(-45deg) scale(0.9);
        }
        100% {
            opacity: 0;
            transform: rotateY(0deg) scale(1);
        }
    }
    </style>
    <div id="page-flip-overlay" class="page-flip-overlay"></div>
    <script>
    window.triggerPageFlip = function() {
        var overlay = document.getElementById('page-flip-overlay');
        if (!overlay) return;
        overlay.classList.remove('active');
        void overlay.offsetWidth; // force reflow
        overlay.classList.add('active');
        setTimeout(function(){ overlay.classList.remove('active'); }, 900);
    }
    </script>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .et-category {
        color: #d71920;
        font-weight: 700;
        margin-bottom: 0.5em;
        font-size: 1.1em;
    }
    .et-news-headline {
        font-size: 1.1em;
        font-weight: 700;
        color: #222;
        margin-bottom: 0.2em;
    }
    .et-news-preview {
        color: #444;
        font-size: 0.98em;
        margin-bottom: 0.5em;
    }
    .et-upvotes {
        color: #d71920;
        font-weight: 700;
        font-size: 1em;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        background: #d71920;
        color: #fff;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: #b71c1c;
        color: #fff;
        box-shadow: 0 2px 8px 0 rgba(215,25,32,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# MOCK DATABASE (Pseudo-RAG Data)
# ==========================================
# Time context constraint: March 29, 2026. Location: India.
NEWS_DB = {
    "national":[
        {
            "id": "n1",
            "headline": "India's UPI Processed 15 Billion Transactions in March 2026",
            "preview": "Unified Payments Interface achieves a massive new milestone, but infrastructure strains are showing.",
            "likes": 24500,
            "articles":[
                "NPCI reports an unprecedented 15.2 billion transactions logged by March 28, 2026.",
                "Rural fintech adoption, especially voice-based UPI payments, drove 40% of the new growth.",
                "Several banking servers experienced micro-outages last week due to the massive transaction load.",
                "Experts suggest RBI may consider a micro-fee for transactions above ₹10,000 to fund server upgrades, though NPCI denies immediate plans."
            ]
        },
        {
            "id": "n2",
            "headline": "ISRO Successfully Docks 'Vyom' Module with ISS",
            "preview": "In a historic first, India's autonomous module connects with the International Space Station.",
            "likes": 42100,
            "articles":[
                "ISRO's Vyom experimental habitat successfully docked with the ISS at 14:00 IST today.",
                "The module will serve as a microgravity lab for Indian pharmaceutical startups for the next 6 months.",
                "NASA praised the automated docking sequence, which was powered by a new Indian-built AI vision system.",
                "Rumors suggest this is the final test before India launches its independent space station in 2028."
            ]
        }
    ],
    "global":[
        {
            "id": "g1",
            "headline": "EU Passes the 'Neural Data Privacy' Act",
            "preview": "First-of-its-kind legislation targets BCI (Brain-Computer Interface) tech companies.",
            "likes": 18900,
            "articles":[
                "The European Union voted 450-120 to pass the Neural Data Privacy Act this morning.",
                "Companies like Neuralink and Synchron must now process all neural data entirely on-device; no cloud storage permitted.",
                "Tech stocks tumbled, with major BCI manufacturers dropping 5-8% on the Frankfurt exchange.",
                "Critics argue this will stall medical research for paralysis treatments by cutting off large datasets."
            ]
        },
        {
            "id": "g2",
            "headline": "Solid-State Battery Breakthrough Enables 1000-mile EV Range",
            "preview": "Toyota and MIT unveil a commercially viable solid-state cell ready for 2027 production.",
            "likes": 31000,
            "articles":[
                "Researchers successfully scaled a sulfide-based solid-state battery that doesn't degrade for 5,000 cycles.",
                "The new cells allow EVs to travel 1,000 miles on a single 10-minute charge.",
                "Lithium futures plummeted globally as the new tech requires significantly less raw lithium.",
                "Initial rollouts will be restricted to luxury vehicle models due to high initial manufacturing costs."
            ]
        }
    ]
}

# Derived trending (combining and sorting by likes)
all_news = NEWS_DB["national"] + NEWS_DB["global"]
NEWS_DB["trending"] = sorted(all_news, key=lambda x: x["likes"], reverse=True)

# ==========================================
# STATE MANAGEMENT
# ==========================================
if "current_view" not in st.session_state:
    st.session_state.current_view = "homepage"
if "previous_view" not in st.session_state:
    st.session_state.previous_view = "homepage"
if "selected_article" not in st.session_state:
    st.session_state.selected_article = None
if "briefing_cache" not in st.session_state:
    st.session_state.briefing_cache = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history =[]
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# AI AGENT LOGIC (With Robust Demo Fallback)
# ==========================================
def run_agent(system_prompt, user_prompt, max_tokens=300):
    """
    Executes the AI request. 
    Includes a highly reliable fallback mechanism if no API key is provided 
    so the app remains fully functional for demos.
    """
    if not st.session_state.api_key:
        time.sleep(1.5) # Simulate API latency
        return _mock_ai_response(system_prompt, user_prompt)

    try:
        client = OpenAI(api_key=st.session_state.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ **API Error:** {str(e)}\n\n*(Falling back to standard view)*\n\n" + _mock_ai_response(system_prompt, user_prompt)

def _mock_ai_response(system, user):
    """Simulates realistic, intelligent responses based on context to guarantee demo reliability."""
    if "TL;DR" in system:
        return "### TL;DR\nA major development has occurred, fundamentally shifting the landscape. The events are driven by new adoptions and breakthroughs, yet face infrastructural or regulatory hurdles.\n\n### Key Insights\n- Massive scale reached unexpectedly.\n- Secondary markets/sectors heavily impacted.\n- Innovation outpacing current regulatory/hardware capacity.\n\n### Who is Impacted\nConsumers, direct industry stakeholders, and peripheral supply chains.\n\n### Why it Matters\nThis establishes a new benchmark for the sector and will force competitors and regulators to immediately adapt or be left behind."
    elif "Student" in system:
        return "Hey! Think of this like upgrading your phone's OS. Everyone wants the cool new features, but the servers are struggling to handle everyone downloading it at once. It's a huge step forward for technology!"
    elif "Investor" in system:
        return "This is a strong bullish signal for primary tech operators but reveals supply-chain/infrastructure bottlenecks. Look to invest in the secondary infrastructure providers who will be contracted to fix these bottlenecks."
    elif "Founder" in system:
        return "Opportunity alert: The big players are creating a massive new ecosystem but leaving gaps in user-experience and backend stability. Build agile SaaS or middleware solutions that solve these specific friction points."
    elif "investigative journalist" in system or "facts" in system.lower():
        return "✅ **Verified Facts:**\n- The event officially occurred and was recorded.\n- Metric targets were achieved.\n\n❓ **Speculation/Rumors:**\n- Regulatory bodies may impose new rules or fees.\n- The underlying tech could be a precursor to a larger project."
    elif "Predict" in system or "consequence" in system or "What happens next" in system:
        return "1. **Short-term:** Increased attention from regulators and industry stakeholders.\n2. **Long-term:** Potential for new industry standards and market shifts."
    elif "Q&A bot" in system or "question" in system.lower():
        # Try to extract a plausible answer from the user/context, else fallback
        if "impact" in user.lower():
            return "The impact includes significant changes for both consumers and industry players, with new opportunities and challenges emerging as a result of this event."
        elif "explain" in user.lower() and "kid" in user.lower():
            return "Imagine something really big happened in technology, like everyone suddenly using a new app. It's exciting, but it also means the people running it have to work extra hard to keep everything working smoothly!"
        else:
            return "Based on the provided sources, the answer is: The event marks a major milestone and will likely influence related sectors and future developments."
    else:
        return "Based on the provided articles, this is a complex issue requiring adaptive strategies. Can you specify which aspect you'd like to dive deeper into?"

# ==========================================
# UI COMPONENTS
# ==========================================
def render_news_card(article, context=""):
    with st.container(border=True):
        st.subheader(article["headline"])
        st.write(article["preview"])
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.markdown(f"👍 **{article['likes']:,}** Upvotes")
        with cols[2]:
            if st.button("Generate AI Briefing ✨", key=f"btn_{article['id']}_{context}", use_container_width=True):
                st.session_state.selected_article = article
                st.session_state.current_view = "briefing"
                st.session_state.chat_history =[]
                st.rerun()

def view_homepage():
    st.markdown('<span class="et-logo">ET</span><span class="thinkfeed-title">ThinkFeed</span>', unsafe_allow_html=True)
    st.markdown("""
    <script>
    if (window.triggerPageFlip) window.triggerPageFlip();
    </script>
    """, unsafe_allow_html=True)
    st.write("<span style='color:#d71920;font-weight:600;'>India's Most Trusted AI News Feed</span>", unsafe_allow_html=True)
    st.divider()

    left, center, right = st.columns([2, 5, 2])

    # Sidebar: News by Industry
    with left:
        st.markdown('<div class="et-section">', unsafe_allow_html=True)
        st.markdown('<div class="et-category">News by Industry</div>', unsafe_allow_html=True)
        st.markdown('<div class="et-featured">FEATURED</div>', unsafe_allow_html=True)
        industries = ["AUTO", "BANKING / FINANCE", "CONS. PRODUCTS", "ENERGY", "RENEWABLES", "IND'L GOODS / SVS", "INTERNET", "HEALTHCARE", "JOBS", "RETAIL", "SERVICES", "RISE", "MEDIA", "TECH", "TELECOM", "TRANSPORTATION"]
        for ind in industries:
            st.markdown(f'<div style="margin-bottom:0.4em;">{ind}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Main News Feed
    with center:
        st.markdown('<div class="et-section">', unsafe_allow_html=True)
        st.markdown('<div class="et-category">Top Stories</div>', unsafe_allow_html=True)
        tabs = st.tabs(["🇮🇳 National", "🌍 Global", "🔥 Trending"])
        with tabs[0]:
            for article in NEWS_DB["national"]:
                render_news_card(article, "national")
        with tabs[1]:
            for article in NEWS_DB["global"]:
                render_news_card(article, "global")
        with tabs[2]:
            for article in NEWS_DB["trending"]:
                render_news_card(article, "trending")
        st.markdown('</div>', unsafe_allow_html=True)

    # Right Sidebar: India/Trending
    with right:
        st.markdown('<div class="et-section">', unsafe_allow_html=True)
        st.markdown('<div class="et-category">India</div>', unsafe_allow_html=True)
        for article in NEWS_DB["national"][:3]:
            st.markdown(f'<div class="et-news-headline">{article["headline"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="et-news-preview">{article["preview"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def view_briefing():
    st.markdown("""
    <script>
    if (window.triggerPageFlip) window.triggerPageFlip();
    </script>
    """, unsafe_allow_html=True)
    article = st.session_state.selected_article
    context = "\n".join([f"Source {i+1}: {txt}" for i, txt in enumerate(article['articles'])])
    
    # Header & Nav
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_view = "homepage"
            st.rerun()
    with col2:
        st.markdown(f"## {article['headline']}")

    # Ensure caching so we don't spam APIs on UI reruns (like chat)
    cache_key = article['id']
    if cache_key not in st.session_state.briefing_cache:
        with st.spinner("🧠 Analyzing multiple sources and synthesizing intelligence..."):
            
            # Core Briefing Generation
            prompt_system_core = "You are an expert intelligence analyst. Given the news sources, extract the core facts and structure them exactly into four sections: TL;DR, Key Insights (bullets), Who is impacted, and Why it matters."
            core_briefing = run_agent(prompt_system_core, f"Sources:\n{context}", max_tokens=350)
            
            # Innovation: Truth Radar Generation
            prompt_system_truth = "You are an investigative journalist. Separate the provided text strictly into two categories: '✅ Verified Facts' and '❓ Speculation/Rumors'."
            truth_radar = run_agent(prompt_system_truth, f"Sources:\n{context}", max_tokens=250)
            
            # Prediction Generation
            prompt_system_pred = "Predict 'What happens next?'. Give 1 short-term consequence and 1 long-term consequence based only on the context provided."
            predictions = run_agent(prompt_system_pred, f"Sources:\n{context}", max_tokens=200)

            st.session_state.briefing_cache[cache_key] = {
                "context": context,
                "core": core_briefing,
                "truth": truth_radar,
                "predictions": predictions,
                "personas": {}
            }

    data = st.session_state.briefing_cache[cache_key]

    # Layout: Two columns (Main Briefing vs Intelligence Tools)
    main_col, side_col = st.columns([6, 4])

    with main_col:
        # Core Briefing
        st.markdown("### 📄 Intelligence Briefing")
        st.info(data["core"])

        # Persona Section
        st.markdown("### 🎭 Persona Mode (Explain it to me like I am...)")
        persona_choice = st.radio("Select Persona:", ["🎓 Student", "💼 Investor", "🚀 Founder"], horizontal=True, label_visibility="collapsed")
        
        # Lazy load persona generations to save tokens/time
        if persona_choice not in data["personas"]:
            with st.spinner(f"Adapting tone for {persona_choice}..."):
                p_prompt = f"Explain the core of this news assuming the reader is a {persona_choice}. Focus on personal relevance to them ('Why you should care'). Max 3 sentences."
                data["personas"][persona_choice] = run_agent(p_prompt, f"Context:\n{context}", max_tokens=150)
        
        st.success(f"**Relevance to you:**\n\n{data['personas'][persona_choice]}")

    with side_col:
        # Innovative Feature: Truth Radar
        with st.container(border=True):
            st.markdown("### 📡 Signal vs. Noise Radar")
            st.caption("AI analyzes sources to separate hard facts from media speculation.")
            st.write(data["truth"])

        # Optional: Predictions
        with st.container(border=True):
            st.markdown("### 🔮 What Happens Next?")
            st.write(data["predictions"])

    st.divider()

    # Interactive Q&A
    st.markdown("### 💬 Deep Dive Q&A")
    st.caption("Ask questions strictly about this news event. The AI will answer based *only* on the provided sources.")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about this news..."):
        # Add user message to state and UI
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                sys_chat = "You are a Q&A bot. Answer the user's question using ONLY the provided context. If the answer is not in the context, say 'The provided sources do not contain information on this.'"
                usr_chat = f"Context:\n{context}\n\nQuestion: {prompt}"
                answer = run_agent(sys_chat, usr_chat, max_tokens=200)
                st.markdown(answer)
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    # No page-container wrapper here

# ==========================================
# SIDEBAR (Settings)
# ==========================================
with st.sidebar:
    st.markdown("### 📰 About ET ThinkFeed")
    st.info("AI-powered news, inspired by The Economic Times. All content is demo/mock for reliability.")
    st.divider()
    st.markdown("""
    **Architecture Info:**
    - Simulated RAG pipeline
    - Modular AI Agents
    - Built with Streamlit
    """)

# ==========================================
# APP ROUTING
# ==========================================
if st.session_state.current_view != st.session_state.previous_view:
    st.markdown("""<script>window.triggerPageFlip();</script>""", unsafe_allow_html=True)
    st.session_state.previous_view = st.session_state.current_view

if st.session_state.current_view == "homepage":
    view_homepage()
elif st.session_state.current_view == "briefing":
    view_briefing()