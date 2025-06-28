import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
import time
import PyPDF2
import io
import interview
import role_playing
import linkscraper

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="CareerOracle - Mystical Career Advisor",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for multi-page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'selected_role_index' not in st.session_state:
    st.session_state.selected_role_index = None
if 'game_data' not in st.session_state:
    st.session_state.game_data = {}
if 'interview_data' not in st.session_state:
    st.session_state.interview_data = {}

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .oracle-logo {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #667eea, 0 0 20px #667eea; }
        to { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #667eea, 0 0 40px #667eea; }
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.3rem;
        font-style: italic;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .job-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    .job-title {
        font-size: 1.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    .job-description {
        color: #6c757d;
        margin-bottom: 1rem;
    }
    .experience-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .experience-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
    .personality-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(33, 150, 243, 0.1);
    }
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px dashed #dee2e6;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f0f2ff 0%, #e8eaff 100%);
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    .score-item {
        background-color: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .score-bar {
        background-color: rgba(255,255,255,0.2);
        border-radius: 10px;
        height: 20px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .overall-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .strengths-section {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(212, 237, 218, 0.3);
    }
    .considerations-section {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(255, 243, 205, 0.3);
    }
    .mystical-border {
        border: 2px solid transparent;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea) border-box;
        border-radius: 15px;
        background-clip: padding-box, border-box;
        position: relative;
    }
    .mystical-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 15px;
        z-index: -1;
        animation: borderGlow 3s ease-in-out infinite alternate;
    }
    @keyframes borderGlow {
        from { opacity: 0.7; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        st.error(f"Error reading PDF file: {str(e)}")
        return None

def generate_job_recommendations(cv_text, personality_type):
    """Generate job recommendations based on CV and personality type"""
    
    prompt = f"""
    Analyze the following CV and personality type to generate 3-5 suitable job recommendations.
    
    CV Content: {cv_text[:2000]}  # Limit to first 2000 characters
    
    Personality Type: {personality_type}
    
    For each job recommendation, provide:
    1. Job title
    2. Brief description of the role
    3. Suitability score (1-10)
    4. Suitability level (Excellent/Good/Fair/Poor)
    5. Estimated salary range
    6. Growth potential (High/Medium/Low)
    
    Return as JSON:
    {{
        "recommendations": [
            {{
                "title": "Job Title",
                "description": "Role description",
                "score": 8.5,
                "suitability": "Excellent",
                "salary_range": "$60,000 - $80,000",
                "growth_potential": "High"
            }}
        ]
    }}
    
    Make recommendations specific to the CV content and personality type. Focus on roles where the candidate's background and personality would be a good fit.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career advisor analyzing CVs and personality types to recommend suitable job roles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)['recommendations']
    
    except Exception as e:
        # Fallback recommendations
        return [
            {
                "title": "Software Developer",
                "description": "Develop and maintain software applications using modern programming languages and frameworks.",
                "score": 7.5,
                "suitability": "Good",
                "salary_range": "$70,000 - $100,000",
                "growth_potential": "High"
            },
            {
                "title": "Data Analyst",
                "description": "Analyze data to help organizations make informed business decisions and improve processes.",
                "score": 7.0,
                "suitability": "Good",
                "salary_range": "$60,000 - $85,000",
                "growth_potential": "High"
            },
            {
                "title": "Project Manager",
                "description": "Lead and coordinate projects, ensuring they are completed on time and within budget.",
                "score": 6.5,
                "suitability": "Fair",
                "salary_range": "$75,000 - $110,000",
                "growth_potential": "Medium"
            }
        ]

def generate_job_roles(personality_type, cv_content):
    """Generate job roles based on personality type and CV content"""
    
    prompt = f"""
    Based on the following personality type and CV content, suggest 5-7 job roles that would be a great fit.
    
    Personality Type: {personality_type}
    CV Content: {cv_content}
    
    For each job role, provide:
    1. Job Title
    2. Brief description of why it's a good fit
    3. Key responsibilities
    4. Required skills
    
    Return the response as a JSON array with the following structure:
    [
        {{
            "title": "Job Title",
            "description": "Why this role fits the personality and background",
            "responsibilities": ["Responsibility 1", "Responsibility 2", "Responsibility 3"],
            "skills": ["Skill 1", "Skill 2", "Skill 3"]
        }}
    ]
    
    Focus on roles that align with the personality type and leverage the skills/experience mentioned in the CV.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career advisor specializing in matching personality types and backgrounds with suitable job roles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        # Extract JSON from the response (in case there's additional text)
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        st.error(f"Error generating job roles: {str(e)}")
        return []

def experience_job_role(job_title, job_description, personality_type):
    """Generate an interactive job role experience using LLM"""
    
    prompt = f"""
    Create an interactive job role experience for: {job_title}
    
    Job Description: {job_description}
    User's Personality Type: {personality_type}
    
    Provide a realistic day-in-the-life scenario with:
    1. A typical morning routine
    2. Key tasks and challenges for the day
    3. Interactions with colleagues/clients
    4. Decision-making scenarios
    5. End-of-day reflection
    
    Make it engaging and interactive, as if the user is actually experiencing this role.
    Include specific details and realistic scenarios that someone in this position would encounter.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an immersive career simulation expert. Create engaging, realistic job role experiences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating job experience: {str(e)}"

def generate_role_score(job_title, job_description, personality_type, experience_content):
    """Generate quantitative scores for the job role based on multiple criteria"""
    
    prompt = f"""
    Based on the job role and the user's personality type, provide a quantitative assessment of this role.
    
    Job Title: {job_title}
    Job Description: {job_description}
    User's Personality Type: {personality_type}
    Experience Content: {experience_content}
    
    Evaluate this role on a scale of 1-10 for each of the following criteria:
    
    1. **Personality Fit** (1-10): How well does this role align with the user's personality type?
    2. **Skill Match** (1-10): How well do the required skills match the user's background?
    3. **Growth Potential** (1-10): What are the career advancement opportunities?
    4. **Work-Life Balance** (1-10): How balanced is the workload and schedule?
    5. **Compensation Potential** (1-10): What is the earning potential and benefits?
    6. **Job Security** (1-10): How stable and secure is this position?
    7. **Learning Opportunities** (1-10): How much continuous learning and development is available?
    8. **Team Dynamics** (1-10): How collaborative and supportive is the work environment?
    
    Return the response as a JSON object with the following structure:
    {{
        "scores": {{
            "personality_fit": score,
            "skill_match": score,
            "growth_potential": score,
            "work_life_balance": score,
            "compensation_potential": score,
            "job_security": score,
            "learning_opportunities": score,
            "team_dynamics": score
        }},
        "overall_score": average_score,
        "strengths": ["strength1", "strength2", "strength3"],
        "considerations": ["consideration1", "consideration2", "consideration3"],
        "recommendation": "brief recommendation based on scores"
    }}
    
    Be objective and realistic in your scoring. Consider the specific personality type and job requirements.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career assessment expert who provides objective, data-driven evaluations of job roles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        # Extract JSON from the response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        return {
            "scores": {
                "personality_fit": 5,
                "skill_match": 5,
                "growth_potential": 5,
                "work_life_balance": 5,
                "compensation_potential": 5,
                "job_security": 5,
                "learning_opportunities": 5,
                "team_dynamics": 5
            },
            "overall_score": 5.0,
            "strengths": ["Unable to generate strengths"],
            "considerations": ["Unable to generate considerations"],
            "recommendation": "Unable to generate recommendation"
        }

def main_page():
    """Main page with job recommendations and results"""
    # Header with Oracle Logo
    st.markdown('<div class="oracle-logo">🔮</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="color: #495057; margin-bottom: 0.5rem;">🔮 CareerOracle</h1>
        <p style="color: #6c757d; font-size: 1.2rem; margin-bottom: 2rem;">The Mystical Career Advisor</p>
        <p style="color: #495057; font-size: 1rem;">Upload your CV and reveal your destined career path through the Oracle's mystical trials...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.5rem; margin-bottom: 2rem;">
            <h3 style="color: white; margin-bottom: 1rem;">🔮 Oracle's Portal</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Personality type selection
        st.markdown("**🌟 Choose Your Personality Type:**")
        personality_types = [
            "INTJ - The Architect",
            "INTP - The Logician", 
            "ENTJ - The Commander",
            "ENTP - The Debater",
            "INFJ - The Advocate",
            "INFP - The Mediator",
            "ENFJ - The Protagonist",
            "ENFP - The Campaigner",
            "ISTJ - The Logistician",
            "ISFJ - The Defender",
            "ESTJ - The Executive",
            "ESFJ - The Consul",
            "ISTP - The Virtuoso",
            "ISFP - The Adventurer",
            "ESTP - The Entrepreneur",
            "ESFP - The Entertainer"
        ]
        
        selected_personality = st.selectbox(
            "Select your personality type:",
            personality_types,
            key="personality_selector"
        )
        
        if selected_personality:
            st.session_state.personality_type = selected_personality
        
        # CV upload
        st.markdown("**📄 Upload Your CV:**")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            key="cv_uploader"
        )
        
        if uploaded_file is not None:
            # Extract text from PDF
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                cv_text = ""
                for page in pdf_reader.pages:
                    cv_text += page.extract_text()
                
                st.session_state.cv_text = cv_text
                
                # Show preview
                with st.expander("📄 CV Preview"):
                    st.text_area("Extracted text:", cv_text[:500] + "..." if len(cv_text) > 500 else cv_text, height=200)
                
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
        
        # Generate recommendations button
        if st.button("🔮 Seek Oracle's Prophecy", type="primary"):
            if 'cv_text' in st.session_state and 'personality_type' in st.session_state:
                with st.spinner("🔮 The Oracle is reading your destiny..."):
                    recommendations = generate_job_recommendations(
                        st.session_state.cv_text,
                        st.session_state.personality_type
                    )
                    st.session_state.job_recommendations = recommendations
                st.success("Oracle's prophecies have been revealed!")
            else:
                st.error("Please upload your CV and select your personality type.")
    
    # Display job recommendations
    if 'job_recommendations' in st.session_state and st.session_state.job_recommendations:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center;">
                <h2 style="color: white; margin-bottom: 0.5rem;">🔮 Oracle's Prophecies</h2>
                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Your destined career paths have been revealed...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display each job recommendation
        for i, job in enumerate(st.session_state.job_recommendations):
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border: 2px solid #e9ecef; border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h3 style="color: #495057; margin-bottom: 1rem;">🌟 {job['title']}</h3>
                    <p style="color: #6c757d; margin-bottom: 1rem;"><strong>Oracle's Vision:</strong> {job['description']}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="color: #495057; margin: 0;"><strong>Destiny Score:</strong> {job['score']:.1f}/10</p>
                            <p style="color: #6c757d; margin: 0;"><strong>Alignment Level:</strong> {job['suitability']}</p>
                        </div>
                        <div>
                            <p style="color: #495057; margin: 0;"><strong>Salary Range:</strong> {job['salary_range']}</p>
                            <p style="color: #6c757d; margin: 0;"><strong>Growth Potential:</strong> {job['growth_potential']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if game has been completed for this role
                game_key = f"game_completed_{i}"
                interview_key = f"interview_completed_{i}"
                
                if game_key in st.session_state and st.session_state[game_key]:
                    # Show completed game indicator
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 1px solid #c3e6cb; border-radius: 10px; padding: 1rem; margin: 1rem 0; text-align: center;">
                        <h4 style="color: #155724; margin-bottom: 0.5rem;">✅ Oracle's Trial Completed</h4>
                        <p style="color: #155724; margin: 0;">You have completed the mystical trials for this role. Click below to view your results.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(f"🔮 View Oracle's Revelation for {job['title']}", key=f"view_results_{i}"):
                            st.session_state.current_page = 'game'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                if interview_key in st.session_state and st.session_state[interview_key]:
                    # Show completed interview indicator
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%); border: 1px solid #bee5eb; border-radius: 10px; padding: 1rem; margin: 1rem 0; text-align: center;">
                        <h4 style="color: #0c5460; margin-bottom: 0.5rem;">✅ Professional Interview Completed</h4>
                        <p style="color: #0c5460; margin: 0;">You have completed the professional interview for this role. Click below to view your results.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(f"🎤 View Interview Results for {job['title']}", key=f"view_interview_{i}"):
                            st.session_state.current_page = 'interview'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                # Show action buttons
                if (game_key not in st.session_state or not st.session_state[game_key]) and (interview_key not in st.session_state or not st.session_state[interview_key]):
                    # All three options available
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"🔮 Immersive Experience for {job['title']}", key=f"start_game_{i}"):
                            st.session_state.current_page = 'game'
                            st.session_state.selected_role_index = i
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🎤 Mock Interview for {job['title']}", key=f"start_interview_{i}"):
                            st.session_state.current_page = 'interview'
                            st.session_state.selected_role_index = i
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🔍 Real-time Jobs for {job['title']}", key=f"start_job_finder_{i}"):
                            st.session_state.current_page = 'job_finder'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                elif game_key in st.session_state and st.session_state[game_key] and (interview_key not in st.session_state or not st.session_state[interview_key]):
                    # Only interview and job finder available
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"🎤 Mock Interview for {job['title']}", key=f"start_interview_{i}"):
                            st.session_state.current_page = 'interview'
                            st.session_state.selected_role_index = i
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🔍 Real-time Jobs for {job['title']}", key=f"start_job_finder_{i}"):
                            st.session_state.current_page = 'job_finder'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                elif interview_key in st.session_state and st.session_state[interview_key] and (game_key not in st.session_state or not st.session_state[game_key]):
                    # Only Oracle's trial and job finder available
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"🔮 Immersive Experience for {job['title']}", key=f"start_game_{i}"):
                            st.session_state.current_page = 'game'
                            st.session_state.selected_role_index = i
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🔍 Real-time Jobs for {job['title']}", key=f"start_job_finder_{i}"):
                            st.session_state.current_page = 'job_finder'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                else:
                    # Only job finder available (both trials completed)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(f"🔍 Real-time Jobs for {job['title']}", key=f"start_job_finder_{i}"):
                            st.session_state.current_page = 'job_finder'
                            st.session_state.selected_role_index = i
                            st.rerun()
    
    # Initial state or no recommendations yet
    elif 'cv_text' not in st.session_state:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 20px; padding: 4rem; margin: 4rem 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="color: #495057; margin-bottom: 1rem;">🔮 Welcome to CareerOracle</h2>
            <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">
                Upload your CV and select your personality type in the sidebar to begin your mystical career journey.
            </p>
            <p style="color: #495057;">
                The Oracle will reveal your destined career paths and guide you through interactive trials to test your alignment with each role.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Main app logic
def main():
    # Page navigation
    if st.session_state.current_page == 'game':
        role_playing.game_page()
    elif st.session_state.current_page == 'interview':
        interview.interview_page()
    elif st.session_state.current_page == 'job_finder':
        linkscraper.job_finder_page()
    else:
        main_page()

if __name__ == "__main__":
    main() 