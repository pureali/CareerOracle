import streamlit as st
import openai
import os
import json
import time
from dotenv import load_dotenv
import tempfile
import base64
import google_speech

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def text_to_speech(text, voice="alloy"):
    """Convert text to speech using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            response.stream_to_file(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def speech_to_text(audio_file):
    """Convert speech to text using OpenAI Whisper"""
    try:
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        return transcript.text
    except Exception as e:
        st.error(f"Error transcribing speech: {str(e)}")
        return None

def generate_interview_questions(job_title, job_description, personality_type):
    """Generate interview questions based on job and personality"""
    
    prompt = f"""
    Create 2 professional interview questions for the role of {job_title}.
    
    Job Description: {job_description}
    Candidate's Personality Type: {personality_type}
    
    Create exactly:
    1 TECHNICAL question - specific to the skills and knowledge required for this role
    1 BEHAVIORAL question - about work experience, problem-solving, and soft skills
    
    Return as JSON:
    {{
        "questions": [
            {{
                "question": "Question text",
                "type": "TECHNICAL" or "BEHAVIORAL",
                "context": "Brief context or scenario",
                "evaluation_criteria": "What to look for in the answer (1-10 scale)"
            }}
        ]
    }}
    
    Make the questions professional, relevant to the role, and suitable for a formal interview setting.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior HR professional creating interview questions for job candidates."},
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
        # Fallback questions
        return {
            "questions": [
                {
                    "question": "Can you walk us through a challenging technical problem you solved in your previous role?",
                    "type": "TECHNICAL",
                    "context": "We want to understand your technical problem-solving approach.",
                    "evaluation_criteria": "Technical knowledge, problem-solving methodology, communication skills"
                },
                {
                    "question": "Tell us about a time when you had to work with a difficult team member. How did you handle the situation?",
                    "type": "BEHAVIORAL",
                    "context": "We want to assess your interpersonal skills and conflict resolution abilities.",
                    "evaluation_criteria": "Communication, conflict resolution, teamwork, professional maturity"
                }
            ]
        }

