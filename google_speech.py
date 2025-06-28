import streamlit as st
import os
import tempfile
import base64
import openai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def text_to_speech(text, voice_name="en-US-Standard-A", language_code="en-US"):
    """
    Convert text to speech using OpenAI TTS (fallback since Google Cloud requires credentials)
    Returns base64 encoded audio data
    """
    try:
        # Use OpenAI TTS as fallback
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save to temporary file and convert to base64
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            response.stream_to_file(tmp_file.name)
            
            # Read the file and convert to base64
            with open(tmp_file.name, "rb") as audio_file:
                audio_content = audio_file.read()
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            return audio_base64
        
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def speech_to_text(audio_data, language_code="en-US"):
    """
    Convert speech to text using OpenAI Whisper (fallback since Google Cloud requires credentials)
    audio_data should be base64 encoded audio
    """
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # Use OpenAI Whisper for transcription
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return transcript.text
        
    except Exception as e:
        st.error(f"Speech-to-text error: {str(e)}")
        return None

def create_audio_player(audio_base64, text="Listen to question"):
    """
    Create an HTML audio player for the base64 encoded audio
    """
    if audio_base64:
        audio_html = f"""
        <audio controls style="width: 100%; margin: 10px 0;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        st.markdown(f"**{text}**")

def create_audio_recorder():
    """
    Create a simple audio recorder using HTML5 and JavaScript
    Returns the recorded audio as base64
    """
    audio_recorder_html = """
    <div style="margin: 20px 0;">
        <button id="startRecording" onclick="startRecording()" style="background: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">
            🎤 Start Recording
        </button>
        <button id="stopRecording" onclick="stopRecording()" style="background: #4b4b4b; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px; display: none;">
            ⏹️ Stop Recording
        </button>
        <div id="recordingStatus" style="margin: 10px 0; font-weight: bold; color: #ff4b4b;"></div>
        <audio id="recordedAudio" controls style="width: 100%; margin: 10px 0; display: none;"></audio>
    </div>
    
    <script>
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = document.getElementById('recordedAudio');
                audio.src = audioUrl;
                audio.style.display = 'block';
                
                // Convert to base64 and send to Streamlit
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64Audio = reader.result.split(',')[1];
                    // Store in session storage for Streamlit to access
                    sessionStorage.setItem('recordedAudioData', base64Audio);
                };
                reader.readAsDataURL(audioBlob);
            };
            
            mediaRecorder.start();
            isRecording = true;
            
            document.getElementById('startRecording').style.display = 'none';
            document.getElementById('stopRecording').style.display = 'inline-block';
            document.getElementById('recordingStatus').textContent = '🔴 Recording... Speak now!';
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            document.getElementById('recordingStatus').textContent = '❌ Error: Could not access microphone';
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            
            document.getElementById('startRecording').style.display = 'inline-block';
            document.getElementById('stopRecording').style.display = 'none';
            document.getElementById('recordingStatus').textContent = '✅ Recording complete!';
            
            // Stop all tracks
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }
    </script>
    """
    
    st.markdown(audio_recorder_html, unsafe_allow_html=True)
    
    # Add a button to process the recorded audio
    if st.button("🎵 Process Recorded Answer"):
        # For now, we'll use a simple text input as fallback
        st.info("🎤 Voice recording feature is being set up. Please use the text input below for now.")
        return None
    
    return None

def speak_question(question_text, question_number):
    """
    Speak the question using text-to-speech and display it
    """
    st.markdown(f"### Question {question_number}")
    st.markdown(f"**{question_text}**")
    
    # Convert question to speech
    audio_base64 = text_to_speech(question_text)
    
    if audio_base64:
        create_audio_player(audio_base64, "🎧 Listen to the question:")
        st.markdown("---")
    else:
        st.warning("⚠️ Could not generate speech for this question.")

def get_voice_answer():
    """
    Get voice answer from user using microphone
    """
    st.markdown("### 🎤 Record Your Answer")
    st.markdown("Click 'Start Recording' and speak your answer clearly.")
    
    # Create the audio recorder
    transcribed_text = create_audio_recorder()
    
    # For now, provide a text input as fallback
    st.markdown("### 📝 Or type your answer:")
    text_answer = st.text_area("Type your answer here:", height=100)
    
    if text_answer:
        return text_answer
    
    return transcribed_text

def process_voice_interview(questions, job_title, personality_type):
    """
    Process a complete voice-based interview
    """
    answers = []
    
    for i, question in enumerate(questions, 1):
        st.markdown(f"## Question {i} of {len(questions)}")
        
        # Speak the question
        speak_question(question, i)
        
        # Get voice answer
        st.markdown("### Your Answer:")
        answer = get_voice_answer()
        
        if answer:
            answers.append({
                "question": question,
                "answer": answer,
                "question_number": i
            })
            st.success(f"✅ Answer {i} recorded!")
        else:
            st.warning(f"⚠️ No answer recorded for question {i}")
        
        st.markdown("---")
    
    return answers

def evaluate_voice_interview(answers, job_title, personality_type):
    """
    Evaluate the voice interview answers
    """
    if not answers:
        return None
    
    # Prepare the evaluation prompt
    answers_text = "\n\n".join([
        f"Question {ans['question_number']}: {ans['question']}\nAnswer: {ans['answer']}"
        for ans in answers
    ])
    
    prompt = f"""
    Evaluate the following interview answers for a {job_title} position.
    
    Candidate's Personality Type: {personality_type}
    
    Interview Answers:
    {answers_text}
    
    Please provide a comprehensive evaluation including:
    1. Overall Score (1-10)
    2. Communication Skills Assessment
    3. Technical Knowledge (if applicable)
    4. Problem-Solving Abilities
    5. Cultural Fit
    6. Strengths
    7. Areas for Improvement
    8. Specific Recommendations
    
    Return as JSON:
    {{
        "overall_score": score,
        "communication_skills": "assessment",
        "technical_knowledge": "assessment",
        "problem_solving": "assessment",
        "cultural_fit": "assessment",
        "strengths": ["strength1", "strength2", "strength3"],
        "areas_for_improvement": ["area1", "area2", "area3"],
        "recommendations": ["rec1", "rec2", "rec3"],
        "detailed_feedback": "comprehensive feedback"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert interview evaluator specializing in voice-based interviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
        
    except Exception as e:
        st.error(f"Error evaluating interview: {str(e)}")
        return None 