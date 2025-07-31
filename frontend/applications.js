document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const jobId = urlParams.get("job_id");

  if (!jobId) {
    alert("Job ID missing in URL");
    return;
  }

  fetch("http://192.168.145.78:5000/jobapplications", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ job_id: jobId })
  })
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("applicantsContainer");
      const screenButtonContainer = document.getElementById("screenButtonContainer");

      container.innerHTML = "";

      if (!data.applications || !Array.isArray(data.applications)) {
        console.error("Invalid response format:", data);
        container.innerHTML = "<p>No applicants found or invalid response.</p>";
        return;
      }

      // Show screen button if more than 1 applicant
      if (data.applications.length > 1) {
        const screenBtn = document.createElement("button");
        screenBtn.textContent = "Screen Applications";
        screenBtn.style.padding = "8px 16px";
        screenBtn.style.backgroundColor = "#4CAF50";
        screenBtn.style.color = "white";
        screenBtn.style.border = "none";
        screenBtn.style.borderRadius = "4px";
        screenBtn.style.cursor = "pointer";

        screenBtn.onclick = () => {
          const placeholder = document.createElement("p");
          placeholder.textContent = "Screening in progress...";
          screenButtonContainer.replaceChild(placeholder, screenBtn);

          fetch(`http://192.168.145.78:5000/resumescreening/${jobId}`)

            .then(res => res.json())
            .then(result => {
              console.log("Screening result:", result);
              placeholder.textContent = "Screening complete! Redirecting...";
              setTimeout(() => {
                window.location.href = `screen.html?job_id=${jobId}`;
              }, 1000);
            })
            .catch(err => {
              console.error("Error during screening:", err);
              placeholder.textContent = "Error during screening. Try again.";
            });
        };

        screenButtonContainer.appendChild(screenBtn);
      }

      data.applications.forEach(applicant => {
        const div = document.createElement("div");
        div.innerHTML = `
          <p><strong>Name:</strong> ${applicant.name}</p>
          <p><strong>Resume:</strong> <a href="${applicant.resume_link}" target="_blank">View</a></p>
          <hr>
        `;
        container.appendChild(div);
      });
    })
    .catch(err => {
      console.error("Error fetching applicants:", err);
    });
});
