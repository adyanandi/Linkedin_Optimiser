import streamlit as st
from scraper.profile_scraper import scrape_profile_data, setup_driver
from analyzer.analyze import analyze_linkedin_profile
from scraper.TopSkills import get_top_skills

# ---------- Page Configuration ----------
st.set_page_config(page_title="LinkedIn AI Optimizer", layout="centered", page_icon="🔗")

# ---------- Custom Styling ----------
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f9;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .stButton button {
        background-color: #0072b1;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: background 0.3s ease;
    }
    .stButton button:hover {
        background-color: #005582;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Title & Subtitle ----------
st.markdown("<h1 style='text-align: center;'>🔍 LinkedIn Optimizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Scrape, Analyze, and Optimize your LinkedIn profile using AI</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Session Initialization ----------
if 'profile_analyzed' not in st.session_state:
    st.session_state.profile_analyzed = False
if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = None
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None

# ---------- Input Section ----------
st.markdown("### 📎 Enter your LinkedIn Profile URL:")
profile_url = st.text_input("", placeholder="https://www.linkedin.com/in/your-profile")

if st.button("🚀 Scrape & Analyze"):
    if profile_url:
        with st.spinner("🛠️ Setting up WebDriver..."):
            driver = setup_driver()

        with st.spinner("🔍 Scraping LinkedIn profile..."):
            try:
                scraped_data = scrape_profile_data(driver, profile_url)
            except Exception as e:
                st.error(f"❌ Error during scraping: {e}")
                driver.quit()
                st.stop()

        driver.quit()
        st.success("✅ Profile scraped successfully!")

        with st.spinner("🤖 Analyzing with AI..."):
            try:
                ai_summary = analyze_linkedin_profile(scraped_data)
                st.session_state.ai_summary = ai_summary
                st.session_state.scraped_data = scraped_data
                st.session_state.profile_analyzed = True
            except Exception as e:
                st.error(f"❌ AI Processing Failed: {e}")
                st.stop()
    else:
        st.warning("⚠️ Please enter a valid LinkedIn profile URL.")

# ---------- Display AI Summary if Available ----------
if st.session_state.ai_summary:
    st.markdown("### 🧠 AI Summary & Suggestions:")
    st.info(st.session_state.ai_summary)

# ---------- Sidebar for Top Skills ----------
if st.session_state.profile_analyzed:
    st.sidebar.header("👀 Want to know the Top Skills in Demand?")
    st.sidebar.write("Curious to see which skills are trending in your field? Type a job role and press the button below to explore!")
    job_role = st.sidebar.text_input("Enter the job role you're interested in:", placeholder="e.g. Data Scientist")

    if st.sidebar.button("💼 Get Top Skills"):
        if job_role:
            try:
                top_skills = get_top_skills(job_role)
                if top_skills:
                    st.sidebar.markdown("### 🔝 Top 5 Skills:")
                    for idx, (skill, count) in enumerate(top_skills, start=1):
                        st.sidebar.markdown(f"{idx}. {skill.capitalize()}")
                else:
                    st.sidebar.warning(f"⚠️ No top skills found for '{job_role}'")
            except Exception as e:
                st.sidebar.error(f"❌ Error fetching skills: {e}")
        else:
            st.sidebar.warning("⚠️ Please enter a valid job role.")







