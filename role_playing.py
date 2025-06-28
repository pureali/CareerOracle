import streamlit as st
import openai
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        if st.button("🎤 Try Professional Interview", key=f"try_interview_{i}"):
            st.session_state.current_page = 'interview'
            st.rerun()
    
    with col3:
        if st.button("📄 Download Report", key=f"download_{i}"):
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