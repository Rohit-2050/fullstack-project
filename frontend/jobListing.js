document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("job-listings");
  const urlParams = new URLSearchParams(window.location.search);
  const seekerId = urlParams.get("seeker_id");
  const providerId = urlParams.get("provider_id");

  fetch("http://192.168.145.78:5000/jobs")
    .then(res => res.json())
    .then(data => {
      console.log(data);
      const jobs = data;
     
      if (jobs.length === 0) {
        container.innerHTML = "<p>No jobs posted yet.</p>";
        return;
      }

      jobs.sort((a, b) => b.job_id - a.job_id);

      jobs.forEach(job => {
        const jobCard = document.createElement("div");
        jobCard.className = "job-card";

        let actionBtn = "";
        if (seekerId) {
          actionBtn = `<a href="apply.html?seeker_id=${seekerId}&job_id=${job.job_id}" class="apply-btn">Apply Now</a>`;
        }

        jobCard.innerHTML = `
          <h2 class="job-title">${job.title}</h2>
          <p class="job-description">${job.job_description}</p>
          <div class="job-meta">
            <span><strong>Experience:</strong> ${job.experience_level} year(s)</span>
            <span><strong>Category:</strong> ${job.category}</span>
            <span><strong>Type:</strong> ${job.job_type}</span>
            <span><strong>Deadline:</strong> ${job.application_deadline}</span>
          </div>
          ${actionBtn}
        `;
        container.appendChild(jobCard);
      });
    })
    .catch(() => {
      container.innerHTML = "<p>Error fetching job listings.</p>";
    });

  const btn = document.getElementById("postjob");
  if (btn) {
    btn.addEventListener("click", () => {
      if (providerId) {
        window.location.href = `postJob.html?provider_id=${providerId}`;
      } else {
        window.location.href = "jobprovider.html";
      }
  
    });
  }

 
});
