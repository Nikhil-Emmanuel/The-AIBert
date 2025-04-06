# 📚 The AIBert - The Teacher's Friend 🚀

This project is a modern, AI-integrated web application with a smooth and professional interface for teachers and educators. It enables effortless interaction with Google Classroom, Google Forms and Google Sheets to generate quizzes, collect responses, evaluate them using Google's Gemini Generative AI model, and provide individual feedback - All these at the tip of your fingertips ! 

---

## 🛠️ Features

- 🔐 Google Sign-In authentication
- 🧑‍🏫 Connect and manage Google Classroom using OAuth
- 🧠 Google Gemini-powered quiz generation & evaluation
- 📋 Auto-create Google Forms with questions
- 🤖 Evaluate answers with Google Generative AI
- 📄 Fetch, analyze, and store student responses
- 📊 Score calculation & detailed feedback per student
- 📈 Export feedback and scores to Google Sheets
- 🌐 Deployed using Vite + Amazon Web Service (AWS)
- 💾 MongoDB integration for activity logs and recovery

---

## 📁 Directory Structure

```
📁 Root Directory
├── 📁 assets/             # Contains all images and icons for UI
├── 📁 idx/                # (IDX workspace and environment files)
├── 📁 .vscode/            # VSCode settings
├── .gitignore             # Ignore sensitive files like .env
├── package.json           # Project dependencies and scripts
├── server.js              # Backend server handling endpoint APIs & OAuth
├── .env                   # Your API keys (NOT COMMITTED)
│
├── index.html             # Login page with Google Sign-In
├── index.css              # Styling for index.html
├── main.js                # Handles login/auth logic
│
├── dashboard.html         # Main dashboard after login
├── dashboard.css          # Styling for the dashboard
├── dashboard.js           # Fetches students, activities and user action controls
│
├── chatbot.html           # AI-based quiz generation interface
├── chatbot.css            # Styling for chatbot page
├── chatbot.js             # Invokes Gemini models and handles form creation
│
├── grades.html            # Shows student grades & feedback
├── grades.css             # Styling for grades
├── grades.js              # Fetches and renders grades
│
├── result.html            # View exported sheets and question topic
├── result.css             # Styling for results
├── result.js              # Displays list of exported sheets with timestamps
│
├── gemini.js              # Core Gemini API logic for prompting, feedback & question generation
├── mobile.css             # Responsive styles for smaller screens
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

### 3. **Create a `.env` file**

Create a `.env` in the **root directory** and add your sensitive credentials:

```env
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
MONGODB_URI=your_mongodb_connection_string
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_GOOGLE_CLASSROOM_API_KEY=your_google_api_key (if needed)
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

## 🔮 Future Improvements 
- Will be able to grade paper manuscripts
- Upload pictures, PDFs, texts,etc
- Enabling text recognition using OCR technologies
- Further easing the burden on teachers by assisting in grading and feedbacks

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
