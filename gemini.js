import dotenv from "dotenv";
dotenv.config();
const GEMINI_KEY = process.env.VITE_GEMINI_API_KEY;
import { GoogleGenerativeAI } from "@google/generative-ai";
const genAI = new GoogleGenerativeAI(GEMINI_KEY);
export async function evaluateAnswer(question, studentAnswer, correctAnswer) {
    try {
        const prompt = `
        Question: ${question}
        Student's Answer: ${studentAnswer}
        Correct Answer: ${correctAnswer}

        Evaluate the student's answer based on correctness and clarity like a good teacher using the context of given question and correct answer. Provide:
        - A final score out of 50 after grading all answers.
        - Concise Feedback about the student answer within 30 words.
        - Precise Recommendations for improvement and better answers within 30 words.

        Format the response exactly like this and avoid headers, only give the points:
        Score: <numeric score>
        Feedback: <feedback>
        Recommendations: <recommendations>
        `;
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        const scoreMatch = responseText.match(/Score:\s*(\d+(\.\d+)?)/i);console.log(scoreMatch);
        const feedbackMatch = responseText.match(/Feedback:\s*([\s\S]*)/i);console.log("Feedback:",feedbackMatch);
        const recommendationMatch = responseText.match(/Recommendations:\s*([\s\S]*)/i);console.log("Recommendations:",recommendationMatch);

        const score = scoreMatch ? parseFloat(scoreMatch[1]) : 0;
        const feedback = feedbackMatch ? feedbackMatch[1].trim() : "No feedback.";
        const recommendations = recommendationMatch ? recommendationMatch[1].trim() : "No recommendations.";
        return {
            score: Math.min(score, 50), // Ensure max score is 50
            feedback: `${feedback}`,
            recommendations:`${recommendations}`
        };
    } catch (error) {
        console.error("Error evaluating answer with Gemini:", error);
        return {
            score: 0,
            feedback: "An error occurred while evaluating the answer."
        };
    }
}