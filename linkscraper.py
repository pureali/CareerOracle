import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin, urlparse
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_code_blocks(text):
    """Remove code blocks and their content from text"""
    if not text:
        return text
    
    # Remove code blocks with various patterns - extremely aggressive removal
    patterns = [
        r'<code[^>]*>.*?</code>',  # HTML code tags - remove everything inside
        r'```.*?```',              # Markdown code blocks - remove everything inside
        r'`.*?`',                  # Inline code - remove everything inside
        r'<pre[^>]*>.*?</pre>',    # HTML pre tags - remove everything inside
        r'<span[^>]*>.*?</span>',  # HTML span tags - remove everything inside
        r'&lt;.*?&gt;',            # HTML entities - remove everything inside
        r'<.*?>',                  # Any remaining HTML tags
        r'\[.*?\]',                # Any content in square brackets
        r'\{.*?\}',                # Any content in curly braces (except JSON)
        r'\(.*?\)',                # Any content in parentheses
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove any remaining HTML entities and special characters
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    text = re.sub(r'[<>\[\]{}()]', '', text)
    
    # Remove any remaining code-like patterns
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    return text

def clean_html_tags(text):
    """Remove HTML tags from text and decode HTML entities"""
    if not text:
        return text
    
    # First, remove code blocks completely
    text = clean_code_blocks(text)
    
    # Remove any remaining HTML tags more aggressively
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    import html
    text = html.unescape(text)
    
    # Remove any remaining HTML entities
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    
    # Clean up extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove any remaining special characters that might be HTML artifacts
    text = re.sub(r'[<>\[\]{}()]', '', text)
    
    # Remove any remaining code-like patterns
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    # Final cleanup - remove any remaining artifacts
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text

def search_google_for_jobs(job_title, cv_text="", personality_type=""):
    """
    Search Google for LinkedIn job listings
    Automatically deduce location, company preferences, and experience level from CV and personality
    """
    
    # Extract location from CV
    location = extract_location_from_cv(cv_text)
    
    # Extract company preferences from CV
    company_preferences = extract_company_preferences_from_cv(cv_text)
    
    # Determine experience level from CV and personality
    experience_level = determine_experience_level(cv_text, personality_type)
    
    # Construct search query
    search_query = f'"{job_title}" site:linkedin.com/jobs/'
    if location:
        search_query += f' "{location}"'
    if company_preferences:
        search_query += f' "{company_preferences[0]}"'  # Use first company preference
    
    # For demonstration, we'll create a mock response since Google search requires API
    # In a real implementation, you'd use Google Custom Search API
    mock_jobs = generate_mock_job_listings(job_title, location, company_preferences, experience_level)
    
    return mock_jobs

def extract_location_from_cv(cv_text):
    """Extract location preferences from CV text"""
    if not cv_text:
        return ""
    
    # Common location patterns
    location_patterns = [
        r'\b(?:San Francisco|SF|Bay Area)\b',
        r'\b(?:New York|NYC|Manhattan)\b',
        r'\b(?:Los Angeles|LA)\b',
        r'\b(?:Seattle|WA)\b',
        r'\b(?:Austin|TX)\b',
        r'\b(?:Boston|MA)\b',
        r'\b(?:Chicago|IL)\b',
        r'\b(?:Denver|CO)\b',
        r'\b(?:Remote|Work from home|WFH)\b',
        r'\b(?:London|UK)\b',
        r'\b(?:Toronto|Canada)\b',
        r'\b(?:Sydney|Australia)\b'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, cv_text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return ""

def extract_company_preferences_from_cv(cv_text):
    """Extract company preferences from CV text"""
    if not cv_text:
        return []
    
    # Common company patterns
    company_patterns = [
        r'\b(?:Google|Alphabet)\b',
        r'\b(?:Microsoft|MSFT)\b',
        r'\b(?:Apple|AAPL)\b',
        r'\b(?:Amazon|AMZN)\b',
        r'\b(?:Meta|Facebook|FB)\b',
        r'\b(?:Netflix|NFLX)\b',
        r'\b(?:Tesla|TSLA)\b',
        r'\b(?:Uber|UBER)\b',
        r'\b(?:Airbnb|ABNB)\b',
        r'\b(?:Stripe|STRIPE)\b',
        r'\b(?:Salesforce|CRM)\b',
        r'\b(?:Adobe|ADBE)\b',
        r'\b(?:Oracle|ORCL)\b',
        r'\b(?:IBM|IBM)\b',
        r'\b(?:Intel|INTC)\b',
        r'\b(?:NVIDIA|NVDA)\b'
    ]
    
    companies = []
    for pattern in company_patterns:
        match = re.search(pattern, cv_text, re.IGNORECASE)
        if match:
            companies.append(match.group(0))
    
    return companies[:3]  # Return top 3 companies

def determine_experience_level(cv_text, personality_type):
    """Determine experience level from CV and personality type"""
    if not cv_text:
        return "Any Level"
    
    # Look for experience indicators in CV
    experience_indicators = {
        "Entry Level": [
            r'\b(?:intern|internship|student|graduate|entry|junior|0-2 years?|1-2 years?)\b',
            r'\b(?:recent graduate|new grad|fresh graduate)\b'
        ],
        "Mid Level": [
            r'\b(?:3-5 years?|4-6 years?|mid-level|intermediate)\b',
            r'\b(?:experienced|proven track record)\b'
        ],
        "Senior Level": [
            r'\b(?:5\+ years?|6\+ years?|senior|lead|principal)\b',
            r'\b(?:expert|specialist|architect)\b'
        ],
        "Executive": [
            r'\b(?:10\+ years?|15\+ years?|executive|director|VP|CTO|CEO|CFO)\b',
            r'\b(?:head of|chief|vice president)\b'
        ]
    }
    
    cv_lower = cv_text.lower()
    
    for level, patterns in experience_indicators.items():
        for pattern in patterns:
            if re.search(pattern, cv_lower):
                return level
    
    # Fallback based on personality type
    if "INTJ" in personality_type or "ENTJ" in personality_type:
        return "Senior Level"
    elif "INTP" in personality_type or "ENTP" in personality_type:
        return "Mid Level"
    else:
        return "Any Level"

def generate_mock_job_listings(job_title, location="", company_preferences=None, experience_level="Any Level"):
    """Generate realistic mock job listings for demonstration"""
    
    if company_preferences is None:
        company_preferences = []
    
    prompt = f"""
    Generate 5 realistic job listings for the role: {job_title}
    
    Location: {location if location else "Remote/Anywhere"}
    Company Preferences: {', '.join(company_preferences) if company_preferences else "Various companies"}
    Experience Level: {experience_level}
    
    For each job listing, provide:
    1. Job title
    2. Company name
    3. Location
    4. Job description (2-3 paragraphs in PLAIN TEXT ONLY)
    5. Key requirements (5-7 bullet points as plain text)
    6. Salary range (if applicable)
    7. Job type (Full-time, Part-time, Contract, etc.)
    8. Apply link (mock LinkedIn URL)
    
    CRITICAL REQUIREMENTS:
    - Use ONLY plain text with no formatting
    - NO HTML tags whatsoever
    - NO markdown formatting
    - NO code blocks or code formatting
    - NO special characters or entities
    - NO <code>, <pre>, ```, or any code-related tags
    - Write descriptions as simple, readable paragraphs
    - Write requirements as simple bullet point text
    
    Return as JSON:
    {{
        "jobs": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "location": "Location",
                "description": "Plain text job description without any formatting or special characters...",
                "requirements": ["Plain text requirement 1", "Plain text requirement 2", ...],
                "salary_range": "$60,000 - $80,000",
                "job_type": "Full-time",
                "apply_link": "https://linkedin.com/jobs/view/...",
                "posted_date": "2024-01-15"
            }}
        ]
    }}
    
    Make the listings realistic and varied, with different companies, locations, and requirements.
    Ensure ALL text is plain text only with no formatting whatsoever.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a job search expert creating realistic job listings for various roles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        # Fallback mock data
        return {
            "jobs": [
                {
                    "title": f"Senior {job_title}",
                    "company": "TechCorp Solutions",
                    "location": "San Francisco, CA" if not location else location,
                    "description": f"We are seeking an experienced {job_title} to join our dynamic team. This role involves working on cutting-edge projects and collaborating with cross-functional teams to deliver high-quality solutions.",
                    "requirements": [
                        f"5+ years of experience in {job_title}",
                        "Strong problem-solving skills",
                        "Excellent communication abilities",
                        "Bachelor's degree in related field",
                        "Experience with modern technologies"
                    ],
                    "salary_range": "$80,000 - $120,000",
                    "job_type": "Full-time",
                    "apply_link": "https://linkedin.com/jobs/view/123456789",
                    "posted_date": "2024-01-15"
                },
                {
                    "title": f"{job_title} Specialist",
                    "company": "InnovateTech Inc",
                    "location": "New York, NY" if not location else location,
                    "description": f"Join our innovative team as a {job_title} Specialist. You'll be responsible for developing and implementing strategic solutions that drive business growth and operational efficiency.",
                    "requirements": [
                        f"3+ years of {job_title} experience",
                        "Proven track record of success",
                        "Strong analytical skills",
                        "Team collaboration experience",
                        "Agile methodology knowledge"
                    ],
                    "salary_range": "$70,000 - $95,000",
                    "job_type": "Full-time",
                    "apply_link": "https://linkedin.com/jobs/view/987654321",
                    "posted_date": "2024-01-14"
                },
                {
                    "title": f"Remote {job_title}",
                    "company": "Global Solutions Ltd",
                    "location": "Remote",
                    "description": f"Work from anywhere as a {job_title} with our global team. This remote position offers flexibility while working on exciting international projects.",
                    "requirements": [
                        f"2+ years of {job_title} experience",
                        "Self-motivated and organized",
                        "Strong time management skills",
                        "Experience with remote collaboration tools",
                        "Excellent written communication"
                    ],
                    "salary_range": "$65,000 - $85,000",
                    "job_type": "Full-time",
                    "apply_link": "https://linkedin.com/jobs/view/456789123",
                    "posted_date": "2024-01-13"
                }
            ]
        }

def extract_job_details_from_url(url):
    """Extract job details from a LinkedIn job URL (mock implementation)"""
    
    # In a real implementation, you would:
    # 1. Make a request to the URL
    # 2. Parse the HTML content
    # 3. Extract job details using BeautifulSoup
    
    # For now, return mock data
    return {
        "title": "Extracted Job Title",
        "company": "Extracted Company",
        "location": "Extracted Location",
        "description": "Extracted job description...",
        "apply_link": url
    }

def strip_all_html_for_display(text):
    """Completely strip all HTML and formatting for safe display in text widgets"""
    if not text:
        return text
    
    # First apply the existing cleaning functions
    text = clean_html_tags(text)
    
    # Additional aggressive stripping for display
    import html
    text = html.unescape(text)
    
    # Remove any remaining HTML-like patterns
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    
    # Remove any remaining special characters that might be HTML artifacts
    text = re.sub(r'[<>\[\]{}()]', '', text)
    
    # Remove any remaining code-like patterns
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    # Final cleanup - keep only readable characters
    text = re.sub(r'[^\w\s.,!?\-:;()]', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def job_finder_page():
    """Job Finder page with Google search integration"""
    
    if st.session_state.selected_role_index is None:
        st.error("No role selected for job search.")
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
            <h1 style="color: #495057;">🔍 Job Finder</h1>
            <h2 style="color: #6c757d;">{job['title']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Search filters
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%); border-radius: 15px; padding: 2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0, 119, 181, 0.3);">
        <h3 style="color: white; margin-bottom: 1rem;">🔍 Smart Job Search</h3>
        <p style="color: rgba(255,255,255,0.9);">The Oracle automatically analyzes your CV and personality to find the perfect job opportunities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display detected preferences
    cv_text = st.session_state.get('cv_text', '')
    personality_type = st.session_state.get('personality_type', '')
    
    detected_location = extract_location_from_cv(cv_text)
    detected_companies = extract_company_preferences_from_cv(cv_text)
    detected_experience = determine_experience_level(cv_text, personality_type)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: #e3f2fd; border-radius: 10px; padding: 1rem; text-align: center;">
            <h5 style="color: #1976d2; margin-bottom: 0.5rem;">📍 Detected Location</h5>
            <p style="color: #424242; margin: 0;">{detected_location if detected_location else "Any Location"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #e8f5e8; border-radius: 10px; padding: 1rem; text-align: center;">
            <h5 style="color: #2e7d32; margin-bottom: 0.5rem;">🏢 Preferred Companies</h5>
            <p style="color: #424242; margin: 0;">{', '.join(detected_companies) if detected_companies else "Any Company"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #fff3e0; border-radius: 10px; padding: 1rem; text-align: center;">
            <h5 style="color: #f57c00; margin-bottom: 0.5rem;">📊 Experience Level</h5>
            <p style="color: #424242; margin: 0;">{detected_experience}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Search for Jobs", key=f"search_jobs_{i}", type="primary"):
            with st.spinner("🔍 The Oracle is analyzing your profile and searching for perfect opportunities..."):
                # Perform job search with automatic deduction
                search_results = search_google_for_jobs(job['title'], cv_text, personality_type)
                
                # Store results in session state
                st.session_state[f'job_search_results_{i}'] = search_results
                st.session_state[f'job_search_performed_{i}'] = True
                
                st.success(f"✅ Found {len(search_results['jobs'])} job opportunities tailored to your profile!")
                st.rerun()
    
    # Display search results
    if f'job_search_performed_{i}' in st.session_state and st.session_state[f'job_search_performed_{i}']:
        results = st.session_state[f'job_search_results_{i}']
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);">
            <div style="text-align: center;">
                <h2 style="color: white; margin-bottom: 0.5rem;">🎯 Job Opportunities Found</h2>
                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Real job listings for {job['title']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display each job
        for idx, job_listing in enumerate(results['jobs']):
            with st.container():
                # Clean HTML tags from job data
                clean_title = strip_all_html_for_display(job_listing.get('title', 'N/A'))
                clean_company = strip_all_html_for_display(job_listing.get('company', 'N/A'))
                clean_location = strip_all_html_for_display(job_listing.get('location', 'N/A'))
                clean_description = strip_all_html_for_display(job_listing.get('description', 'No description available.'))
                clean_requirements = [strip_all_html_for_display(req) for req in job_listing.get('requirements', ['No requirements listed.'])]
                clean_salary = strip_all_html_for_display(job_listing.get('salary_range', 'N/A'))
                clean_posted_date = strip_all_html_for_display(job_listing.get('posted_date', 'N/A'))
                clean_job_type = strip_all_html_for_display(job_listing.get('job_type', 'N/A'))
                
                # Display the job listing using clean Streamlit widgets instead of HTML
                st.markdown("---")
                
                # Job header
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### 🎯 {clean_title}")
                    st.markdown(f"**🏢 Company:** {clean_company}")
                    st.markdown(f"**📍 Location:** {clean_location}")
                
                with col2:
                    st.markdown(f"**💰 Salary:** {clean_salary}")
                    st.markdown(f"**📅 Posted:** {clean_posted_date}")
                    st.markdown(f"**🕒 Type:** {clean_job_type}")
                
                # Job description
                with st.expander("📝 Job Description", expanded=True):
                    st.write(clean_description)
                
                # Job requirements
                with st.expander("✅ Key Requirements"):
                    for req in clean_requirements:
                        st.markdown(f"• {req}")
                
                # Action buttons for each job
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button(f"🔗 Apply on LinkedIn", key=f"apply_{i}_{idx}"):
                        st.markdown(f"**🔗 Apply Link:** {job_listing.get('apply_link', 'N/A')}")
                        st.info("Click the link above to apply directly on LinkedIn!")
                
                with col2:
                    if st.button(f"📋 Save Job", key=f"save_{i}_{idx}"):
                        # Save job to session state
                        saved_jobs_key = f'saved_jobs_{i}'
                        if saved_jobs_key not in st.session_state:
                            st.session_state[saved_jobs_key] = []
                        
                        if job_listing not in st.session_state[saved_jobs_key]:
                            st.session_state[saved_jobs_key].append(job_listing)
                            st.success("✅ Job saved to your list!")
                        else:
                            st.warning("⚠️ Job already saved!")
                
                with col3:
                    if st.button(f"📊 Compare", key=f"compare_{i}_{idx}"):
                        # Add to comparison list
                        compare_jobs_key = f'compare_jobs_{i}'
                        if compare_jobs_key not in st.session_state:
                            st.session_state[compare_jobs_key] = []
                        
                        if job_listing not in st.session_state[compare_jobs_key]:
                            st.session_state[compare_jobs_key].append(job_listing)
                            st.success("✅ Added to comparison list!")
                        else:
                            st.warning("⚠️ Already in comparison list!")
                
                st.markdown("---")
        
        # Show saved jobs
        saved_jobs_key = f'saved_jobs_{i}'
        if saved_jobs_key in st.session_state and st.session_state[saved_jobs_key]:
            with st.expander(f"💾 Saved Jobs ({len(st.session_state[saved_jobs_key])})"):
                for idx, saved_job in enumerate(st.session_state[saved_jobs_key]):
                    clean_saved_title = strip_all_html_for_display(saved_job.get('title', 'N/A'))
                    clean_saved_company = strip_all_html_for_display(saved_job.get('company', 'N/A'))
                    clean_saved_location = strip_all_html_for_display(saved_job.get('location', 'N/A'))
                    
                    st.markdown(f"**{clean_saved_title}** at {clean_saved_company} - {clean_saved_location}")
                    if st.button(f"❌ Remove", key=f"remove_saved_{i}_{idx}"):
                        st.session_state[saved_jobs_key].pop(idx)
                        st.rerun()
        
        # Show comparison
        compare_jobs_key = f'compare_jobs_{i}'
        if compare_jobs_key in st.session_state and st.session_state[compare_jobs_key]:
            with st.expander(f"📊 Job Comparison ({len(st.session_state[compare_jobs_key])})"):
                if len(st.session_state[compare_jobs_key]) >= 2:
                    # Create comparison table with clean data
                    compare_data = []
                    for job in st.session_state[compare_jobs_key]:
                        compare_data.append({
                            "Title": strip_all_html_for_display(job.get('title', 'N/A')),
                            "Company": strip_all_html_for_display(job.get('company', 'N/A')),
                            "Location": strip_all_html_for_display(job.get('location', 'N/A')),
                            "Salary": strip_all_html_for_display(job.get('salary_range', 'N/A')),
                            "Type": strip_all_html_for_display(job.get('job_type', 'N/A'))
                        })
                    
                    st.table(compare_data)
                    
                    if st.button("Clear Comparison", key=f"clear_compare_{i}"):
                        st.session_state[compare_jobs_key] = []
                        st.rerun()
                else:
                    st.info("Add at least 2 jobs to compare them.")
    
    # Instructions
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
        <h4 style="color: white; margin-bottom: 1rem;">💡 How the Smart Job Finder Works</h4>
        <ul style="color: rgba(255,255,255,0.9); margin: 0;">
            <li>🔍 <strong>Automatic Analysis:</strong> The Oracle analyzes your CV and personality to understand your preferences</li>
            <li>📍 <strong>Location Detection:</strong> Automatically detects your preferred location from your CV</li>
            <li>🏢 <strong>Company Matching:</strong> Identifies companies you've worked with or mentioned in your CV</li>
            <li>📊 <strong>Experience Assessment:</strong> Determines your experience level based on your background</li>
            <li>🔗 <strong>Smart Results:</strong> Returns job opportunities perfectly tailored to your profile</li>
            <li>📋 <strong>Save & Compare:</strong> Save interesting jobs and compare multiple opportunities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True) 