import streamlit as st
import openai
import os
import json
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_immersive_scenario(job_title, job_description, personality_type, scenario_type="office"):
    """Generate an immersive scenario for the role-playing experience"""
    
    scenarios = {
        "office": [
            "You arrive at your new office on your first day as a {role}. The building is modern, with glass walls and open spaces. Your desk is set up with a powerful computer and multiple monitors. As you settle in, you notice your team members are already deep in their work.",
            "The office is buzzing with activity. You can hear the sound of keyboards clicking, phones ringing, and people discussing projects. The air is filled with the energy of a productive workplace.",
            "Your workspace is organized and professional. You have access to all the tools and resources you need to excel in your role. The environment feels both challenging and supportive."
        ],
        "meeting": [
            "You're sitting in a conference room with your team. The table is covered with laptops, documents, and coffee cups. The atmosphere is focused but collaborative.",
            "The meeting room has a large screen displaying project timelines and metrics. Your colleagues are engaged in discussing the current challenges and opportunities.",
            "You can feel the collective energy of the team as they work together to solve problems and make decisions. The room is filled with the sound of ideas being shared and debated."
        ],
        "crisis": [
            "Suddenly, an urgent situation arises. The office atmosphere changes from routine to high-stakes. Everyone's attention is focused on resolving the crisis quickly and effectively.",
            "The normal office routine is interrupted by an unexpected challenge. You can see the team springing into action, each person taking on their role in the response.",
            "Time seems to slow down as the crisis unfolds. You need to think quickly and act decisively while coordinating with your team members."
        ],
        "collaboration": [
            "You're working closely with a colleague on a complex project. The two of you are brainstorming solutions and sharing ideas. The collaboration feels productive and energizing.",
            "The workspace is set up for teamwork, with whiteboards covered in diagrams and sticky notes. You and your teammate are deeply engaged in solving a challenging problem together.",
            "You can feel the synergy of working with someone who complements your skills. The collaboration is bringing out the best in both of you."
        ]
    }
    
    base_scenario = random.choice(scenarios.get(scenario_type, scenarios["office"]))
    
    prompt = f"""
    Create an immersive, first-person scenario for someone experiencing their first day as a {job_title}.
    
    Job Description: {job_description}
    Personality Type: {personality_type}
    Base Scenario: {base_scenario}
    
    Write this as if the user is actually experiencing this moment. Use sensory details, emotions, and immediate thoughts. Make it feel like they are truly in this role and situation.
    
    Include:
    - What they see, hear, and feel
    - Their immediate thoughts and reactions
    - The atmosphere and energy of the environment
    - Specific details about their role and responsibilities
    - The people around them and their interactions
    
    Write in present tense, as if it's happening right now. Make it engaging and realistic.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an immersive storytelling expert creating realistic, engaging workplace scenarios."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"You step into your new role as a {job_title}. The office environment is professional yet welcoming. You can feel the energy of a productive workplace around you. Your desk is set up with all the tools you need, and your colleagues are already engaged in their work. You take a moment to absorb the atmosphere and prepare for the challenges ahead."

def generate_interactive_choice(job_title, current_scenario, choice_type, personality_type):
    """Generate interactive choices for the role-playing experience"""
    
    choice_types = {
        "approach": [
            "How do you want to approach this situation?",
            "What's your first move in this scenario?",
            "How do you plan to handle this challenge?",
            "What's your strategy for this moment?"
        ],
        "interaction": [
            "How do you interact with your colleagues?",
            "What do you say to your team members?",
            "How do you communicate your thoughts?",
            "What's your approach to teamwork?"
        ],
        "problem_solving": [
            "How do you solve this technical challenge?",
            "What's your approach to this problem?",
            "How do you troubleshoot this issue?",
            "What's your methodology for this task?"
        ],
        "decision": [
            "What decision do you make?",
            "How do you choose to proceed?",
            "What's your call in this situation?",
            "How do you prioritize your actions?"
        ]
    }
    
    question = random.choice(choice_types.get(choice_type, choice_types["approach"]))
    
    prompt = f"""
    Create 4 different choices for a {job_title} in this scenario:
    
    Current Situation: {current_scenario}
    Question: {question}
    Personality Type: {personality_type}
    
    Generate 4 realistic options (A, B, C, D) that represent different approaches, styles, or strategies. Each choice should be:
    - Realistic for someone in this role
    - Different from the others (not just slight variations)
    - Appropriate for the situation
    - Reflective of different work styles or personality approaches
    
    Return as JSON:
    {{
        "question": "{question}",
        "choices": {{
            "A": "First choice description",
            "B": "Second choice description", 
            "C": "Third choice description",
            "D": "Fourth choice description"
        }},
        "context": "Brief explanation of what each choice represents"
    }}
    
    Make the choices engaging and meaningful, representing different approaches to the situation.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are creating interactive choices for an immersive role-playing experience."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        # Fallback choices
        return {
            "question": question,
            "choices": {
                "A": "Take a methodical, analytical approach",
                "B": "Collaborate with team members for input",
                "C": "Trust your instincts and act quickly",
                "D": "Research and gather more information first"
            },
            "context": "Different approaches to handling the situation"
        }