def evaluate_interview_answer(question, answer, job_title, personality_type):
    """Evaluate interview answer and provide score with feedback"""
    
    prompt = f"""
    Evaluate this interview answer for a professional setting.
    
    Job Title: {job_title}
    Candidate's Personality Type: {personality_type}
    Question: {question['question']}
    Question Type: {question['type']}
    Evaluation Criteria: {question['evaluation_criteria']}
    Candidate's Answer: {answer}
    
    Provide a score from 1-10 and detailed feedback.
    
    Return as JSON:
    {{
        "score": score,
        "feedback": "Detailed feedback explaining the score",
        "strengths": ["strength1", "strength2"],
        "improvements": ["improvement1", "improvement2"],
        "overall_assessment": "Brief overall assessment"
    }}
    
    Scoring guide:
    1-3: Poor answer, lacks relevant experience/knowledge
    4-6: Average answer, shows some understanding
    7-8: Good answer, demonstrates relevant capabilities
    9-10: Excellent answer, shows strong alignment with role requirements
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior HR professional evaluating interview responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
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
            "improvements": ["Could provide more specific examples"],
            "overall_assessment": "Average response"
        }

def generate_interview_introduction(job_title, job_description):
    """Generate formal interview introduction"""
    
    prompt = f"""
    Create a formal interview introduction for the role of {job_title}.
    
    Job Description: {job_description}
    
    Include:
    1. Welcome message
    2. Introduction of the interview panel
    3. Brief overview of the role
    4. Interview format explanation
    5. Professional closing before questions
    
    Make it formal, welcoming, and professional.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior HR professional conducting a formal job interview."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"""
        Welcome to the formal interview for the position of {job_title}. 
        
        I'm Sarah Johnson, Senior HR Manager, and I'll be conducting this interview today along with our Technical Lead, Michael Chen, and Department Director, Lisa Rodriguez.
        
        We're excited to learn more about your background and how you might fit into our team. This role involves {job_description[:100]}...
        
        Today's interview will consist of 2 questions - one technical and one behavioral. We'll give you time to think and respond, and we encourage you to provide specific examples from your experience.
        
        Are you ready to begin?
        """

def get_score_label(score):
    """Convert numerical score to descriptive label"""
    if score >= 9:
        return "🌟 Outstanding"
    elif score >= 8:
        return "✨ Excellent"
    elif score >= 7:
        return "🎯 Very Good"
    elif score >= 6:
        return "👍 Good"
    elif score >= 5:
        return "⚖️ Satisfactory"
    elif score >= 4:
        return "⚠️ Below Average"
    else:
        return "❌ Needs Improvement"

def interview_page():
    """Main interview page with audio capabilities"""
    
    if st.session_state.selected_role_index is None:
        st.error("No role selected for the interview.")
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
            <h1 style="color: #495057;">🎤 Professional Interview</h1>
            <h2 style="color: #6c757d;">{job['title']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize interview state
    interview_key = f"interview_started_{i}"
    current_q_key = f"interview_question_{i}"
    scores_key = f"interview_scores_{i}"
    
    if interview_key not in st.session_state:
        st.session_state[interview_key] = False
    if current_q_key not in st.session_state:
        st.session_state[current_q_key] = 0
    if scores_key not in st.session_state:
        st.session_state[scores_key] = []
    
    # Check if interview is completed and show results
    if f'interview_completed_{i}' in st.session_state and st.session_state[f'interview_completed_{i}']:
        show_interview_results(i, job)
        return
    
    # Start interview button
    if not st.session_state[interview_key]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 20px; padding: 3rem; margin: 2rem 0; text-align: center; box-shadow: 0 8px 32px rgba(44, 62, 80, 0.3);">
            <h2 style="color: white; margin-bottom: 1rem;">🎤 Professional Interview Session</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem;">
                Welcome to your formal interview. Choose your preferred interview method.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interview method selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 15px; padding: 2rem; margin: 1rem 0; text-align: center; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);">
                <h3 style="color: white; margin-bottom: 1rem;">🎤 Voice Interview</h3>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin-bottom: 1rem;">
                    🔊 AI Spoken Questions - Listen to professional interview questions<br>
                    🎤 Voice Responses - Answer using your microphone<br>
                    📊 AI Evaluation - Get detailed feedback on your responses
                </p>
                <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                    Uses Google Cloud Speech services for high-quality audio processing
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎤 Begin Voice Interview", key=f"begin_voice_interview_{i}"):
                st.session_state[interview_key] = True
                st.session_state[f"interview_mode_{i}"] = "voice"
                st.session_state[current_q_key] = 0
                st.session_state[scores_key] = []
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 15px; padding: 2rem; margin: 1rem 0; text-align: center; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);">
                <h3 style="color: white; margin-bottom: 1rem;">📝 Text Interview</h3>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin-bottom: 1rem;">
                    🔊 AI Spoken Questions - Listen to professional interview questions<br>
                    ⌨️ Text Responses - Type your answers<br>
                    📊 AI Evaluation - Get detailed feedback on your responses
                </p>
                <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                    Traditional text-based interview with audio questions
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 Begin Text Interview", key=f"begin_text_interview_{i}"):
                st.session_state[interview_key] = True
                st.session_state[f"interview_mode_{i}"] = "text"
                st.session_state[current_q_key] = 0
                st.session_state[scores_key] = []
                st.rerun()
    
    else:
        # Interview is in progress
        current_q = st.session_state[current_q_key]
        scores = st.session_state[scores_key]
        
        # Generate interview introduction if not already done
        intro_key = f"interview_intro_{i}"
        if intro_key not in st.session_state:
            with st.spinner("🎤 Preparing interview introduction..."):
                introduction = generate_interview_introduction(
                    job['title'],
                    job['description']
                )
                st.session_state[intro_key] = introduction
        
        # Generate questions if not already done
        questions_key = f"interview_questions_{i}"
        if questions_key not in st.session_state:
            with st.spinner("🎤 Preparing interview questions..."):
                questions_data = generate_interview_questions(
                    job['title'],
                    job['description'],
                    st.session_state.personality_type
                )
                st.session_state[questions_key] = questions_data['questions']
        
        questions = st.session_state[questions_key]
        
        # Check if interview is complete
        if current_q >= len(questions):
            # Interview completed - calculate final results
            final_score = sum(scores) / len(scores)
            
            # Generate final assessment
            with st.spinner("🎤 Generating final assessment..."):
                final_assessment = generate_interview_final_assessment(
                    job['title'],
                    scores,
                    st.session_state.personality_type
                )
            
            # Store results
            st.session_state[f'interview_results_{i}'] = {
                'final_score': final_score,
                'final_assessment': final_assessment,
                'scores': scores,
                'questions': questions
            }
            st.session_state[f'interview_completed_{i}'] = True
            
            # Show results
            show_interview_results(i, job)
        
        else:
            # Show current question
            question = questions[current_q]
            question_type = question.get('type', 'GENERAL')
            
            # Check interview mode
            interview_mode = st.session_state.get(f"interview_mode_{i}", "text")
            
            # Show introduction for first question
            if current_q == 0:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h3 style="color: #1565c0; margin-bottom: 1rem;">🎤 Interview Introduction</h3>
                    <p style="color: #1976d2; line-height: 1.6;">{}</p>
                </div>
                """.format(st.session_state[intro_key]), unsafe_allow_html=True)
            
            # Question styling
            if question_type == "TECHNICAL":
                bg_color = "linear-gradient(135deg, #3498db 0%, #2980b9 100%)"
                border_color = "#2980b9"
                icon = "⚙️"
                type_label = "Technical Question"
            elif question_type == "BEHAVIORAL":
                bg_color = "linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)"
                border_color = "#8e44ad"
                icon = "🧠"
                type_label = "Behavioral Question"
            else:
                bg_color = "linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%)"
                border_color = "#7f8c8d"
                icon = "🎤"
                type_label = "Interview Question"
            
            st.markdown(f"""
            <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                    <h3 style="color: white; margin: 0;">{type_label} {current_q + 1} of {len(questions)}</h3>
                </div>
                <p style="font-size: 1.1rem; font-weight: bold; color: white; margin-bottom: 1rem;"><strong>{question['question']}</strong></p>
                <p style="color: rgba(255,255,255,0.8); font-style: italic; background-color: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;">{question['context']}</p>
                <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; background-color: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 5px;"><strong>Evaluation Criteria:</strong> {question['evaluation_criteria']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Handle different interview modes
            if interview_mode == "voice":
                # Voice interview mode using Google Speech
                st.markdown("### 🎤 Voice Interview Mode")
                
                # Speak the question using Google Speech
                google_speech.speak_question(question['question'], current_q + 1)
                
                # Get voice answer using Google Speech
                st.markdown("### 🎤 Record Your Answer")
                voice_answer = google_speech.get_voice_answer()
                
                if voice_answer:
                    st.success("✅ Voice answer recorded and transcribed!")
                    st.text_area("Transcribed Answer:", voice_answer, height=100)
                    
                    # Submit voice answer
                    if st.button("📤 Submit Voice Answer", key=f"submit_voice_{i}_{current_q}"):
                        submit_answer(question, voice_answer, i, current_q, scores, scores_key, job, icon, type_label)
                
            else:
                # Text interview mode (existing logic)
                # Audio section
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔊 Listen to the question:**")
                    
                    # Generate and play audio for the question
                    audio_key = f"question_audio_{i}_{current_q}"
                    if audio_key not in st.session_state:
                        with st.spinner("🎤 Generating audio..."):
                            audio_file = text_to_speech(question['question'], voice="alloy")
                            if audio_file:
                                st.session_state[audio_key] = audio_file
                    
                    if audio_key in st.session_state and st.session_state[audio_key]:
                        with open(st.session_state[audio_key], "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/mp3")
                            
                            # Play button
                            if st.button("🔊 Play Question", key=f"play_{i}_{current_q}"):
                                st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.error("Unable to generate audio for this question.")
                
                with col2:
                    st.markdown("**🎤 Record your voice answer:**")
                    
                    # Option 1: File uploader for audio response
                    st.markdown("**Option 1: Upload recorded audio file**")
                    uploaded_audio = st.file_uploader(
                        "Upload your recorded answer (MP3, WAV, M4A)",
                        type=['mp3', 'wav', 'm4a'],
                        key=f"audio_upload_{i}_{current_q}"
                    )
                    
                    if uploaded_audio:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_audio.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Transcribe the audio
                        with st.spinner("🎤 Transcribing your answer..."):
                            transcribed_text = speech_to_text(tmp_file_path)
                        
                        if transcribed_text:
                            st.success("✅ Audio transcribed successfully!")
                            st.text_area("Transcribed Answer:", transcribed_text, height=100)
                            
                            # Submit transcribed answer
                            if st.button("📤 Submit Transcribed Answer", key=f"submit_transcribed_{i}_{current_q}"):
                                submit_answer(question, transcribed_text, i, current_q, scores, scores_key, job, icon, type_label)
                        else:
                            st.error("❌ Failed to transcribe audio. Please try again.")
                        
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
                    
                    # Option 2: Text input as fallback
                    st.markdown("**Option 2: Type your answer**")
                    user_answer = st.text_area(
                        "Type your answer here:",
                        height=150,
                        key=f"text_answer_{i}_{current_q}"
                    )
                    
                    if user_answer:
                        if st.button("📤 Submit Text Answer", key=f"submit_text_{i}_{current_q}"):
                            submit_answer(question, user_answer, i, current_q, scores, scores_key, job, icon, type_label)
            
            # Text response section (fallback)
            st.markdown("---")
            st.markdown("**✍️ Or type your answer (alternative):**")
            
            # Text area for response
            user_answer = st.text_area(
                "Provide a detailed answer to the question above:",
                height=150,
                key=f"answer_{i}_{current_q}",
                help="Be specific, provide examples, and demonstrate your knowledge and experience"
            )
            
            # Submit answer button
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("🎤 Submit Voice Answer", key=f"submit_voice_{i}_{current_q}"):
                    transcribed_key = f"transcribed_{i}_{current_q}"
                    if transcribed_key in st.session_state and st.session_state[transcribed_key]:
                        answer_to_evaluate = st.session_state[transcribed_key]
                        submit_answer(question, answer_to_evaluate, i, current_q, scores, scores_key, job, icon, type_label)
                    else:
                        st.error("Please record and transcribe your answer first.")
            
            with col2:
                if st.button("✍️ Submit Text Answer", key=f"submit_text_{i}_{current_q}"):
                    if user_answer.strip():
                        submit_answer(question, user_answer, i, current_q, scores, scores_key, job, icon, type_label)
                    else:
                        st.error("Please provide a text answer.")
            
            with col3:
                if st.button("🔄 Skip Question", key=f"skip_{i}_{current_q}"):
                    st.session_state[current_q_key] = current_q + 1
                    st.rerun()
            
            # Progress indicator
            progress = (current_q / len(questions)) * 100
            st.progress(progress / 100)
            st.markdown(f"**🎤 Interview Progress: {current_q + 1}/{len(questions)} questions completed**")

def submit_answer(question, answer, i, current_q, scores, scores_key, job, icon, type_label):
    """Helper function to submit and evaluate answers"""
    # Evaluate the answer
    with st.spinner("🎤 Evaluating your response..."):
        evaluation = evaluate_interview_answer(
            question,
            answer,
            job['title'],
            st.session_state.personality_type
        )
    
    # Store the score
    scores.append(evaluation['score'])
    st.session_state[scores_key] = scores
    
    # Show evaluation
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-left: 4px solid #27ae60; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(39, 174, 96, 0.2);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <h4 style="color: white; margin: 0;">Interview Evaluation - {type_label}</h4>
        </div>
        <p style="font-size: 1.1rem; font-weight: bold; color: white; margin-bottom: 0.5rem;"><strong>Score: {evaluation['score']}/10</strong></p>
        <p style="color: white; margin-bottom: 1rem;"><strong>Feedback:</strong> {evaluation['feedback']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show strengths and improvements
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border: 1px solid #2980b9; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h5 style="color: white; margin-bottom: 0.5rem;">✨ Strengths:</h5>
        </div>
        """, unsafe_allow_html=True)
        for strength in evaluation['strengths']:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); border: 1px solid #c0392b; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h5 style="color: white; margin-bottom: 0.5rem;">🔧 Areas for Improvement:</h5>
        </div>
        """, unsafe_allow_html=True)
        for improvement in evaluation['improvements']:
            st.markdown(f"• {improvement}")
    
    # Move to next question
    st.session_state[f'interview_question_{i}'] = current_q + 1
    st.rerun()

def generate_interview_final_assessment(job_title, scores, personality_type):
    """Generate comprehensive final interview assessment"""
    
    overall_score = sum(scores) / len(scores)
    
    prompt = f"""
    Create a comprehensive final interview assessment for a candidate who completed a professional interview for: {job_title}
    
    Overall Score: {overall_score:.1f}/10
    Individual Scores: {scores}
    Personality Type: {personality_type}
    
    Provide a professional assessment including:
    1. Overall assessment (2-3 sentences)
    2. 3-4 key strengths demonstrated
    3. 3-4 areas for improvement
    4. Hiring recommendation (Strong Yes/Yes/Maybe/No)
    
    Return as JSON:
    {{
        "overall_assessment": "Professional assessment of the candidate's interview performance",
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "improvements": ["improvement 1", "improvement 2", "improvement 3"],
        "hiring_recommendation": "Strong Yes/Yes/Maybe/No with brief reasoning"
    }}
    
    Make the assessment professional and suitable for a real hiring decision.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior HR professional providing final interview assessments."},
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
            recommendation = "Strong Yes - Excellent interview performance with strong technical and behavioral competencies."
        elif overall_score >= 6:
            recommendation = "Yes - Good interview performance with room for growth."
        elif overall_score >= 4:
            recommendation = "Maybe - Average performance, consider additional evaluation."
        else:
            recommendation = "No - Below average performance, not recommended for this role."
        
        return {
            "overall_assessment": f"The candidate demonstrated an overall interview performance of {overall_score:.1f}/10, showing {get_score_label(overall_score).lower()} capabilities.",
            "strengths": [
                "Professional communication skills" if overall_score >= 6 else "Willingness to participate",
                "Technical knowledge" if overall_score >= 7 else "Basic understanding of role requirements",
                "Problem-solving approach" if overall_score >= 6 else "Attempted to provide examples"
            ],
            "improvements": [
                "Enhance technical depth and specific examples" if overall_score < 7 else "Continue developing technical expertise",
                "Improve communication clarity and structure" if overall_score < 6 else "Strengthen presentation skills",
                "Provide more detailed behavioral examples" if overall_score < 6 else "Build confidence in responses"
            ],
            "hiring_recommendation": recommendation
        }

