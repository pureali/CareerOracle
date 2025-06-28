import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
import time
import PyPDF2
import io
import interview

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

def generate_role_questions(job_title, job_description, personality_type):
    """Generate 5 specific questions for the role-playing game with multiple choice options"""
    
    prompt = f"""
    Create 5 specific questions for a role-playing game to evaluate a candidate's suitability for: {job_title}
    
    Job Description: {job_description}
    User's Personality Type: {personality_type}
    
    Create exactly:
    3 TECHNICAL questions - specific to the skills, tools, and technical knowledge required for this role
    2 PSYCHOLOGY questions - about work behavior, team dynamics, and soft skills relevant to this role
    
    Technical questions should cover:
    - Specific technical skills, tools, or methodologies
    - Problem-solving in technical scenarios
    - Technical decision-making and best practices
    
    Psychology questions should cover:
    - Work behavior and professional conduct
    - Team collaboration and communication
    - Stress management and adaptability
    
    Each question should have 4 multiple choice options (A, B, C, D) with clear evaluation criteria for scoring 1-10.
    
    Return as JSON:
    {{
        "questions": [
            {{
                "question": "Question text",
                "context": "Brief context or scenario",
                "type": "TECHNICAL" or "PSYCHOLOGY",
                "options": {{
                    "A": "Option A text",
                    "B": "Option B text", 
                    "C": "Option C text",
                    "D": "Option D text"
                }},
                "evaluation_criteria": "What to look for in the answer (1-10 scale)"
            }}
        ]
    }}
    
    Make sure the questions are highly specific to {job_title} and the technical/psychological challenges someone in this role would actually face.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career assessment expert creating role-specific technical and psychology questions for job evaluation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        # Fallback questions based on role type
        if "developer" in job_title.lower() or "programmer" in job_title.lower() or "engineer" in job_title.lower():
            return {
                "questions": [
                    {
                        "question": "How would you approach debugging a complex production issue that's affecting multiple users?",
                        "context": "A critical bug has been reported in production affecting user authentication.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Immediately deploy a hotfix without testing to resolve the issue quickly",
                            "B": "Set up a staging environment, reproduce the issue, and test the fix thoroughly",
                            "C": "Ask users to wait while you research the problem in documentation",
                            "D": "Delegate the issue to a more experienced team member"
                        },
                        "evaluation_criteria": "Technical problem-solving, debugging methodology, production safety"
                    },
                    {
                        "question": "What's your approach to code review when a team member submits a large pull request?",
                        "context": "A colleague has submitted a 500-line PR with multiple features.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Approve it quickly to maintain team velocity",
                            "B": "Request it be broken into smaller, focused PRs for better review",
                            "C": "Skip the review since the code looks fine at first glance",
                            "D": "Focus only on the final result, not the implementation details"
                        },
                        "evaluation_criteria": "Code review best practices, attention to detail, team collaboration"
                    },
                    {
                        "question": "How do you handle technical debt when working on new features?",
                        "context": "You need to add a new feature but the existing codebase has significant technical debt.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Ignore the technical debt and focus only on the new feature",
                            "B": "Refactor the relevant code sections while implementing the new feature",
                            "C": "Request a complete codebase rewrite before proceeding",
                            "D": "Implement the feature using workarounds to avoid touching existing code"
                        },
                        "evaluation_criteria": "Technical debt management, code quality awareness, practical approach"
                    },
                    {
                        "question": "How do you handle disagreements with your team lead about technical decisions?",
                        "context": "Your team lead wants to use a different technology than what you recommend.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Accept their decision without question to maintain harmony",
                            "B": "Present your case with data and examples, then accept the final decision",
                            "C": "Continue arguing until they change their mind",
                            "D": "Implement your preferred solution secretly"
                        },
                        "evaluation_criteria": "Professional communication, conflict resolution, team dynamics"
                    },
                    {
                        "question": "How do you manage stress when facing multiple urgent deadlines?",
                        "context": "You have three critical projects due in the same week.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Work overtime and weekends to meet all deadlines",
                            "B": "Prioritize tasks, communicate with stakeholders, and request extensions if needed",
                            "C": "Focus on one project and let the others slip",
                            "D": "Ask colleagues to take over some of your responsibilities"
                        },
                        "evaluation_criteria": "Stress management, prioritization, professional responsibility"
                    }
                ]
            }
        elif "manager" in job_title.lower() or "lead" in job_title.lower():
            return {
                "questions": [
                    {
                        "question": "How do you handle a team member who consistently misses deadlines?",
                        "context": "A team member has missed the last three project deadlines.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Immediately escalate to HR for disciplinary action",
                            "B": "Have a private conversation to understand the root cause and create an improvement plan",
                            "C": "Reduce their workload and give them easier tasks",
                            "D": "Publicly call them out in team meetings"
                        },
                        "evaluation_criteria": "Performance management, communication skills, leadership approach"
                    },
                    {
                        "question": "What's your approach to resource allocation when multiple projects compete for the same team members?",
                        "context": "Three high-priority projects need the same senior developer.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Assign them to the project with the highest budget",
                            "B": "Analyze project priorities, timelines, and team member skills to make an informed decision",
                            "C": "Let the team member choose which project they prefer",
                            "D": "Split their time equally across all three projects"
                        },
                        "evaluation_criteria": "Resource management, strategic thinking, decision-making"
                    },
                    {
                        "question": "How do you measure and track team performance effectively?",
                        "context": "You need to establish KPIs for your development team.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Focus only on lines of code written per developer",
                            "B": "Use a balanced approach including code quality, delivery speed, and team satisfaction",
                            "C": "Let each team member set their own goals",
                            "D": "Rely solely on client feedback"
                        },
                        "evaluation_criteria": "Performance measurement, KPI design, team management"
                    },
                    {
                        "question": "How do you build trust and rapport with a new team member?",
                        "context": "A new senior developer has joined your team.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Give them space to settle in on their own",
                            "B": "Schedule regular 1-on-1s, introduce them to the team, and provide clear onboarding",
                            "C": "Immediately assign them to a high-pressure project to test their skills",
                            "D": "Let them shadow you for the first month"
                        },
                        "evaluation_criteria": "Team building, onboarding, interpersonal skills"
                    },
                    {
                        "question": "How do you handle team conflicts between strong personalities?",
                        "context": "Two senior team members have conflicting opinions on a major technical decision.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Let them resolve it themselves to avoid getting involved",
                            "B": "Facilitate a structured discussion to find common ground and reach consensus",
                            "C": "Make the decision yourself to end the conflict quickly",
                            "D": "Separate them by assigning them to different projects"
                        },
                        "evaluation_criteria": "Conflict resolution, facilitation skills, leadership"
                    }
                ]
            }
        else:
            # Generic questions for other roles
            return {
                "questions": [
                    {
                        "question": "How would you approach learning a new technology required for your role?",
                        "context": "Your role requires expertise in a technology you're not familiar with.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Take a comprehensive online course before starting any work",
                            "B": "Learn through hands-on practice while working on real projects",
                            "C": "Ask colleagues to teach you everything you need to know",
                            "D": "Focus on the basics and learn advanced features later"
                        },
                        "evaluation_criteria": "Learning approach, adaptability, initiative"
                    },
                    {
                        "question": "How do you ensure quality in your work deliverables?",
                        "context": "You need to deliver a high-stakes project to a client.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Rely on your experience and deliver without additional review",
                            "B": "Implement a systematic review process and quality checks",
                            "C": "Ask the client to review and provide feedback",
                            "D": "Focus on meeting the deadline rather than quality"
                        },
                        "evaluation_criteria": "Quality assurance, attention to detail, professional standards"
                    },
                    {
                        "question": "How do you handle feedback and criticism about your work?",
                        "context": "A client has provided negative feedback about your recent deliverable.",
                        "type": "TECHNICAL",
                        "options": {
                            "A": "Defend your work and explain why the feedback is incorrect",
                            "B": "Listen carefully, ask clarifying questions, and use it to improve",
                            "C": "Ignore the feedback and continue with your approach",
                            "D": "Immediately apologize and offer a discount"
                        },
                        "evaluation_criteria": "Feedback handling, professional growth, client relations"
                    },
                    {
                        "question": "How do you maintain work-life balance in a demanding role?",
                        "context": "Your role requires significant time commitment and occasional overtime.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Prioritize work over personal life to ensure success",
                            "B": "Set clear boundaries, manage time effectively, and communicate needs",
                            "C": "Take frequent breaks and work only during regular hours",
                            "D": "Let work consume all your time when projects are busy"
                        },
                        "evaluation_criteria": "Work-life balance, time management, self-care"
                    },
                    {
                        "question": "How do you handle uncertainty and ambiguity in your role?",
                        "context": "Project requirements are unclear and constantly changing.",
                        "type": "PSYCHOLOGY",
                        "options": {
                            "A": "Wait for clear direction before taking any action",
                            "B": "Proactively seek clarification, make reasonable assumptions, and adapt as needed",
                            "C": "Complain about the lack of clear direction",
                            "D": "Make decisions based on your best guess and hope for the best"
                        },
                        "evaluation_criteria": "Adaptability, problem-solving, professional maturity"
                    }
                ]
            }

def evaluate_answer(question, selected_option, job_title, personality_type):
    """Evaluate a user's selected option and provide a score with feedback"""
    
    prompt = f"""
    Evaluate this selected option for a role-playing game question.
    
    Job Title: {job_title}
    User's Personality Type: {personality_type}
    Question: {question['question']}
    Context: {question['context']}
    Evaluation Criteria: {question['evaluation_criteria']}
    Selected Option: {selected_option}
    All Options: {question['options']}
    
    Provide a score from 1-10 and brief feedback.
    
    Return as JSON:
    {{
        "score": score,
        "feedback": "Brief feedback explaining the score",
        "strengths": ["strength1", "strength2"],
        "improvements": ["improvement1", "improvement2"]
    }}
    
    Scoring guide:
    1-3: Poor choice, lacks relevant skills/knowledge
    4-6: Average choice, shows some understanding
    7-8: Good choice, demonstrates relevant capabilities
    9-10: Excellent choice, shows strong alignment with role requirements
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career assessment expert evaluating candidate responses for job suitability."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        return {
            "score": 5,
            "feedback": "Unable to evaluate response",
            "strengths": ["Response provided"],
            "improvements": ["Could provide more specific examples"]
        }

def get_score_label(score):
    """Convert numerical score to descriptive label"""
    if score >= 9:
        return "🌟 Legendary"
    elif score >= 8:
        return "✨ Exceptional"
    elif score >= 7:
        return "🎯 Excellent"
    elif score >= 6:
        return "👍 Good"
    elif score >= 5:
        return "⚖️ Average"
    elif score >= 4:
        return "⚠️ Below Average"
    else:
        return "❌ Needs Improvement"

def generate_final_assessment(job_title, scores, technical_avg, psychology_avg, personality_type):
    """Generate comprehensive final assessment with technical and psychology breakdown"""
    
    overall_score = sum(scores) / len(scores)
    
    prompt = f"""
    Create a comprehensive final assessment for a candidate who completed a role-playing evaluation for: {job_title}
    
    Overall Score: {overall_score:.1f}/10
    Technical Average: {technical_avg:.1f}/10
    Psychology Average: {psychology_avg:.1f}/10
    Personality Type: {personality_type}
    
    Individual Scores: {scores}
    
    Provide a mystical oracle-themed assessment including:
    1. Overall assessment (2-3 sentences)
    2. 3-4 key strengths
    3. 3-4 areas for improvement
    4. Career recommendation (should they pursue this role?)
    
    Return as JSON:
    {{
        "overall_assessment": "Oracle's mystical assessment of the candidate's overall suitability",
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "improvements": ["improvement 1", "improvement 2", "improvement 3"],
        "career_recommendation": "Oracle's final verdict on pursuing this career path"
    }}
    
    Make the assessment specific to the technical vs psychology scores and provide actionable insights.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a mystical career oracle providing final assessments with technical and psychology insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        # Fallback assessment
        if overall_score >= 8:
            recommendation = f"The stars align favorably for your journey as a {job_title}. Your technical mastery and psychological alignment suggest great potential for success in this realm."
        elif overall_score >= 6:
            recommendation = f"The Oracle sees promise in your path toward {job_title}, though some areas require refinement. With dedication, you may find success in this domain."
        else:
            recommendation = f"The Oracle's vision suggests that the path of {job_title} may not align with your current strengths. Consider exploring other realms that better match your natural abilities."
        
        return {
            "overall_assessment": f"The Oracle has revealed your destiny in the realm of {job_title}. Your overall alignment shows {overall_score:.1f}/10, with technical mastery at {technical_avg:.1f}/10 and psychological readiness at {psychology_avg:.1f}/10.",
            "strengths": [
                "Strong problem-solving abilities" if technical_avg >= 7 else "Willingness to learn and adapt",
                "Good communication skills" if psychology_avg >= 7 else "Positive attitude toward challenges",
                "Professional approach to work" if overall_score >= 6 else "Determination to succeed"
            ],
            "improvements": [
                "Enhance technical skills through practice and training" if technical_avg < 7 else "Continue developing technical expertise",
                "Improve stress management and adaptability" if psychology_avg < 7 else "Strengthen team collaboration skills",
                "Focus on time management and prioritization" if overall_score < 7 else "Build confidence in decision-making"
            ],
            "career_recommendation": recommendation
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
                    # Both trials available
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"🔮 Oracle's Trial for {job['title']}", key=f"start_game_{i}"):
                            st.session_state.current_page = 'game'
                            st.session_state.selected_role_index = i
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🎤 Professional Interview for {job['title']}", key=f"start_interview_{i}"):
                            st.session_state.current_page = 'interview'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                elif game_key in st.session_state and st.session_state[game_key] and (interview_key not in st.session_state or not st.session_state[interview_key]):
                    # Only interview available
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(f"🎤 Professional Interview for {job['title']}", key=f"start_interview_{i}"):
                            st.session_state.current_page = 'interview'
                            st.session_state.selected_role_index = i
                            st.rerun()
                
                elif interview_key in st.session_state and st.session_state[interview_key] and (game_key not in st.session_state or not st.session_state[game_key]):
                    # Only Oracle's trial available
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(f"🔮 Oracle's Trial for {job['title']}", key=f"start_game_{i}"):
                            st.session_state.current_page = 'game'
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