def generate_scenario_outcome(job_title, scenario, choice, personality_type):
    """Generate the outcome and consequences of the user's choice"""
    
    prompt = f"""
    Describe what happens next after the {job_title} makes this choice:
    
    Scenario: {scenario}
    Choice Made: {choice}
    Personality Type: {personality_type}
    
    Write this as an immersive, first-person experience showing:
    - The immediate consequences of their choice
    - How their colleagues react
    - What happens in the environment
    - The results of their decision
    - Any new challenges or opportunities that arise
    
    Make it feel like they are experiencing the outcome in real-time. Include sensory details and emotional responses.
    Write in present tense, as if it's happening right now.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are describing the immediate consequences of a workplace decision in an immersive way."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Your choice leads to immediate results. Your colleagues notice your approach and respond accordingly. The situation evolves based on your decision, presenting new opportunities and challenges."

def evaluate_choice_effectiveness(job_title, scenario, choice, outcome, personality_type):
    """Evaluate how effective the user's choice was in the given scenario"""
    
    prompt = f"""
    Evaluate the effectiveness of this choice in the context of a {job_title} role:
    
    Scenario: {scenario}
    Choice Made: {choice}
    Outcome: {outcome}
    Personality Type: {personality_type}
    
    Rate the choice on a scale of 1-10 and provide:
    1. Effectiveness score (1-10)
    2. Brief explanation of why this score
    3. What worked well about this approach
    4. What could have been improved
    5. How it aligns with the role requirements
    
    Return as JSON:
    {{
        "score": score,
        "explanation": "Why this score was given",
        "strengths": ["strength1", "strength2"],
        "improvements": ["improvement1", "improvement2"],
        "role_alignment": "How well this choice fits the role"
    }}
    
    Be objective but constructive in your evaluation.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are evaluating workplace decisions objectively and constructively."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        return {
            "score": 7,
            "explanation": "The choice shows good judgment for the role",
            "strengths": ["Demonstrates appropriate approach", "Shows role understanding"],
            "improvements": ["Could be more specific", "Consider alternative perspectives"],
            "role_alignment": "Generally aligns well with role requirements"
        }

def generate_role_specific_puzzle(job_title, job_description, puzzle_type):
    """Generate role-specific puzzles or challenges"""
    
    puzzle_types = {
        "technical": [
            "Debug a complex system issue",
            "Optimize a process or workflow",
            "Design a solution to a technical problem",
            "Troubleshoot a critical error"
        ],
        "communication": [
            "Present a complex idea to stakeholders",
            "Resolve a team conflict",
            "Explain technical concepts to non-technical people",
            "Negotiate with clients or vendors"
        ],
        "leadership": [
            "Make a difficult decision with limited information",
            "Motivate a team during a challenging period",
            "Delegate tasks effectively",
            "Handle a crisis situation"
        ],
        "problem_solving": [
            "Analyze data to find insights",
            "Create a strategy for a complex project",
            "Identify root causes of problems",
            "Develop innovative solutions"
        ]
    }
    
    puzzle_description = random.choice(puzzle_types.get(puzzle_type, puzzle_types["problem_solving"]))
    
    prompt = f"""
    Create a realistic, role-specific puzzle for a {job_title}:
    
    Job Description: {job_description}
    Puzzle Type: {puzzle_description}
    
    Create a detailed scenario that:
    1. Presents a realistic challenge someone in this role would face
    2. Provides enough context and information to work with
    3. Requires critical thinking and role-specific skills
    4. Has multiple possible approaches or solutions
    5. Feels like a real workplace situation
    
    Include:
    - The specific problem or challenge
    - Relevant background information
    - Available resources and constraints
    - What success looks like
    - Potential obstacles or complications
    
    Make it engaging and challenging but solvable.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are creating realistic workplace challenges and puzzles for role-specific training."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"As a {job_title}, you encounter a challenging situation that requires your expertise. The problem involves {puzzle_description.lower()}. You need to analyze the situation, consider your options, and implement the best solution using your skills and knowledge."

