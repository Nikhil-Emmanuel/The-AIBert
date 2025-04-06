import { GoogleGenerativeAI } from "@google/generative-ai";
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const OAUTH_TOKEN = sessionStorage.getItem("oauth_token");
var topic1,formatTopic,ques,ans;
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
async function generateQuestions() {
    const topicInput = document.getElementById("promptInput");
    const responseContainer = document.getElementById("responseContainer");
    const createFormBtn = document.getElementById("createFormBtn");
    const topic = topicInput.value.trim();
    topic1 = topic; // To reference topic name outside this scope
    topic1 = topic1.replace(/\b\w/g, char => char.toUpperCase());
    if (!topic) {
        alert("❌ Please enter a topic!");
        return;
    }
    const prompt = `You are an expert in academic and research. Based on the topic "${topic}", create a set of questions suitable for mentioned students. Do not include any description, only give the questions.`;
    try {
        responseContainer.innerHTML = "<li>⏳ Generating questions, please wait...</li>";
        createFormBtn.style.display = "none"; // Hide form button while loading
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = await response.text(); // Await the text response
        const questions = text.split("\n").filter(q => q.trim() !== "");
        displayQuestions(text); // Call function to display the questions
        const answerPrompt = `Provide accurate and concise answers to the following questions based on the given class without any topic or description. Give only the answers:\n${questions.join("\n")}`;
        const answerResult = await model.generateContent(answerPrompt);
        const answerResponse = await answerResult.response;
        const answersText = await answerResponse.text();
        const answers = answersText.split("\n").filter(a => a.trim() !== "");
        ques = questions;     //Store in MongoDB
        ans = answers;
        } 
    catch (error) 
    {
        console.error("🚨 Error generating questions:", error);
        responseContainer.innerHTML = "<li>❌ Failed to generate questions. Please try again.</li>";
    }
}
async function saveToDatabase(topic, questions, answers, formUrl) {
    try {
        const response = await fetch("https://localhost:3000/save-activity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic, questions, answers, formUrl })
        });
        if (!response.ok) throw new Error("Failed to save data.");
        console.log("✅ Questions & answers saved successfully.");
    } catch (error) {
        console.error("❌ Error saving to database:", error);
    }
}

function displayQuestions(text) {
    const responseContainer = document.getElementById("responseContainer");
    const responseSection = document.getElementById("responseSection");
    responseContainer.innerHTML = ""; // Clear previous questions
    const questions = text.split("\n").filter(q => q.trim() !== "");
    if (questions.length === 0) {
        responseContainer.innerHTML = "<li>⚠ No questions generated. Try again.</li>";
        return;
    }
    responseContainer.style.listStyleType = "none"; // Remove default numbering
    questions.forEach(question => {                 // Display each question as a numbered list
        const listItem = document.createElement("li");
        listItem.textContent = question;
        responseContainer.appendChild(listItem);
    });
    responseSection.style.display = "block"; // Make the section visible
    document.getElementById("createFormBtn").style.display = "block"; 
    const shouldScroll = window.innerHeight + window.scrollY >= document.body.offsetHeight - 50;
    if (shouldScroll) {
        responseContainer.scrollIntoView({ behavior: "smooth", block: "end" });
    }
}

document.getElementById("createFormBtn").addEventListener("click", function () {
    const button = this;
    button.disabled = true;
    button.style.opacity = "0.6";
    button.style.cursor = "not-allowed";
    setTimeout(() => {
        button.disabled = false;
        button.style.opacity = "1";
        button.style.cursor = "pointer";
    }, 7000); // 7 seconds wait time to create the form
});

