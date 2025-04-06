# 📚 The AIBert - The Teacher's Friend 🚀

This project is a modern, AI-integrated web application with a smooth and professional interface for teachers and educators. It enables effortless interaction with Google Classroom, Google Forms and Google Sheets to generate quizzes, collect responses, evaluate them using Google's Gemini Generative AI model, and provide individual feedback - All these at the tip of your fingertips ! 

---

## 🛠️ Features

- 🔐 Google Sign-In authentication
- 🧑‍🏫 Connect and manage Google Classroom using OAuth
- 🧠 Gemini AI-powered quiz generation & evaluation
- 📋 Auto-create Google Forms with questions 
- 📄 Fetch, analyze, and store student responses
- 📊 Score calculation & detailed feedback per student
- 📈 Export feedback and scores to Google Sheets
- 🌐 Deployed using Vite + Amazon Web Service (AWS)
- 💾 MongoDB integration for activity logs and recovery

---

## 📁 Directory Structure

```
📁 Root Directory
├── 📁 assets/             # Contains all images and icons
├── 📁 idx/                # (IDX workspace files, not required for deploy)
├── 📁 .vscode/            # VSCode settings
├── .gitignore             # Ignore sensitive files like .env
├── package.json           # Project dependencies and scripts
├── server.js              # Backend server handling APIs & OAuth
├── .env                   # Your API keys (NOT COMMITTED)
│
├── index.html             # Login page with Google Sign-In
├── index.css              # Styling for index.html
├── main.js                # Handles login/auth logic
│
├── dashboard.html         # Main dashboard after login
├── dashboard.css          # Styling for the dashboard
├── dashboard.js           # Fetches students, activities, and test controls
│
├── chatbot.html           # AI-based quiz generation interface
├── chatbot.css            # Styling for chatbot page
├── chatbot.js             # Calls Gemini and handles form creation
│
├── grades.html            # Shows student grades & feedback
├── grades.css             # Styling for grades
├── grades.js              # Fetches and renders grades
│
├── result.html            # View exported sheets and topic logs
├── result.css             # Styling for results
├── result.js              # Displays list of exported sheets with timestamps
│
├── gemini.js              # Core Gemini API logic for feedback & question generation
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

### 5. **🚀 Deployment on AWS EC2**
- This project can be easily deployed to an AWS EC2 instance:
- Host both the Vite frontend and Node.js backend (server.js).
- Clone the repo on your EC2 instance and bash ``` run npm install && npm run build```.
- Use PM2 to run the backend (server.js) persistently.
- Use Nginx as a reverse proxy to serve the Vite build (```dist/```) and forward ```/api``` calls to your Node.js server.
- Environment variables (like ```MONGO_URI, GOOGLE_CLIENT_ID```) are securely stored in a .env file in the root directory — it’s ignored from Git via .gitignore.

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
| `server.js`        | Backend logic: OAuth, DB, Forms, Sheets |
| `package.json`     | Lists dependencies like `googleapis`, `vite`, `generativeAI` |
| `.env`             | Keeps sensitive API keys secure |
| `assets/`          | Contains images used in UI |
| `mobile.css`       | Makes the site responsive for mobile device screens |

---

## ☁️ Cloud Services Used

- **Google's Project IDX** for code development and testing
- **Google OAuth 2.0** for authentication
- **Google Classroom API** for accessing existing class and student interaction
- **Google Forms API** to auto-create quizzes and extract responses
- **Google Sheets API** to export results
- **Gemini API (Google Generative AI)** for evaluation and question generation
- **MongoDB Atlas** for storing responses & logs

---

## 🧪 Sample Usage Flow

1. Teacher login using Google Sign-In on `index.html`.
2. Enter or create a Google Classroom.
3. Navigate to the chatbot, generate a quiz, and post it.
4. Students respond via the Google Form.
5. Teacher clicks "Grade" to get Gemini feedback.
6. View results and scores in `grades.html`.
7. Export them to Google Sheets and view via `result.html`.

---

## 🛡️ Security Tips

- Never expose your `.env` file
- Use `.gitignore` to exclude sensitive files
- Always use HTTPS when deployed

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
