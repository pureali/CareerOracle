# CareerOracle - Mystical Career Advisor

A Streamlit application that provides mystical career guidance through AI-powered analysis of CVs and personality types, featuring interactive role-playing trials, professional interviews, and real job search functionality.

## Features

- **🔮 Oracle's Prophecies**: AI-generated job recommendations based on CV analysis and personality type
- **⚙️ Oracle's Trial**: Interactive role-playing game with technical and psychology questions
- **🎤 Professional Interview**: AI-conducted interview with **voice interaction** - questions are spoken and answers recorded via microphone
- **🔍 Job Finder**: Search for real job opportunities on LinkedIn with customizable filters
- **📊 Comprehensive Scoring**: Detailed assessment with technical and psychological breakdown
- **📄 Downloadable Reports**: Export your results for future reference

## Project Structure

```
CareerOracle/
├── app.py              # Main application with navigation and job recommendations
├── role_playing.py     # Oracle's Trial game logic and question generation
├── interview.py        # Professional interview functionality
├── linkscraper.py      # Job Finder with LinkedIn job search
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Modules

### `app.py`
- Main application entry point
- Job recommendation generation
- CV parsing and analysis
- Navigation between different features
- Main page with personality selection and CV upload

### `role_playing.py`
- Oracle's Trial game implementation
- Question generation for different job roles
- Answer evaluation and scoring
- Game state management
- Results display and reporting

### `interview.py`
- Professional interview functionality
- **🔊 AI Spoken Questions**: Questions are spoken aloud using text-to-speech
- **🎤 Voice Responses**: Users can record answers using microphone
- **📝 Audio Transcription**: Voice responses are converted to text using OpenAI Whisper
- **📊 AI Evaluation**: Detailed feedback and scoring for responses
- Interview results and recommendations

### `linkscraper.py`
- **🔍 Job Finder**: Search for real job opportunities
- **🌐 LinkedIn Integration**: Search LinkedIn job listings using Google search
- **📍 Location Filtering**: Filter jobs by location
- **🏢 Company Filtering**: Filter jobs by specific companies
- **📊 Experience Level**: Filter by experience requirements
- **💾 Job Saving**: Save interesting jobs for later review
- **📊 Job Comparison**: Compare multiple job opportunities side by side
- **🔗 Direct Apply Links**: Direct links to apply on LinkedIn

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CareerOracle
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env and add your OpenAI API key
```

5. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Upload Your CV**: Upload a PDF version of your CV
2. **Select Personality Type**: Choose your MBTI personality type from the dropdown
3. **Generate Recommendations**: Click "Seek Oracle's Prophecy" to get job recommendations
4. **Take Oracle's Trial**: Click on any job to start the interactive role-playing game
5. **Professional Interview**: Try the AI-conducted interview with voice interaction:
   - **Listen to Questions**: AI speaks each interview question aloud
   - **Record Answers**: Use your microphone to record your responses
   - **Upload Audio**: Upload recorded audio files for transcription
   - **Get Feedback**: Receive detailed evaluation of your answers
6. **🔍 Find Real Jobs**: Use the Job Finder to search for actual job opportunities:
   - **Search Filters**: Filter by location, company, and experience level
   - **Job Listings**: View detailed job descriptions and requirements
   - **Save Jobs**: Save interesting opportunities for later review
   - **Compare Jobs**: Compare multiple positions side by side
   - **Apply Directly**: Click apply links to go directly to LinkedIn
7. **Download Results**: Save your assessment reports for future reference

## Features in Detail

### Oracle's Trial
- 5 questions per role (3 technical + 2 psychology)
- Real-time scoring and feedback
- Role-specific scenarios and challenges
- Comprehensive final assessment

### Professional Interview
- AI-generated interview questions
- Detailed answer evaluation
- Strengths and improvement areas
- Career recommendations

### Job Finder
- **Real Job Search**: Search actual LinkedIn job listings
- **Smart Filtering**: Filter by location, company, experience level
- **Detailed Listings**: View complete job descriptions and requirements
- **Salary Information**: See salary ranges when available
- **Job Management**: Save and compare job opportunities
- **Direct Application**: One-click apply links to LinkedIn

### Job Recommendations
- AI-powered analysis of CV content
- Personality type consideration
- Salary range and growth potential
- Suitability scoring

## Dependencies

- `streamlit`: Web application framework
- `openai`: OpenAI API integration
- `PyPDF2`: PDF text extraction
- `python-dotenv`: Environment variable management
- `beautifulsoup4`: Web scraping for job search
- `requests`: HTTP requests for web scraping

## Contributing

The modular structure makes it easy to:
- Add new question types to `role_playing.py`
- Modify interview logic in `interview.py`
- Enhance job search functionality in `linkscraper.py`
- Enhance job recommendations in `app.py`
- Add new features as separate modules

## License

This project is licensed under the MIT License.