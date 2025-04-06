async function fetchClassDetails() 
{
    const classCode = sessionStorage.getItem("classroom_code"); //Use sessionStorage
    const authToken = sessionStorage.getItem("oauth_token");    // Use sessionStorage

    if (!classCode) {
        console.error("Class code not found.");
        document.getElementById("className").textContent = "Class: Not Found";
        return;
    }
    if (!authToken) {
        console.error("Auth token missing.");
        document.getElementById("className").textContent = "Class: Authorization Required";
        return;
    }
    try {
        // Fetch all enrolled courses
        const coursesResponse = await fetch(
            `https://classroom.googleapis.com/v1/courses`,
            {
                method: "GET",
                headers: { Authorization: `Bearer ${authToken}` },
            }
        );
        if (!coursesResponse.ok) throw new Error("Failed to fetch courses");
        const coursesData = await coursesResponse.json();
        //Find the matching course based on classCode
        const matchedCourse = coursesData.courses.find(course => course.enrollmentCode === classCode);
        if (!matchedCourse) {
            console.error("No course found with that code.");
            document.getElementById("className").textContent = "Class: Not Found";
            return;
        }
        //Display the class name on the dashboard
        document.getElementById("className").textContent = `Class: ${matchedCourse.name}`;
    } catch (error) {
        console.error("Error fetching class name:", error);
        document.getElementById("className").textContent = "Class: Unknown";
    }
}
fetchClassDetails();

async function checkAndFetchStudents() 
{
    setTimeout(async () => {
        const oauthToken = sessionStorage.getItem("oauth_token");
        const classroomCode = sessionStorage.getItem("classroom_code");
        if (!oauthToken || !classroomCode) {
            console.error("Missing authentication details. Redirecting to login...");
            window.location.href = "index.html";
            return;
        }
        try 
        {
            // Convert Classroom Code to Course ID
            const courseId = await getCourseIdFromCode(oauthToken, classroomCode);
            if (!courseId) {
                alert("Invalid classroom code. Please enter a valid code.");
                sessionStorage.removeItem("classroom_code");
                window.location.href = "index.html";
                return;
            }
            // Fetch Students with Course ID
            await fetchClassStudents(oauthToken, courseId);
        }
        catch (error) 
        {
            console.error("Error fetching course ID:", error);
            window.location.href = "index.html";
        }
    }, 500);
}

async function loadRecentActivities() {
    try {
        const response = await fetch("https://localhost:3000/recent_activities", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            mode: "cors",
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const activities = await response.json();
        const activityContainer = document.getElementById("recent-activities");
        activityContainer.innerHTML = "";
        if (activities.length === 0) {
            activityContainer.innerHTML = "<p>No recent activities.</p>";
            return;
        }
        const activityList = document.createElement("ol"); // Numbered list
        activityList.style.textAlign = "left"; // Ensure left alignment
        activities.forEach(({ activity,topic, timestamp }, index) => {
            const activityItem = document.createElement("li");
            activityItem.classList.add("activity-item");
            activityItem.innerHTML = `<strong>${activity} on ${topic}</strong><br><small>${new Date(timestamp).toLocaleString()}</small>`;
            activityList.appendChild(activityItem);
        });
        activityContainer.appendChild(activityList);
        console.log("✅ Recent activities loaded successfully!");
    } catch (error) {
        console.error("🚨 Error loading activities:", error);
    }
}
document.addEventListener("DOMContentLoaded", loadRecentActivities);

async function getCourseIdFromCode(oauthToken, classroomCode) {
    try {
        const response = await fetch(`https://classroom.googleapis.com/v1/courses`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${oauthToken}`,
                Accept: "application/json",
            },
        });
        if (!response.ok) {
            console.error("Error fetching courses:", await response.json());
            return null;
        }
        const data = await response.json();
        if (!data.courses || data.courses.length === 0) {
            console.warn("No courses found for this user.");
            return null;
        }
        // Find the course that matches the provided classroom code
        const matchedCourse = data.courses.find(course => course.enrollmentCode === classroomCode);
        return matchedCourse ? matchedCourse.id : null;
    } catch (error) {
        console.error("Error retrieving course ID:", error);
        return null;
    }
}

async function fetchClassStudents(oauthToken, courseId) {
    try {
        const response = await fetch(`https://classroom.googleapis.com/v1/courses/${courseId}/students`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${oauthToken}`,
                Accept: "application/json",
            },
        });

        if (!response.ok) {
            console.error("Error fetching students:", await response.json());
            if (response.status === 401) {
                alert("Session expired. Please log in again.");
                sessionStorage.removeItem("oauth_token");
                window.location.href = "index.html";
            }
            return;
        }
        const data = await response.json();
        const classMembersList = document.getElementById("classMembersList");
        classMembersList.innerHTML = "";
        if (data.students?.length > 0) {
            data.students.forEach((student, index) => {
                const listItem = document.createElement("li");
                // Capitalize first letter of each word in the name
                const fullName = student.profile.name.fullName
                    .toLowerCase() // Convert to lowercase first
                    .split(" ") // Split into words
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize first letter
                    .join(" "); // Join back into a string
                listItem.textContent = `${fullName}`;
                classMembersList.appendChild(listItem);
            });
        } else {
            classMembersList.innerHTML = "<li>No students found.</li>";
        }
    } catch (error) {
        console.error("Error fetching students:", error);
    }
}
const logoutButton = document.getElementById("logout");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            sessionStorage.removeItem("oauth_token"); // Clear session token
            sessionStorage.removeItem("classroom_code"); // Clear classroom code
            window.location.href = "index.html"; // Redirect to login page
        });
    }
const test = document.getElementById("createTest");
const viewres = document.getElementById("viewResults");
const feedback = document.getElementById("viewFeedback");
if (test) {
    test.addEventListener("click", () => {
        window.location.href = "chatbot.html";
    })}
if (viewres) {
    viewres.addEventListener("click", () => {
    window.location.href = "grades.html";
    })}
if (feedback) {
    feedback.addEventListener("click", () => {
    window.location.href = "result.html";
    })}

document.addEventListener("DOMContentLoaded", checkAndFetchStudents);

history.pushState(null, null, location.href);
window.onpopstate = function () {history.pushState(null, null, location.href);};