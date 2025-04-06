const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = import.meta.env.VITE_GOOGLE_CLIENT_SECRET;
const GOOGLE_SCOPES = "https://www.googleapis.com/auth/classroom.courses.readonly https://www.googleapis.com/auth/classroom.coursework.me https://www.googleapis.com/auth/classroom.rosters.readonly https://www.googleapis.com/auth/forms https://www.googleapis.com/auth/forms.responses.readonly https://www.googleapis.com/auth/forms.body.readonly https://www.googleapis.com/auth/forms.body https://www.googleapis.com/auth/classroom.courseworkmaterials https://www.googleapis.com/auth/classroom.coursework.students https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets";
let oauthToken = null;
function loadGoogleAPI() {
    return new Promise((resolve, reject) => {
        if (typeof google !== "undefined") {
            resolve(google);
        } else {
            const script = document.createElement("script");
            script.src = "https://apis.google.com/js/api.js";
            script.async = true;
            script.defer = true;
            script.onload = () => resolve(google);
            script.onerror = () => reject("Google API failed to load");
            document.head.appendChild(script);
        }
    });
}
async function onSignIn(googleUser) {
    const profile = googleUser.getBasicProfile();
    const idToken = googleUser.getAuthResponse().id_token;
    sessionStorage.setItem("oauth_token", idToken);
    window.location.replace("dashboard.html");
}

loadGoogleAPI().then(() => {
    console.log("✅ Google API Loaded");
}).catch(err => console.error("❌ Error Loading Google API:", err));

document.addEventListener("DOMContentLoaded", function () {
    const loginPage = document.getElementById("loginPage");
    const classroomOptions = document.getElementById("classroomOptions");
    const enterCodePage = document.getElementById("enterCodePage");
    const enterCodeBtn = document.getElementById("enterCode");
    const createClassBtn = document.getElementById("createClass");
    const addClassroomBtn = document.getElementById("addClassroom");
    const gSignIn = document.getElementById("gSignIn");
    const classroomCodeInput = document.getElementById("classroomCodeInput");

    function showPage(show, hide) {
        hide.classList.add("hidden");
        setTimeout(() => {
            hide.style.display = "none";
            show.style.display = "block";
            setTimeout(() => show.classList.remove("hidden"), 50);
        }, 400);
    }
    //Handle Google Sign-In Response
    window.handleCredentialResponse = async (response) => {
        console.log("User signed in!");
        if (!response.credential) {
            console.error("❌ No credential received.");
            return;
        }
        sessionStorage.setItem("google_credential", response.credential);
        console.log("ID Token stored.");
        //Use OAuth token client to get access token
        initOAuthClient();
        tokenClient.requestAccessToken({ prompt: "consent" });
    };

    async function exchangeJWTForOAuth(idToken) {
        try {
            const response = await fetch("https://oauth2.googleapis.com/token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({
                    client_id: GOOGLE_CLIENT_ID,
                    client_secret: GOOGLE_CLIENT_SECRET,
                    grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    assertion: idToken,
                }),
            });
            const data = await response.json();
            if (!response.ok) {
                console.error("❌ OAuth token exchange failed:", data);
                return null;
            }
            return data.access_token; //Return the OAuth access token
        } catch (error) {
            console.error("❌ Error exchanging JWT for OAuth:", error);
            return null;
        }
    }
    let tokenClient;
function initOAuthClient() {
    if (!tokenClient) {
        tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            client_secret: GOOGLE_CLIENT_SECRET, // Include client secret
            scope: GOOGLE_SCOPES,
            callback: (response) => {
                if (response.access_token) {
                    sessionStorage.setItem("oauth_token", response.access_token);
                    console.log("✅ OAuth Token stored");
                    showPage(classroomOptions, loginPage);
                } else {
                    console.error("❌ Failed to get OAuth token.");
                }
            },
        });
    }
    
}
    //  Check if Already Signed In
    const storedToken = sessionStorage.getItem("oauth_token");
    if (storedToken) {
        oauthToken = storedToken;
        showPage(classroomOptions, loginPage);
    }
    //  Initialize Google Sign-In
    if (GOOGLE_CLIENT_ID) {
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleCredentialResponse,
            auto_select: true, // Auto sign-in for returning users
        });
        google.accounts.id.renderButton(gSignIn, { theme: "outline", size: "large" });
        google.accounts.id.prompt();
    } else {
        console.error("❌ Google Client ID is missing!");
    }
    enterCodeBtn.addEventListener("click", () => showPage(enterCodePage, classroomOptions));
    createClassBtn.addEventListener("click", () => {window.open("https://classroom.google.com/", "_blank");});
    addClassroomBtn.addEventListener("click", () => {
        const classroomCode = classroomCodeInput.value.trim();
        if (!classroomCode) {
            alert("Please enter a valid classroom code.");
            return;
        }
        sessionStorage.setItem("classroom_code", classroomCode);
        window.location.href = "dashboard.html";
    });
});

document.getElementById("logout").addEventListener("click", function ()
{
    sessionStorage.clear();
    window.location.href = "index.html";
});

history.pushState(null, null, location.href);
window.onpopstate = function () {   history.pushState(null, null, location.href); };