def generate_final_role_assessment(job_title, all_choices, all_scores, personality_type):
    """Generate a comprehensive assessment of the user's performance in the role"""
    
    if not all_scores:
        return {
            "overall_score": 0,
            "role_fit": "Unable to assess",
            "strengths": ["No data available"],
            "improvements": ["Complete more scenarios"],
            "career_recommendation": "Continue exploring the role"
        }
    
    avg_score = sum(all_scores) / len(all_scores)
    
    prompt = f"""
    Provide a comprehensive assessment of someone's performance in a {job_title} role:
    
    Average Performance Score: {avg_score:.1f}/10
    Number of Scenarios Completed: {len(all_choices)}
    Personality Type: {personality_type}
    
    Based on their choices and performance, provide:
    1. Overall assessment of their role fit
    2. Key strengths they demonstrated
    3. Areas for improvement
    4. Career recommendation
    
    Return as JSON:
    {{
        "overall_score": {avg_score:.1f},
        "role_fit": "Excellent/Good/Fair/Poor fit for the role",
        "strengths": ["strength1", "strength2", "strength3"],
        "improvements": ["improvement1", "improvement2", "improvement3"],
        "career_recommendation": "Specific recommendation for this person"
    }}
    
    Be constructive and specific in your assessment.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are providing a comprehensive career assessment based on role-playing performance."},
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
            "overall_score": avg_score,
            "role_fit": "Good" if avg_score >= 7 else "Fair" if avg_score >= 5 else "Poor",
            "strengths": ["Shows potential for the role", "Demonstrates learning ability"],
            "improvements": ["Continue developing skills", "Gain more experience"],
            "career_recommendation": "Consider pursuing this role with additional training"
        }

def game_page():
    """Immersive role-playing game page"""
    if st.session_state.selected_role_index is None:
        st.error("No role selected for the immersive experience.")
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
            <h1 style="color: #495057;">🎭 Immersive Experience</h1>
            <h2 style="color: #6c757d;">{job['title']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize game state
    game_key = f"immersive_started_{i}"
    current_scenario_key = f"current_scenario_{i}"
    scenarios_completed_key = f"scenarios_completed_{i}"
    scores_key = f"immersive_scores_{i}"
    choices_key = f"immersive_choices_{i}"
    
    if game_key not in st.session_state:
        st.session_state[game_key] = False
    if current_scenario_key not in st.session_state:
        st.session_state[current_scenario_key] = 0
    if scenarios_completed_key not in st.session_state:
        st.session_state[scenarios_completed_key] = []
    if scores_key not in st.session_state:
        st.session_state[scores_key] = []
    if choices_key not in st.session_state:
        st.session_state[choices_key] = []
    
    # Check if game is completed and show results
    if f'immersive_completed_{i}' in st.session_state and st.session_state[f'immersive_completed_{i}']:
        show_immersive_results(i, job)
        return
    
    # Start game button
    if not st.session_state[game_key]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 3rem; margin: 2rem 0; text-align: center; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin-bottom: 1rem;">🎭 Step Into Your Role</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem;">
                You are about to experience what it's really like to be a {job['title']}. 
                You'll face realistic challenges, make important decisions, and solve role-specific puzzles.
            </p>
            <p style="color: rgba(255,255,255,0.8); font-size: 1rem;">
                🏢 Office Scenarios - Experience daily work situations<br>
                🧩 Role Puzzles - Solve challenges specific to your role<br>
                🤝 Team Interactions - Navigate workplace relationships<br>
                ⚡ Crisis Management - Handle unexpected situations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎭 Begin Immersive Experience", key=f"begin_immersive_{i}"):
                st.session_state[game_key] = True
                st.session_state[current_scenario_key] = 0
                st.session_state[scenarios_completed_key] = []
                st.session_state[scores_key] = []
                st.session_state[choices_key] = []
                st.rerun()
    
    else:
        # Game is in progress
        current_scenario = st.session_state[current_scenario_key]
        scenarios_completed = st.session_state[scenarios_completed_key]
        scores = st.session_state[scores_key]
        choices = st.session_state[choices_key]
        
        # Define scenario types and their order
        scenario_types = [
            ("office", "Your First Day"),
            ("meeting", "Team Collaboration"),
            ("crisis", "Crisis Management"),
            ("collaboration", "Project Challenge"),
            ("puzzle", "Role-Specific Puzzle")
        ]
        
        # Check if all scenarios are completed
        if current_scenario >= len(scenario_types):
            # Game completed - generate final assessment
            with st.spinner("🎭 Analyzing your performance..."):
                final_assessment = generate_final_role_assessment(
                    job['title'],
                    choices,
                    scores,
                    st.session_state.personality_type
                )
            
            # Store results
            st.session_state[f'immersive_results_{i}'] = {
                'final_score': final_assessment['overall_score'],
                'role_fit': final_assessment['role_fit'],
                'strengths': final_assessment['strengths'],
                'improvements': final_assessment['improvements'],
                'career_recommendation': final_assessment['career_recommendation'],
                'scores': scores,
                'choices': choices,
                'scenarios_completed': scenarios_completed
            }
            st.session_state[f'immersive_completed_{i}'] = True
            
            # Show results
            show_immersive_results(i, job)
        
        else:
            # Show current scenario
            scenario_type, scenario_title = scenario_types[current_scenario]
            
            # Generate scenario if not already done
            scenario_key = f"scenario_{i}_{current_scenario}"
            if scenario_key not in st.session_state:
                with st.spinner("🎭 Creating your immersive scenario..."):
                    if scenario_type == "puzzle":
                        scenario_text = generate_role_specific_puzzle(
                            job['title'],
                            job['description'],
                            "technical"
                        )
                    else:
                        scenario_text = generate_immersive_scenario(
                            job['title'],
                            job['description'],
                            st.session_state.personality_type,
                            scenario_type
                        )
                    st.session_state[scenario_key] = scenario_text
            
            scenario_text = st.session_state[scenario_key]
            
            # Display scenario
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🎭</span>
                    <h3 style="color: #495057; margin: 0;">{scenario_title}</h3>
                </div>
                <p style="color: #495057; font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem;">{scenario_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate choices if not already done
            choice_key = f"choice_{i}_{current_scenario}"
            if choice_key not in st.session_state:
                with st.spinner("🎭 Preparing your options..."):
                    choice_data = generate_interactive_choice(
                        job['title'],
                        scenario_text,
                        "approach",
                        st.session_state.personality_type
                    )
                    st.session_state[choice_key] = choice_data
            
            choice_data = st.session_state[choice_key]
            
            # Display choices
            st.markdown("**🎭 What do you do?**")
            
            option_labels = [f"{key}: {value}" for key, value in choice_data['choices'].items()]
            selected_option = st.radio(
                "Choose your action:",
                option_labels,
                key=f"immersive_choice_{i}_{current_scenario}",
                help="Select the option that best represents how you would handle this situation"
            )
            
            selected_key = selected_option.split(":")[0] if selected_option else None
            
            # Submit choice button
            if st.button("🎭 Make Your Choice", key=f"submit_immersive_{i}_{current_scenario}"):
                if selected_key:
                    # Generate outcome
                    with st.spinner("🎭 Experiencing the consequences..."):
                        outcome = generate_scenario_outcome(
                            job['title'],
                            scenario_text,
                            choice_data['choices'][selected_key],
                            st.session_state.personality_type
                        )
                    
                    # Evaluate choice
                    with st.spinner("🎭 Analyzing your performance..."):
                        evaluation = evaluate_choice_effectiveness(
                            job['title'],
                            scenario_text,
                            choice_data['choices'][selected_key],
                            outcome,
                            st.session_state.personality_type
                        )
                    
                    # Store results
                    scores.append(evaluation['score'])
                    choices.append(choice_data['choices'][selected_key])
                    scenarios_completed.append(scenario_title)
                    st.session_state[scores_key] = scores
                    st.session_state[choices_key] = choices
                    st.session_state[scenarios_completed_key] = scenarios_completed
                    
                    # Show outcome and evaluation
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 4px solid #28a745; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(40, 167, 69, 0.2);">
                        <h4 style="color: #155724; margin-bottom: 1rem;">🎭 What Happens Next</h4>
                        <p style="color: #155724; line-height: 1.6;">{outcome}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left: 4px solid #2196f3; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(33, 150, 243, 0.2);">
                        <h4 style="color: #0d47a1; margin-bottom: 1rem;">📊 Performance Analysis</h4>
                        <p style="color: #0d47a1; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">Score: {evaluation['score']}/10</p>
                        <p style="color: #0d47a1; margin-bottom: 1rem;"><strong>Analysis:</strong> {evaluation['explanation']}</p>
                        <p style="color: #0d47a1; margin-bottom: 0.5rem;"><strong>Role Alignment:</strong> {evaluation['role_alignment']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show strengths and improvements
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%); border: 1px solid #bee5eb; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h5 style="color: #0c5460; margin-bottom: 0.5rem;">✨ What Worked Well:</h5>
                        </div>
                        """, unsafe_allow_html=True)
                        for strength in evaluation['strengths']:
                            st.markdown(f"• {strength}")
                    
                    with col2:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 1px solid #ffeaa7; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                            <h5 style="color: #856404; margin-bottom: 0.5rem;">🔧 Areas for Improvement:</h5>
                        </div>
                        """, unsafe_allow_html=True)
                        for improvement in evaluation['improvements']:
                            st.markdown(f"• {improvement}")
                    
                    # Move to next scenario
                    st.session_state[current_scenario_key] = current_scenario + 1
                    st.rerun()
                else:
                    st.error("Please select an option before proceeding.")
            
            # Progress indicator
            progress = (current_scenario / len(scenario_types)) * 100
            st.progress(progress / 100)
            st.markdown(f"**🎭 Progress: {current_scenario + 1}/{len(scenario_types)} scenarios completed**")
            
            # Show completed scenarios
            if scenarios_completed:
                st.markdown("**✅ Completed Scenarios:**")
                for i, scenario in enumerate(scenarios_completed, 1):
                    st.markdown(f"{i}. {scenario}")

def show_immersive_results(i, job):
    """Display completed immersive experience results"""
    if f'immersive_results_{i}' not in st.session_state:
        return
    
    results = st.session_state[f'immersive_results_{i}']
    final_score = results['final_score']
    role_fit = results['role_fit']
    strengths = results['strengths']
    improvements = results['improvements']
    career_recommendation = results['career_recommendation']
    scores = results['scores']
    scenarios_completed = results['scenarios_completed']
    
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">🎭 Immersive Experience Complete</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Your journey as a {job['title']} has revealed your true potential...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score and role fit
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);">
            <h3 style="color: white; margin-bottom: 0.5rem;">🌟 Overall Performance</h3>
            <h2 style="color: white; font-size: 2.5rem; margin: 0;">{final_score:.1f}/10</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">{role_fit} Fit</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);">
            <h3 style="color: white; margin-bottom: 0.5rem;">🎭 Scenarios Completed</h3>
            <h2 style="color: white; font-size: 2.5rem; margin: 0;">{len(scenarios_completed)}</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">Immersive Experiences</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Career recommendation
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
        <h4 style="color: white; margin-bottom: 1rem;">🌟 Career Recommendation</h4>
        <p style="color: white; font-size: 1.1rem; line-height: 1.6;"><strong>{career_recommendation}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">✨ Key Strengths</h4>
        </div>
        """, unsafe_allow_html=True)
        for strength in strengths:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 1rem;">🔧 Development Areas</h4>
        </div>
        """, unsafe_allow_html=True)
        for improvement in improvements:
            st.markdown(f"• {improvement}")
    
    # Scenario breakdown
    st.markdown("**📊 Scenario Performance Breakdown:**")
    for i, (scenario, score) in enumerate(zip(scenarios_completed, scores), 1):
        st.markdown(f"{i}. **{scenario}**: {score}/10")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎭 Retry Experience", key=f"retry_immersive_{i}"):
            st.session_state[f'immersive_completed_{i}'] = False
            st.session_state[f'immersive_started_{i}'] = False
            st.session_state[f'current_scenario_{i}'] = 0
            st.session_state[f'scenarios_completed_{i}'] = []
            st.session_state[f'immersive_scores_{i}'] = []
            st.session_state[f'immersive_choices_{i}'] = []
            # Clear scenario and choice data
            for key in list(st.session_state.keys()):
                if key.startswith(f'scenario_{i}_') or key.startswith(f'choice_{i}_'):
                    del st.session_state[key]
            if f'immersive_results_{i}' in st.session_state:
                del st.session_state[f'immersive_results_{i}']
            st.rerun()
    
    with col2:
        if st.button("🎤 Try Mock Interview", key=f"try_interview_{i}"):
            st.session_state.current_page = 'interview'
            st.rerun()
    
    with col3:
        if st.button("📄 Download Report", key=f"download_immersive_{i}"):
            # Create a comprehensive report
            report = f"""
🎭 CareerOracle - Immersive Experience Report
============================================

Role: {job['title']}
Personality Type: {st.session_state.personality_type}

📊 PERFORMANCE SUMMARY:
- Overall Score: {final_score:.1f}/10
- Role Fit: {role_fit}
- Scenarios Completed: {len(scenarios_completed)}

🎭 SCENARIO BREAKDOWN:
{chr(10).join([f"- {scenario}: {score}/10" for scenario, score in zip(scenarios_completed, scores)])}

🌟 CAREER RECOMMENDATION:
{career_recommendation}

✨ KEY STRENGTHS:
{chr(10).join([f"- {strength}" for strength in strengths])}

🔧 DEVELOPMENT AREAS:
{chr(10).join([f"- {improvement}" for improvement in improvements])}

Generated by CareerOracle - The Immersive Career Experience
            """
            
            st.download_button(
                label="📄 Download Report",
                data=report,
                file_name=f"immersive_experience_report_{job['title'].replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"download_immersive_report_{i}"
            ) 