def game_page():
    """Game page for role-playing trials"""
    if st.session_state.selected_role_index is None:
        st.error("No role selected for the trial.")
        if st.button("← Return to Prophecies"):
            st.session_state.current_page = 'main'
            st.rerun()
        return
    
    i = st.session_state.selected_role_index
    job = st.session_state.job_recommendations[i]
    
    # Header with return button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Back to Prophecies"):
            st.session_state.current_page = 'main'
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #495057;">🔮 Oracle's Trial</h1>
            <h2 style="color: #6c757d;">{job['title']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize game state
    game_key = f"game_started_{i}"
    current_q_key = f"current_question_{i}"
    scores_key = f"game_scores_{i}"
    
    if game_key not in st.session_state:
        st.session_state[game_key] = False
    if current_q_key not in st.session_state:
        st.session_state[current_q_key] = 0
    if scores_key not in st.session_state:
        st.session_state[scores_key] = []
    
    # Check if game is completed and show results
    if f'game_completed_{i}' in st.session_state and st.session_state[f'game_completed_{i}']:
        show_game_results_on_game_page(i, job)
        return
    
    # Start game button
    if not st.session_state[game_key]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 3rem; margin: 2rem 0; text-align: center; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin-bottom: 1rem;">🔮 Oracle's Trial Awaits</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem;">
                You are about to embark on a mystical journey through 5 trials that will test your technical mastery and psychological alignment with this role.
            </p>
            <p style="color: rgba(255,255,255,0.8); font-size: 1rem;">
                ⚙️ 3 Technical Trials - Testing your skills and knowledge<br>
                🧠 2 Psychology Trials - Evaluating your work behavior and team dynamics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔮 Begin the Oracle's Trial", key=f"begin_trial_{i}"):
                st.session_state[game_key] = True
                st.session_state[current_q_key] = 0
                st.session_state[scores_key] = []
                st.rerun()
    
    else:
        # Game is in progress
        current_q = st.session_state[current_q_key]
        scores = st.session_state[scores_key]
        
        # Generate questions if not already done
        questions_key = f"questions_{i}"
        if questions_key not in st.session_state:
            with st.spinner("🔮 The Oracle is preparing your trials..."):
                questions_data = generate_role_questions(
                    job['title'],
                    job['description'],
                    st.session_state.personality_type
                )
                st.session_state[questions_key] = questions_data['questions']
        
        questions = st.session_state[questions_key]
        
        # Check if game is complete
        if current_q >= len(questions):
            # Game completed - calculate final results
            final_score = sum(scores) / len(scores)
            technical_scores = [scores[i] for i, q in enumerate(questions) if q.get('type') == 'TECHNICAL']
            psychology_scores = [scores[i] for i, q in enumerate(questions) if q.get('type') == 'PSYCHOLOGY']
            
            technical_avg = sum(technical_scores) / len(technical_scores) if technical_scores else 0
            psychology_avg = sum(psychology_scores) / len(psychology_scores) if psychology_scores else 0
            
            # Generate final assessment
            with st.spinner("🔮 The Oracle is revealing your final destiny..."):
                final_assessment = generate_final_assessment(
                    job['title'],
                    scores,
                    technical_avg,
                    psychology_avg,
                    st.session_state.personality_type
                )
            
            # Store results
            st.session_state[f'game_results_{i}'] = {
                'final_score': final_score,
                'technical_avg': technical_avg,
                'psychology_avg': psychology_avg,
                'final_assessment': final_assessment,
                'scores': scores,
                'questions': questions
            }
            st.session_state[f'game_completed_{i}'] = True
            
            # Show results on the same page
            show_game_results_on_game_page(i, job)
        
        else:
            # Show current question
            question = questions[current_q]
            question_type = question.get('type', 'GENERAL')
            
            # Different styling based on question type
            if question_type == "TECHNICAL":
                bg_color = "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)"
                border_color = "#2196f3"
                icon = "⚙️"
                type_label = "Technical Trial"
            elif question_type == "PSYCHOLOGY":
                bg_color = "linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)"
                border_color = "#9c27b0"
                icon = "🧠"
                type_label = "Psychology Trial"
            else:
                bg_color = "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)"
                border_color = "#6c757d"
                icon = "🔮"
                type_label = "Oracle's Trial"
            
            st.markdown(f"""
            <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                    <h3 style="color: #495057; margin: 0;">{type_label} {current_q + 1} of {len(questions)}</h3>
                </div>
                <p style="font-size: 1.1rem; font-weight: bold; color: #212529; margin-bottom: 1rem;"><strong>{question['question']}</strong></p>
                <p style="color: #6c757d; font-style: italic; background-color: rgba(255,255,255,0.7); padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;">Vision Context: {question['context']}</p>
                <p style="color: #495057; font-size: 0.9rem; background-color: rgba(255,255,255,0.8); padding: 0.5rem; border-radius: 5px;"><strong>Judgment Criteria:</strong> {question['evaluation_criteria']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Multiple choice options
            st.markdown("**🔮 Choose your response:**")
            
            option_labels = [f"{key}: {value}" for key, value in question['options'].items()]
            selected_option = st.radio(
                "Select your answer:",
                option_labels,
                key=f"answer_{i}_{current_q}",
                help="Choose the option that best represents how you would handle this situation"
            )
            
            selected_key = selected_option.split(":")[0] if selected_option else None
            
            # Submit answer button
            if st.button("🔮 Submit to Oracle", key=f"submit_{i}_{current_q}"):
                if selected_key:
                    # Evaluate the answer
                    with st.spinner("🔮 The Oracle is judging your response..."):
                        evaluation = evaluate_answer(
                            question,
                            selected_key,
                            job['title'],
                            st.session_state.personality_type
                        )
                    
                    # Store the score
                    scores.append(evaluation['score'])
                    st.session_state[scores_key] = scores
                    
                    # Show evaluation
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 4px solid #28a745; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(40, 167, 69, 0.2);">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                            <h4 style="color: #155724; margin: 0;">Oracle's Judgment - {type_label}</h4>
                        </div>
                        <p style="font-size: 1.1rem; font-weight: bold; color: #155724; margin-bottom: 0.5rem;"><strong>Destiny Score: {evaluation['score']}/10</strong></p>
                        <p style="color: #155724; margin-bottom: 1rem;"><strong>Oracle's Words:</strong> {evaluation['feedback']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show strengths and improvements
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%); border: 1px solid #bee5eb; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h5 style="color: #0c5460; margin-bottom: 0.5rem;">✨ Oracle's Blessings:</h5>
                        </div>
                        """, unsafe_allow_html=True)
                        for strength in evaluation['strengths']:
                            st.markdown(f"• {strength}")
                    
                    with col2:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 1px solid #ffeaa7; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h5 style="color: #856404; margin-bottom: 0.5rem;">🔮 Path to Enlightenment:</h5>
                        </div>
                        """, unsafe_allow_html=True)
                        for improvement in evaluation['improvements']:
                            st.markdown(f"• {improvement}")
                    
                    # Move to next question
                    st.session_state[current_q_key] = current_q + 1
                    st.rerun()
                else:
                    st.error("The Oracle requires you to select an answer before proceeding.")
            
            # Progress indicator
            progress = (current_q / len(questions)) * 100
            st.progress(progress / 100)
            st.markdown(f"**🔮 Oracle's Progress: {current_q + 1}/{len(questions)} trials completed**")
            
            # Show question type breakdown
            technical_count = sum(1 for q in questions if q.get('type') == 'TECHNICAL')
            psychology_count = sum(1 for q in questions if q.get('type') == 'PSYCHOLOGY')
            st.markdown(f"*⚙️ Technical Trials: {technical_count} | 🧠 Psychology Trials: {psychology_count}*")

def show_game_results_on_game_page(i, job):
    """Display completed game results on the game page"""
    if f'game_results_{i}' not in st.session_state:
        return
    
    results = st.session_state[f'game_results_{i}']
    final_score = results['final_score']
    technical_avg = results['technical_avg']
    psychology_avg = results['psychology_avg']
    final_assessment = results['final_assessment']
    
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">🔮 Oracle's Final Revelation</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Your destiny in the realm of {job['title']} has been revealed...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);">
            <h3 style="color: white; margin-bottom: 0.5rem;">🌟 Overall Destiny</h3>
            <h2 style="color: white; font-size: 2.5rem; margin: 0;">{final_score:.1f}/10</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">{get_score_label(final_score)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);">
            <h3 style="color: white; margin-bottom: 0.5rem;">⚙️ Technical Mastery</h3>
            <h2 style="color: white; font-size: 2.5rem; margin: 0;">{technical_avg:.1f}/10</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">{get_score_label(technical_avg)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);">
            <h3 style="color: white; margin-bottom: 0.5rem;">🧠 Psychological Alignment</h3>
            <h2 style="color: white; font-size: 2.5rem; margin: 0;">{psychology_avg:.1f}/10</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">{get_score_label(psychology_avg)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Oracle's final words
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(240, 147, 251, 0.3);">
        <h3 style="color: white; margin-bottom: 1rem;">🔮 Oracle's Final Words</h3>
        <p style="color: white; font-size: 1.1rem; line-height: 1.6;">{final_assessment['overall_assessment']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">✨ Oracle's Blessings</h4>
        </div>
        """, unsafe_allow_html=True)
        for strength in final_assessment['strengths']:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">🔮 Path to Enlightenment</h4>
        </div>
        """, unsafe_allow_html=True)
        for improvement in final_assessment['improvements']:
            st.markdown(f"• {improvement}")
    
    # Career recommendation
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
        <h4 style="color: white; margin-bottom: 1rem;">🌟 Oracle's Career Verdict</h4>
        <p style="color: white; font-size: 1.1rem; line-height: 1.6;"><strong>{final_assessment['career_recommendation']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔮 Retry Oracle's Trial", key=f"retry_{i}"):
            st.session_state[f'game_completed_{i}'] = False
            st.session_state[f'game_started_{i}'] = False
            st.session_state[f'current_question_{i}'] = 0
            st.session_state[f'game_scores_{i}'] = []
            if f'game_results_{i}' in st.session_state:
                del st.session_state[f'game_results_{i}']
            if f'questions_{i}' in st.session_state:
                del st.session_state[f'questions_{i}']
            st.rerun()
    
    with col2:
        if st.button("🔮 Try Another Role", key=f"try_another_{i}"):
            st.session_state.current_page = 'main'
            st.rerun()
    
    with col3:
        if st.button("🔮 Download Results", key=f"download_{i}"):
            # Create a simple text report
            report = f"""