async function createGoogleForm() {
    if (!OAUTH_TOKEN) {
        alert("User not authenticated. Please sign in again.");
        return;
    }
    const questions = [...document.querySelectorAll("#responseContainer li")].map(li => li.textContent);
    if (questions.length === 0) {
        alert("No questions available to create a form.");
        return;
    }
    try {
        // Create new Google Form
        const formResponse = await fetch("https://forms.googleapis.com/v1/forms", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${OAUTH_TOKEN}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                info: {
                    title: `AI Quiz on ${topic1}`  // ✅ ONLY 'title' is allowed
                }
            }),
        });
        if (!formResponse.ok) {
            const errorResponse = await formResponse.json();
            console.error("🚨 Form Creation Error:", errorResponse);
            throw new Error("Failed to create form.");
        }
        const formData = await formResponse.json();
        const formId = formData.formId;
        // Add Questions to the Form with Proper Format
        const updateResponse = await fetch(`https://forms.googleapis.com/v1/forms/${formId}:batchUpdate`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${OAUTH_TOKEN}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                requests: [
                    // Add "Student Name" short answer question first
                    {
                        createItem: {
                            item: {
                                title: "Student Name",
                                questionItem: {
                                    question: {
                                        required: true,
                                        textQuestion: { paragraph: false } // Short answer
                                    }
                                }
                            },
                            location: { index: 0 }
                        }
                    },
                    ...questions.map((question, index) => ({
                        createItem: {
                            item: {
                                title: `${question}`,
                                questionItem: {
                                    question: {
                                        required: true,
                                        textQuestion: { paragraph: true }
                                    }
                                }
                            },
                            location: { index: index + 1 } // Since index=0 is Student Name
                        }
                    }))
                ]
            }),
        });
        if (!updateResponse.ok) throw new Error("Failed to add questions.");
        const formUrl = `https://docs.google.com/forms/d/${formId}/edit`;  //Redirect User to the Form for any corrections
        window.open(formUrl, "_blank");
        postToGoogleClassroom(formUrl);   // Post Form as Google Classroom Assignment
    } catch (error) {
        console.error("Error creating Google Form:", error);
    }
}

async function postToGoogleClassroom(formUrl) {
    const classCode = sessionStorage.getItem("classroom_code");
    if (!classCode) {
        alert("No Classroom Enrollment Code found. Please enter a valid code.");
        return;
    }
    try 
    {
        await saveToDatabase(topic1, ques, ans, formUrl);
        const OAUTH_TOKEN = sessionStorage.getItem("oauth_token");
        //Fetch Course ID from Enrollment Code
        const coursesResponse = await fetch("https://classroom.googleapis.com/v1/courses", {
            method: "GET",
            headers: { "Authorization": `Bearer ${OAUTH_TOKEN}` }
        });
        const coursesData = await coursesResponse.json();
        if (!coursesData.courses) {
            throw new Error("No courses found for this user.");
        }
        //Find Course ID matching the Enrollment Code
        const course = coursesData.courses.find(c => c.enrollmentCode === classCode);
        if (!course) {
            throw new Error("No course found with the provided enrollment code.");
        }
        const courseId = course.id;
        //Post Assignment to the Classroom
        const now = new Date();
        const dueDateTime = new Date(now.getTime() + 24 * 60 * 60 * 1000); // Add 24 hours due date
        const courseworkPayload = {
            title: `Quiz Assignment on ${topic1}`,
            description: "Complete the quiz using the form link below.",
            materials: [{ link: { url: formUrl } }],
            workType: "ASSIGNMENT",
            state: "PUBLISHED",
            dueDate: { 
                year: dueDateTime.getFullYear(), 
                month: dueDateTime.getMonth() + 1, 
                day: dueDateTime.getDate()
            },
            dueTime: { 
                hours: dueDateTime.getHours(), 
                minutes: dueDateTime.getMinutes(), 
                seconds: dueDateTime.getSeconds()
            }
        };
        const classroomResponse = await fetch(`https://classroom.googleapis.com/v1/courses/${courseId}/courseWork`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${OAUTH_TOKEN}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(courseworkPayload),
        });
        const responseData = await classroomResponse.json();
        if (!classroomResponse.ok) {
            console.error("🚨 Error posting to Google Classroom:");
            throw new Error(responseData.error.message);
        }
        console.log("✅ Form successfully posted to Classroom!");
        logActivity(topic1, `Created a Google Form assignment`,formUrl);
        alert("Assignment created and posted successfully! Redirecting to the AIBert dashboard...");
        window.location.href = "dashboard.html";
    }
    catch (error)
    {   console.error("Error posting to Google Classroom:", error); }
}

async function logActivity(topic,activity,formLink) {
    const timestamp = new Date().toISOString();
    const newEntry = { topic,activity,formLink, timestamp };
    try 
    {
        const response = await fetch("https://localhost:3000/log_activity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newEntry),
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        console.log("✅ Activity logged successfully!");
    }
    catch (error) 
    {      console.error("🚨 Error logging activity:", error);    }
}

document.getElementById("generateBtn").addEventListener("click", generateQuestions);
document.getElementById("createFormBtn").addEventListener("click", createGoogleForm);
document.getElementById("backToDashboard").addEventListener("click", () => {window.location.href = "dashboard.html";});

history.pushState(null, null, location.href);
window.onpopstate = function () {   history.pushState(null, null, location.href); };