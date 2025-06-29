# CareerOracle - Mystical Career Advisor

A Streamlit application that provides mystical career guidance through AI-powered analysis of CVs and personality types, featuring interactive role-playing trials, professional interviews, and real job search functionality.

## Features

- **🔮 Oracle's Prophecies**: AI-generated job recommendations based on CV analysis and personality type
- **🎭 Immersive Experience**: Interactive role-playing game with realistic workplace scenarios
- **🎤 Professional Interview**: AI-conducted interview with voice interaction capabilities
- **🔍 Job Finder**: Search for real job opportunities on LinkedIn with customizable filters
- **📊 Comprehensive Scoring**: Detailed assessment with technical and psychological breakdown
- **📄 Downloadable Reports**: Export your results for future reference

## Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/CareerOracle.git
cd CareerOracle
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Edit .env file and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the application**:
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## Project Structure

```
CareerOracle/
├── app.py              # Main application with navigation and job recommendations
├── role_playing.py     # Immersive role-playing experience
├── interview.py        # Professional interview functionality
├── linkscraper.py      # Job Finder with LinkedIn job search
├── google_speech.py    # Voice interaction capabilities
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
└── README.md          # This file
```

## Usage

1. **Upload Your CV**: Upload a PDF version of your CV
2. **Select Personality Type**: Choose your MBTI personality type
3. **Generate Recommendations**: Get AI-powered job recommendations
4. **Take Immersive Experience**: Experience realistic workplace scenarios
5. **Try Mock Interview**: Practice with AI-conducted interviews
6. **Find Real Jobs**: Search for actual job opportunities
7. **Download Results**: Save your assessment reports

## Features in Detail

### 🎭 Immersive Experience
- Realistic workplace scenarios
- Interactive decision-making
- Role-specific challenges
- Performance evaluation

### 🎤 Professional Interview
- AI-generated interview questions
- Voice interaction capabilities
- Detailed answer evaluation
- Career recommendations

### 🔍 Job Finder
- Real LinkedIn job search
- Smart filtering options
- Job saving and comparison
- Direct application links

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.