# 🤖 The AIBert - AI-Assisted Grading and Educational System

A comprehensive AI-powered educational platform that combines intelligent tutoring, automated grading, and advanced analytics to enhance the learning experience for both students and educators. This modern web application provides seamless integration with Google Classroom while offering cutting-edge AI capabilities for educational assessment.

---

## 🌟 Features

### 🎯 Core Educational Platform
- 🔐 Google Sign-In authentication
- 🧑‍🏫 Connect and manage Google Classroom using OAuth
- 🧠 Google Gemini-powered quiz generation & evaluation
- 📋 Auto-create Google Forms with questions
- 📄 Fetch, analyze, and store student responses
- 📈 Export feedback and scores to Google Sheets
- 🌐 Deployed using Vite + Amazon Web Service (AWS)
- 💾 MongoDB integration for activity logs and recovery

### 🤖 Advanced AI Grading System
- **Automated Grading**: Deep learning-based answer evaluation with multiple criteria
- **OCR Integration**: Handwritten and printed text recognition for exam scripts
- **Semantic Analysis**: BERT/SBERT models for deep answer understanding
- **Intelligent Feedback**: Automated generation of detailed, personalized feedback
- **Human Verification**: Quality control system for flagged responses
- **Analytics Dashboard**: Comprehensive performance insights and trend analysis
- **Answer Mapping**: Regex and semantic matching for structured answer extraction

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  • HTML/CSS/JS Interface  • Grading Dashboard  • Analytics UI   │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      AI Backend (Flask)                         │
├─────────────────────────────────────────────────────────────────┤
│  • OCR Module          • Grading Engine      • Feedback Gen     │
│  • Human Verification  • Answer Mapper       • Analytics        │
│  • AIML Manager        • Educational AI      • Training Mgr     │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      ML Models Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  • TrOCR (Handwriting)  • BERT/SBERT (Grading)                 │
│  • Sentence Transformers • Intent Classification                │
│  • Sentiment Analysis   • Educational Assistant                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
📁 The-AIBert/
├── 📁 ai_backend/             # Python Flask AI backend
│   ├── app.py                 # Main Flask application
│   ├── 📁 ml_models/          # Machine learning models
│   │   ├── ocr_module.py      # OCR processing (TrOCR + Tesseract)
│   │   ├── grading_engine.py  # Advanced grading with BERT/SBERT
│   │   ├── feedback_generator.py # Intelligent feedback generation
│   │   ├── human_verification.py # Human review system
│   │   ├── answer_mapper.py   # Answer extraction and mapping
│   │   └── educational_assistant.py # AI tutoring assistant
│   ├── 📁 aiml_engine/        # AIML processing
│   ├── 📁 analytics/          # Performance analytics
│   └── 📁 utils/              # Utility functions
│
├── 📁 assets/                 # UI images and icons
├── 📁 .vscode/                # VSCode settings
├── .gitignore                 # Ignore sensitive files
├── package.json               # Node.js dependencies
├── requirements.txt           # Python dependencies
├── server.js                  # Node.js server for OAuth
├── .env                       # Environment variables (NOT COMMITTED)
│
├── index.html                 # Main login page
├── grading.html               # AI grading system interface
├── dashboard.html             # Teacher dashboard
├── chatbot.html               # AI quiz generation
├── grades.html                # Student grades view
├── result.html                # Results and analytics
│
├── grading.css                # Grading system styles
├── grading.js                 # Grading system functionality
├── gemini.js                  # Gemini API integration
├── mobile.css                 # Responsive styles
└── test_grading_system.py     # Comprehensive test suite
```

---

## 🚀 Getting Started

### 1. **Clone the repository**

```bash
git clone https://github.com/Nikhil-Emmanuel/The-AIBert.git
cd The-AIBert
```

---

### 2. **Install dependencies**

```bash
npm install
```

---

### 3. **Install Python dependencies for AI backend**

```bash
pip install -r requirements.txt
```

### 4. **Create a `.env` file**

Create a `.env` in the **root directory** and add your sensitive credentials:

```env
# Google OAuth & API Configuration
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_GOOGLE_CLASSROOM_API_KEY=your_google_api_key

# Database Configuration
MONGODB_URI=your_mongodb_connection_string

# AI Backend Configuration
AI_BACKEND_PORT=5000
FLASK_DEBUG=False

# Model Configuration (Optional)
CUDA_VISIBLE_DEVICES=0
MODEL_CACHE_DIR=./models
```

> ✅ **Do NOT commit your `.env` file.** It's listed in `.gitignore` for safety.

---

### 4. **Run the project locally**

```bash
npm run dev
```

> This uses **Vite** to start the project on `http://localhost:5173` (or similar).

---

## 🧾 What Each File Does (Explained Briefly)