def show_interview_results(i, job):
    """Display completed interview results"""
    if f'interview_results_{i}' not in st.session_state:
        return
    
    results = st.session_state[f'interview_results_{i}']
    final_score = results['final_score']
    final_assessment = results['final_assessment']
    
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 8px 32px rgba(44, 62, 80, 0.3);">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">🎤 Interview Results</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Your professional interview assessment for {job['title']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Overall score
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); border-radius: 15px; padding: 2rem; text-align: center; margin: 2rem 0; box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);">
        <h3 style="color: white; margin-bottom: 0.5rem;">🎤 Overall Interview Score</h3>
        <h2 style="color: white; font-size: 3rem; margin: 0;">{final_score:.1f}/10</h2>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0;">{get_score_label(final_score)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Final assessment
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(52, 152, 219, 0.3);">
        <h3 style="color: white; margin-bottom: 1rem;">📋 Professional Assessment</h3>
        <p style="color: white; font-size: 1.1rem; line-height: 1.6;">{final_assessment['overall_assessment']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed feedback
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">✨ Key Strengths</h4>
        </div>
        """, unsafe_allow_html=True)
        for strength in final_assessment['strengths']:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">🎯 Areas for Improvement</h4>
        </div>
        """, unsafe_allow_html=True)
        for improvement in final_assessment['improvements']:
            st.markdown(f"• {improvement}")
    
    # Hiring recommendation
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 15px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);">
        <h4 style="color: white; margin-bottom: 1rem;">🎯 Hiring Recommendation</h4>
        <p style="color: white; font-size: 1.1rem; line-height: 1.6;"><strong>{final_assessment['hiring_recommendation']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎤 Retry Interview", key=f"retry_interview_{i}"):
            st.session_state[f'interview_completed_{i}'] = False
            st.session_state[f'interview_started_{i}'] = False
            st.session_state[f'interview_question_{i}'] = 0
            st.session_state[f'interview_scores_{i}'] = []
            if f'interview_results_{i}' in st.session_state:
                del st.session_state[f'interview_results_{i}']
            if f'interview_questions_{i}' in st.session_state:
                del st.session_state[f'interview_questions_{i}']
            if f'interview_intro_{i}' in st.session_state:
                del st.session_state[f'interview_intro_{i}']
            st.rerun()
    
    with col2:
        if st.button("🔮 Try Oracle's Trial", key=f"try_oracle_{i}"):
            st.session_state.current_page = 'game'
            st.rerun()
    
    with col3:
        if st.button("📄 Download Report", key=f"download_interview_{i}"):
            # Create interview report
            report = f"""
🎤 CareerOracle - Professional Interview Report
===============================================

Role: {job['title']}
Personality Type: {st.session_state.personality_type}

📊 INTERVIEW SCORES:
- Overall Score: {final_score:.1f}/10 ({get_score_label(final_score)})
- Individual Scores: {', '.join([f'{score:.1f}' for score in results['scores']])}

📋 PROFESSIONAL ASSESSMENT:
{final_assessment['overall_assessment']}

✨ KEY STRENGTHS:
{chr(10).join([f"- {strength}" for strength in final_assessment['strengths']])}

🎯 AREAS FOR IMPROVEMENT:
{chr(10).join([f"- {improvement}" for improvement in final_assessment['improvements']])}

🎯 HIRING RECOMMENDATION:
{final_assessment['hiring_recommendation']}

Generated by CareerOracle - Professional Interview System
            """
            
            st.download_button(
                label="📄 Download Interview Report",
                data=report,
                file_name=f"interview_report_{job['title'].replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"download_interview_report_{i}"
            ) 