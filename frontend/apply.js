document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const jobId = urlParams.get("job_id");
  const seekerId = urlParams.get("seeker_id");
  const secretCode = urlParams.get("secret_code");

  if (!jobId || !seekerId) {
    alert("Job ID or Seeker ID missing");
    return;
  }

  fetch(`http://192.168.145.78:5000/get_job_by_id/${jobId}`)
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch job details");
      return response.json();
    })
    .then(data => {
      document.getElementById("jobTitle").textContent = data.title;
      document.getElementById("jobDescription").textContent = data.job_description;
    })
    .catch(err => {
      console.error("Error fetching job:", err);
      alert("Could not load job details.");
    });

  fetch(`http://192.168.145.78:5000/getresumes/${seekerId}`)
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch resumes");
      return response.json();
    })
    .then(data => {
      console.log(data);
      const resumeSelect = document.getElementById("resume");
      if (!resumeSelect) throw new Error("Resume select element not found");

      const resumeList = Array.isArray(data) ? data : [data];

      resumeList.forEach(item => {
        const option = document.createElement("option");
        option.value = item;
        option.textContent = item.split('/').pop().split('--')[0];

        resumeSelect.appendChild(option);
      });

      
const viewBtn = document.createElement("button");
viewBtn.textContent = "View Resume";
viewBtn.type = "button"; // so it doesn't trigger form submit
viewBtn.style.marginLeft = "10px";

resumeSelect.parentNode.appendChild(viewBtn);

viewBtn.addEventListener("click", () => {
  const selectedResumeURL = resumeSelect.value;
  if (selectedResumeURL) {
    window.open(selectedResumeURL, "_blank");
  } else {
    alert("Select a resume first");
  }
});
    })
    .catch(err => {
      console.error("Error loading resumes:", err);
      alert("Failed to load resumes.");
    });

  const form = document.getElementById("applicationForm");
  if (!form) {
    console.error("Form not found");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const resumePath = document.getElementById("resume").value;

    if (!resumePath) {
      alert("Select a resume to apply.");
      return;
    }

    const payload = {
      resume_path: resumePath,
      job_id: jobId,
      seeker_id: seekerId
    };

    try {
      const response = await fetch("http://192.168.145.78:5000/jobseekerapply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.status === 409 ) {
        alert("you have already applied for this role");
        return;
      }

      if (!response.ok) {
        throw new Error(result.message || "Something went wrong");
      }

      alert("Application submitted successfully!");
      console.log(result);
      window.location.href = `joblisting.html?secret_code=${secretCode}&seeker_id=${seekerId}`;
      form.reset();

    } catch (err) {
      console.error("Error submitting form:", err);
      alert("Failed to submit application.");
    }
  });
});
