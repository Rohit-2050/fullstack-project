document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const secretCode = urlParams.get("secret_code");

  const response = await fetch("http://192.168.145.78:5000/providerdashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ secret_code: secretCode })
  });

  if (!response.ok) {
    alert("Failed to fetch dashboard data.");
    return;
  }

  const result = await response.json();
  const provider = result.provider;
  const jobPosts = result.job_posts;

  document.getElementById("welcomeMsg").textContent = `Welcome, ${provider.name}`;
  document.getElementById("companyName").textContent = `Company: ${provider.company_name}`;
  document.getElementById("email").textContent = `Email: ${provider.email}`;
  document.getElementById("createdBy").textContent = `Created By: ${provider.created_by}`;

  const jobsContainer = document.getElementById("jobsContainer");
  const postJobBtn = document.createElement("button");
  postJobBtn.textContent = "Post a Job";
  postJobBtn.className = "btn";
  postJobBtn.style.margin = "20px 0";
  postJobBtn.onclick = () => {
    window.location.href = `job.html?provider_id=${provider.provider_id}&secret_code=${secretCode}`;
  };

  jobsContainer.parentNode.insertBefore(postJobBtn, jobsContainer);

  if (jobPosts.length === 0) {
    jobsContainer.innerHTML = "<p>No job posts yet.</p>";
    return;
  }

  jobPosts.forEach((job) => {
    const jobDiv = document.createElement("div");
    jobDiv.className = "job-card";
    jobDiv.innerHTML = `
      <h3>${job.title || "Job Title"}</h3>
      <p>${job.job_description}</p>
      <p>Category: ${job.category}</p>
      <p>Deadline: ${new Date(job.application_deadline).toLocaleDateString()}</p>
      <button class="btn" onclick="viewApplicants('${job.job_id}', '${provider.provider_id}')">View Applicants</button>
    `;
    jobsContainer.appendChild(jobDiv);
  });
});

function viewApplicants(jobId, providerId) {
  window.location.href = `applications.html?job_id=${jobId}&provider_id=${providerId}`;
}

function screenApplicants(jobId, providerId) {
  window.location.href = `screen.html?job_id=${jobId}&provider_id=${providerId}`;
}
