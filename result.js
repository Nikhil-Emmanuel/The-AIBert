document.addEventListener("DOMContentLoaded", async () => {
    const tableBody = document.getElementById("resultTableBody");
    try 
    {
      const res = await fetch("https://localhost:3000/getResults");
      const data = await res.json();
      if (!data.success) {
        throw new Error(data.message || "Could not fetch result.");
      }
      const { timestamp, topic, sheetLink } = data;
      const row = document.createElement("tr");
      row.innerHTML = 
      ` <td>${new Date(timestamp).toLocaleString()}</td>
        <td>${topic}</td>
        <td><button class="sheet-btn" onclick="window.open('${sheetLink}', '_blank')">View Sheet</button></td> `;

      tableBody.appendChild(row);
    } 
    catch (err) 
    {
      console.error("Error loading result:", err);
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="3">No graded data available. Please grade and try again later.</td>`;
      tableBody.appendChild(row);
    }
  });
  
  document.getElementById("backToDashboard").addEventListener("click", () => {
    window.location.href = "dashboard.html";
  });
  