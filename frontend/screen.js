// document.addEventListener("DOMContentLoaded", () => {
//   const jobId = new URLSearchParams(window.location.search).get("job_id");
//   const screenBtn = document.getElementById("screenBtn");

//   if (!jobId) {
//     alert("Job ID missing");
//     return;
//   }

//   fetch(`http://192.168.145.78:5000/get_applicants/${jobId}`)
//     .then((res) => res.json())
//     .then((data) => {
//       if (!Array.isArray(data)) {
//         throw new Error("Invalid response format");
//       }

//       const container = document.getElementById("applicationsContainer");
//       container.innerHTML = "";

//       data.forEach((applicant) => {
//         const div = document.createElement("div");
//         div.textContent = `${applicant.name} (${applicant.email})`;
//         container.appendChild(div);
//       });

//       if (data.length > 1) {
//         screenBtn.style.display = "inline-block";
//         screenBtn.onclick = () => {
//           fetch(`http://192.168.145.78:5000/resumescreening${jobId}`)
//             .then((res) => res.json())
//             .then((result) => {
//               console.log("Screening result:", result);
//               window.location.href = `screen.html?job_id=${jobId}`;
//             })
//             .catch((err) => {
//               console.error("Error during screening:", err);
//             });
//         };
//       }
//     })
//     .catch((err) => {
//       console.error("Error fetching applicants:", err);
//     });
// });


document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const jobId = urlParams.get("job_id");
  console.log(jobId);
  const loadingDiv = document.getElementById("loading");
  const errorMessageDiv = document.getElementById("errorMessage");
  const container = document.getElementById("screenedResults");

  if (!jobId) {
    loadingDiv.innerText = "Error: Missing job ID in URL."; // More user-friendly
    errorMessageDiv.innerText = "Please provide a job ID in the URL (e.g., ?job_id=123).";
    errorMessageDiv.style.display = "block";
    return;
  }

  
  const apiUrl = `http://192.168.145.78:5000/resumescreening/${jobId}`;

  fetch(apiUrl)
    .then(res => {
      if (!res.ok) {
        // Handle HTTP errors (e.g., 404, 500)
        return res.json().then(errData => {
          throw new Error(errData.error || `HTTP error! Status: ${res.status}`);
        });
      }
      return res.json();
    })
    .then(data => {
      console.log("Fetched data:", data);

      if (!Array.isArray(data) || data.length === 0) {
        loadingDiv.innerText = "No screening results found.";
        return;
      }

      // Sort by overall_score in descending order
      data.sort((a, b) => {
        const scoreA = parseFloat(a.overall_score || 0);
        const scoreB = parseFloat(b.overall_score || 0);
        return scoreB - scoreA;
      });

      // Assign ranks based on sorted order
      data.forEach((applicant, index) => {
        applicant.rank = index + 1;
      });

      const table = document.createElement("table");
      const thead = document.createElement("thead");
      thead.innerHTML = `
        <tr>
          <th>Rank</th>
          <th>Name</th>
          <th>Degree</th>
          <th>Experience</th>
          <th>JD Match %</th>
          <th>Score</th>
          <th>Location</th>
          <th>Matched Keywords</th>
          <th>Resume</th>
        </tr>
      `;
      table.appendChild(thead);

      const tbody = document.createElement("tbody");

      data.forEach(applicant => {
        const tr = document.createElement("tr");

        // Ensure MatchingKeywords is an object before iterating
        const matchingKeywords = typeof applicant.MatchingKeywords === 'object' && applicant.MatchingKeywords !== null
          ? applicant.MatchingKeywords
          : {};

        const keywordsFormatted = Object.entries(matchingKeywords)
          .map(([k, v]) => `${k}: ${v}`)
          .join(", ");

        const resumeLink = applicant.resume_link || `/resumes/${applicant.filename}`;


        tr.innerHTML = `
          <td>${applicant.rank}</td>
          <td>${applicant.name || 'N/A'}</td>
          <td>${applicant.degree || 'N/A'}</td>
          <td>${applicant.experience_year || '0'} years</td>
          <td>${applicant.JDMatch || '0'}</td>
          <td>${applicant.overall_score || '0'}</td>
          <td>${applicant.location || 'N/A'}</td>
          <td>${keywordsFormatted || 'None'}</td>
          <td>${applicant.filename ? `<a href="${resumeLink}" target="_blank">View PDF</a>` : 'N/A'}</td>
        `;

        tbody.appendChild(tr);
      });

      table.appendChild(tbody);
      container.innerHTML = ""; // Clear any previous content
      container.appendChild(table);

      loadingDiv.style.display = "none";
      container.style.display = "block";
    })
    .catch(err => {
      console.error("Error loading screening results:", err);
      loadingDiv.style.display = "none"; // Hide loading message
      errorMessageDiv.innerText = `Error loading screening results: ${err.message || err}. Please try again.`;
      errorMessageDiv.style.display = "block"; // Show error message
      container.style.display = "none"; // Ensure table is hidden
    });
});