| File/Folder        | Purpose |
|--------------------|---------|
| `index.html`       | Entry point, handles login and Classroom code |
| `main.js`          | Handles Google Sign-In, token, and navigation |
| `dashboard.html`   | Main dashboard interface post login |
| `dashboard.js`     | Fetches students, activity logs, class data and action links|
| `chatbot.html`     | Gemini-based quiz and question generator |
| `chatbot.js`       | Sends topic to Gemini and creates Google Form with integration |
| `grades.html`      | Shows scores and AI-based feedback |
| `grades.js`        | Fetches and renders graded scores into readable formats |
| `result.html`      | Shows exported Google Sheets with topic and timestamp |
| `result.js`        | Lists Google Sheets links from MongoDB |
| `gemini.js`        | Handles interaction with Gemini model and prompt structuring |
| `server.js`        | Backend logic: OAuth, DataBase, Forms, Sheets, API Calls |
| `package.json`     | Lists dependencies like `googleapis`, `vite`, `generativeAI` |
| `.env`             | Keeps sensitive API keys secure |
| `assets/`          | Contains images used in UI |
| `mobile.css`       | Makes the site responsive for mobile device screens |

---

## ☁️ Cloud Services Used

- **Google's Project IDX** for code development and testing
- **Gemini API (Google Generative AI)** for evaluation and question generation
- **Google Cloud Console** for API and scope configurations
- **Google OAuth 2.0** for authentication
- **Google Classroom API** for accessing existing class and student interaction
- **Google Forms API** to auto-create quizzes and extract responses
- **Google Sheets API** to export results
- **MongoDB Atlas** for storing responses & logs

---

## 🧪 Sample Usage Flow

1. Teacher login using Google Sign-In on `index.html`.
2. Enters Classroom Code or creates a  Google Classroom.
3. Navigates to the chatbot, generates a quiz, review the questions and post it.
4. Students respond via the Google Form posted on Google Classroom.
5. Teacher waits until due date and clicks "Grade" to evaluate responses and feedback using Gemini AI in `grade.html`.
6. Views results, scores and feedbacks as Google Sheets  in `result.html`.
7. Contains individual sheet for each student, which can then be reviewed and exported.

8. Demo account : Email    - gdg25demo@gmail.com
                  Password - AIBertGDG25
---

## 🛡️ Security Tips

- Never expose your `.env` file
- Use `.gitignore` to exclude sensitive files
- Always use HTTPS when deployed

---

## 🤖 AI Grading System - Advanced Features

### 🎯 Automated Grading Capabilities

The AIBert now includes a comprehensive AI-powered grading system with the following features:

#### 📝 OCR Integration
- **Handwritten Text Recognition**: Using Microsoft's TrOCR model for accurate handwriting detection
- **Printed Text Processing**: Tesseract OCR for typed documents
- **Multi-format Support**: Process images, PDFs, and scanned documents
- **Confidence Scoring**: Each extracted text comes with confidence metrics

#### 🧠 Intelligent Grading Engine
- **Semantic Analysis**: BERT/SBERT models for deep understanding of answers
- **Multi-criteria Evaluation**:
  - Semantic Similarity (35%)
  - Factual Accuracy (25%)
  - Completeness (20%)
  - Relevance (10%)
  - Clarity & Coherence (10%)
- **Customizable Rubrics**: Adjust weights based on subject requirements

#### 💬 Feedback Generation
- **Personalized Feedback**: AI-generated detailed explanations
- **Performance Categorization**: Excellent, Good, Fair, Poor with specific recommendations
- **Improvement Suggestions**: Targeted advice for student growth

#### 👥 Human Verification System
- **Quality Control**: Automatic flagging of uncertain grades for human review
- **Review Queue**: Organized workflow for educators to verify AI decisions
- **Confidence Thresholds**: Configurable limits for automatic vs. manual review

#### 📊 Advanced Analytics
- **Student Performance Tracking**: Individual progress over time
- **Class-wide Insights**: Identify trends and areas needing attention
- **Grading Consistency**: Monitor AI performance and accuracy
- **Export Capabilities**: Generate reports in multiple formats

### 🚀 Getting Started with AI Grading

1. **Access the AI Grading System**: Click "🤖 AI Grading System" from the main dashboard
2. **Upload Documents**: Drag and drop exam scripts or type answers manually
3. **Configure Settings**: Set grading criteria and maximum scores
4. **Review Results**: Examine AI-generated scores and feedback
5. **Human Verification**: Review flagged items in the verification queue
6. **Generate Reports**: Create comprehensive analytics and export data

### 📊 API Endpoints for AI Grading

```bash
# Comprehensive grading with all features
POST /grading/comprehensive
{
  "question": "Explain photosynthesis",
  "student_answer": "Plants make food using sunlight",
  "correct_answer": "Photosynthesis is the process...",
  "student_id": "student123",
  "exam_id": "biology_exam_1"
}

# OCR processing for handwritten text
POST /ocr/process
{
  "image": "base64_encoded_image",
  "document_type": "handwritten"
}

# Extract structured Q&A pairs
POST /ocr/extract_answers
{
  "ocr_text": "Question 1: What is AI? Answer: Artificial Intelligence",
  "expected_questions": ["What is AI?"]
}

# Analytics and reporting
GET /analytics/student/{student_id}?days=30
GET /analytics/class/{exam_id}
GET /analytics/system
```

### 🧪 Testing the AI System

Run comprehensive tests for all AI components:

```bash
# Test the complete AI grading system
python test_grading_system.py

# Test specific components
python -m unittest test_grading_system.TestOCRModule
python -m unittest test_grading_system.TestGradingEngine
python -m unittest test_grading_system.TestFeedbackGenerator
python -m unittest test_grading_system.TestHumanVerification
```

---

## 📄 License

This project is licensed under the [Custom Software License](LICENSE).
