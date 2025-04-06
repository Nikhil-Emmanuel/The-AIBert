async function fetchForms() {
    const response = await fetch("https://localhost:3000/getForms");
    const forms = await response.json();
    const formList = document.getElementById("formList");
    if (forms.length === 0) {  //For no data available
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="4" style="text-align:center; font-style:italic;">No data available</td>`;
        formList.appendChild(row);
        return;
    }
    formList.innerHTML = "";
        forms.forEach(form => {
        const row = document.createElement("tr");
        const formattedTimestamp = new Date(form.timestamp).toLocaleString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false // 24-hour format
        }).replace(',', ''); // Remove the comma from output
        row.innerHTML = `
            <td>${formattedTimestamp}</td>
            <td>${form.topic}</td>
            <td><a href="${form.formLink}" target="_blank">Open Form</a></td>
            <td>
                <button class="grade-btn" onclick="gradeForm('${form._id}', '${form.formLink}')" ${form.graded ? "disabled" : ""}>
                    ${form.graded ? "Done" : "Grade"}
                </button>
            </td> `;
        formList.appendChild(row);
    });
}

async function gradeForm(formId, formLink) {
    const accessToken = sessionStorage.getItem("oauth_token");
    const button = document.querySelector(`button[onclick="gradeForm('${formId}', '${formLink}')"]`);
    button.textContent = "Grading...";
    button.disabled = true;
    const response = await fetch("https://localhost:3000/gradeForm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ formId, formLink, accessToken })
    });
    
    const result = await response.json();
    if (result.success) {
        button.textContent = "Done";
        alert("Grading is Successful ! Redirecting to the AIBert dashboard...");
        window.location.href = "dashboard.html";
    } else {
        button.textContent = "Grade";
        button.disabled = false;
        alert("Error grading form.");
    }
}

document.addEventListener("DOMContentLoaded", () => {   fetchForms(); });
document.getElementById("backToDashboard").addEventListener("click", () => { window.location.href = "dashboard.html"; });