import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import { evaluateAnswer } from "./gemini.js"; 
import { google } from "googleapis";
import fetch from "node-fetch";
dotenv.config();
const app = express();
const PORT = process.env.PORT || 3000;
app.use(cors({
    origin: "*",
    methods: "GET,POST",
    allowedHeaders: "Content-Type"
}));
app.use(express.json());

mongoose.connect(process.env.MONGO_URI, {  // Connect to MongoDB
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log("✅ MongoDB Connected"))
  .catch(err => console.error("🚨 MongoDB Connection Error:", err));

const activitySchema = new mongoose.Schema({  //MongoDB Schema & Model
    topic: String,
    activity: String,    
    timestamp: String,    
    formLink: String,       
    graded: { type: Boolean, default: false }
});
const Activity = mongoose.model("Activity", activitySchema);

app.post("/log_activity", async (req, res) => {
    try {
        const newActivity = new Activity(req.body);
        await newActivity.save();
        res.json({ message: "Activity logged successfully!" });
    } catch (error) {
        console.error("🚨 Error saving activity:", error);
        res.status(500).json({ error: "Failed to log activity" });
    }
});

app.get("/recent_activities", async (req, res) => {
    try {
        const activities = await Activity.find().sort({ _id: -1 }).limit(10);
        res.json(activities);
    } catch (error) {
        console.error("🚨 Error retrieving activities:", error);
        res.status(500).json({ error: "Failed to fetch activities" });
    }
});
const saveSchema = new mongoose.Schema({
    topic: String,
    questions: [String],
    answers: [String],
    formUrl: String,
    timestamp: { type: Date, default: Date.now },
    sheetUrl: String
});
const Answers = mongoose.model("Answers", saveSchema);

app.post("/save-activity", async (req, res) => {
    try {
        const { topic, questions, answers, formUrl} = req.body;
        const newActivity = new Answers({ topic, questions, answers, formUrl });
        await newActivity.save();
        res.status(201).json({ message: "Activity saved successfully!" });
        } 
        catch (error) 
        {res.status(500).json({ error: "Failed to save activity." });}
});

app.get("/getForms", async (req, res) => {
    const forms = await Activity.find();
    res.json(forms);
});
app.post("/gradeForm", async (req, res) => 
    {
        try {
                const { formId, formLink, accessToken } = req.body;
                if (!accessToken) return res.status(401).json({ success: false, message: "Unauthorized" });
                const responses = await fetchGoogleFormResponses(formLink, accessToken);
                if (!responses || responses.length === 0) 
                    {return res.status(400).json({ success: false, message: "No responses found." }); }
                const answerDoc = await Answers.findOne({ formUrl: formLink });
                if (!answerDoc) {console.log("Error fetching document from MongoDB.");}
                const correctAnswersMap = {};
                for (let i = 0; i < answerDoc.questions.length; i++) 
                {
                    const questionText = answerDoc.questions[i].trim(); 
                    const correctAnswer = answerDoc.answers[i].trim();    
                    correctAnswersMap[questionText] = correctAnswer;    
                }
                const feedbacks = {};  // Format : { studentName: [ { question, studentAnswer, correctAnswer, score, feedback } ] }
                let totalScore = 0;
                for (let response of responses) 
                {
                    const studentName = response.studentName;
                    const questionAsked = response.question.trim();
                    const studentAnswer = response.answer.trim();
                    const correctAnswer = correctAnswersMap[questionAsked] || "NA";
                    const feedback = await evaluateAnswer(questionAsked, studentAnswer, correctAnswer);// Using Gemini 1.5 
                    if (!feedbacks[studentName]) 
                        {feedbacks[studentName] = [];}
                    feedbacks[studentName].push({
                        question: questionAsked,
                        studentAnswer,
                        correctAnswer,
                        score: feedback.score,
                        feedback: feedback.feedback,
                        recommendation: feedback.recommendations
                    });
                    totalScore += feedback.score;
                }
                const maxScore = responses.length * 50;
                const finalScore = ((totalScore / maxScore) * 50).toFixed(1);
                await updateGoogleSheet(accessToken, feedbacks, formLink);  //Update results to Google Sheets
                await Activity.findByIdAndUpdate(formId, { graded: true }); //Set grade=true in MongoDB
                res.json({ success: true, message: "Form graded successfully.", finalScore });
            } 
        catch (error) 
            {
            console.error("Error grading form:", error);res.status(500).json({ success: false, message: "Internal server error." });
            }
    });

app.get("/getResults", async (req, res) => 
    {
        try 
        {
            const latestAnswer = await Answers.findOne({ sheetUrl: { $exists: true } }).sort({ timestamp: -1 });
            if (!latestAnswer) 
                {return res.status(404).json({ success: false, message: "No graded feedback found." });}
            res.json({
                success: true,
                timestamp: latestAnswer.timestamp,
                topic: latestAnswer.topic,
                sheetLink: latestAnswer.sheetUrl
            });
        }
        catch (error) 
        {
            console.error("Error fetching latest feedback:", error);
            res.status(500).json({ success: false, message: "Internal server error." });
        }
  });

function extractFormId(formLink) 
{
    const match = formLink.match(/\/d\/([^/]+)/);
    return match ? match[1] : null;
}

async function fetchGoogleFormResponses(formLink, accessToken)
{
    const formId = extractFormId(formLink);
    try {
        const response = await fetch(`https://forms.googleapis.com/v1/forms/${formId}/responses`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${accessToken}`,
                "Content-Type": "application/json"
            }
        });
        const formMetadata = await fetch(`https://forms.googleapis.com/v1/forms/${formId}`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`Error fetching form responses: ${response.statusText}`);
        }
        const data = await response.json();
        const questionData = await formMetadata.json();
        if (!data.responses || data.responses.length === 0) 
            {return [];}
        const questionIdMap = {};
        questionData.items.forEach(item => {
            const id = item.questionItem?.question?.questionId;
            const text = item.title;
            if (id && text) {
                questionIdMap[id] = text;
            }
        });
        const parsedResponses = data.responses.map(res => {
            const answers = res.answers;
            let studentName = "N/A"; 
            //Extract "Student Name"
            for (const [questionId, answerData] of Object.entries(answers)) 
                {
                    const questionText = questionIdMap[questionId] || questionId;
                    const studentAnswer = answerData?.textAnswers?.answers?.[0]?.value || "No answer provided";
                    if (questionText.trim().toLowerCase() === "student name") 
                        {studentName = studentAnswer.trim();break;}
                }
            return Object.entries(answers).map(([questionId, answerData]) => {
                const questionText = questionIdMap[questionId] || questionId;
                const studentAnswer = answerData?.textAnswers?.answers?.[0]?.value || "No answer provided";
                if (questionText.trim().toLowerCase() === "student name") return null;// Skip "Student Name"
                return{
                    studentName,
                    question: questionText.trim(),
                    answer: studentAnswer.trim()
                };
            }).filter(Boolean);
        }).flat();
        return parsedResponses;
        }
        catch (error)
        { console.error("Error fetching Google Form responses:", error);return []; }
}

export async function updateGoogleSheet(accessToken, feedbacksByStudent, formLink)
{
    try 
    {
        const auth = new google.auth.OAuth2();
        auth.setCredentials({ access_token: accessToken });
        const drive = google.drive({ version: "v3", auth });
        const fileMetadata = {      //Creating a new Google Sheet File
            name: "Graded Responses",
            mimeType: "application/vnd.google-apps.spreadsheet",
        };
        const file = await drive.files.create({
            resource: fileMetadata,
            fields: "id, webViewLink",
        });
        const spreadsheetId = file.data.id;
        const sheets = google.sheets({ version: "v4", auth });
        for (const studentName in feedbacksByStudent)   //For each student, create a sheet and insert their feedback
            { 
                const sheetTitle = studentName.substring(0, 100);
                await sheets.spreadsheets.batchUpdate({
                    spreadsheetId,
                    requestBody: {
                        requests: [{
                            addSheet: {
                                properties: {
                                    title: sheetTitle
                                }
                            }
                        }]
                    }
                });
                const studentEntries = feedbacksByStudent[studentName];
                const totalScore = studentEntries.reduce((acc, entry) => acc + (entry.score || 0), 0);
                const finalStudentScore = totalScore.toFixed(1);
                const rows = [
                    ["Question", "Student Answer", "Correct Answer", "Score (out of 50)", "Feedback"],
                    ...studentEntries.map(entry => [
                    String(entry.question ?? "Nil"),
                    String(entry.studentAnswer ?? "Nil"),
                    String(entry.correctAnswer ?? "Nil"),
                    typeof entry.score === "number" ? entry.score.toFixed(1) : "0.0",
                    String(entry.feedback ?? "No feedback"),
                    ]),
                    ["Final Score", finalStudentScore]
                ];
                await sheets.spreadsheets.values.update({
                    spreadsheetId,
                    range: `${sheetTitle}!A1`,
                    valueInputOption: "RAW",
                    requestBody: { values: rows }
                });
            }
        await Answers.findOneAndUpdate(
            { formUrl: formLink }, // Find by formUrl
            { $set: { sheetUrl: file.data.webViewLink } }, // Only update sheetUrl
            { new: true } // Return the updated document (optional)
        );
    }
    catch(error)
    {console.error("❌ Error updating Google Sheet:", error);throw error;}
}

app.listen(PORT, () => console.log(`✅ Server running on http://localhost:${PORT}`));