🔮 CareerOracle - Oracle's Final Revelation
==========================================

Role: {job['title']}
Personality Type: {st.session_state.personality_type}

📊 SCORES:
- Overall Destiny: {final_score:.1f}/10 ({get_score_label(final_score)})
- Technical Mastery: {technical_avg:.1f}/10 ({get_score_label(technical_avg)})
- Psychological Alignment: {psychology_avg:.1f}/10 ({get_score_label(psychology_avg)})

🔮 ORACLE'S FINAL WORDS:
{final_assessment['overall_assessment']}

✨ ORACLE'S BLESSINGS:
{chr(10).join([f"- {strength}" for strength in final_assessment['strengths']])}

🔮 PATH TO ENLIGHTENMENT:
{chr(10).join([f"- {improvement}" for improvement in final_assessment['improvements']])}

🌟 ORACLE'S CAREER VERDICT:
{final_assessment['career_recommendation']}

Generated by CareerOracle - The Mystical Career Advisor
            """
            
            st.download_button(
                label="📄 Download Report",
                data=report,
                file_name=f"career_oracle_report_{job['title'].replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"download_report_{i}"
            )

# Main app logic
def main():
    # Page navigation
    if st.session_state.current_page == 'game':
        game_page()
    elif st.session_state.current_page == 'interview':
        interview.interview_page()
    else:
        main_page()

if __name__ == "__main__":
    main() 