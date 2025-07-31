document.addEventListener("DOMContentLoaded", async function () {
  const urlParams = new URLSearchParams(window.location.search);
  const secret_code = urlParams.get("secret_code");

  if (!secret_code) {
    alert("Secret code missing.");
    return;
  }

  try {
    const response = await fetch("http://192.168.145.78:5000/jobseekerdashboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ secret_code })
    });

    const result = await response.json();
    console.log("Dashboard response:", result);

    if (!result.seeker || !result.seeker.name) {
      alert("Invalid seeker data.");
      return;
    }

    const seekerId = result.seeker.id;

    const welcomeEl = document.getElementById("welcome");
    if (welcomeEl) {
      welcomeEl.innerText = `Welcome, ${result.seeker.name}`;
    }

    const jobList = document.getElementById("jobList");
    if (jobList) {
      jobList.innerHTML = "";

      const applications = result.applications;

      console.log("Applications:", applications);

      if (!applications || applications.length === 0) {
        jobList.innerHTML = "<p>No applied jobs yet.</p>";
      } else {
        applications.forEach(app => {
          const li = document.createElement("li");
          li.textContent = `${app.title} - ${app.company_name} (${app.location})`;
          jobList.appendChild(li);
        });
      }
    }

    const applyBtn = document.getElementById("applyBtn");
    if (applyBtn) {
      applyBtn.addEventListener("click", function () {
        window.location.href = `joblisting.html?secret_code=${secret_code}&seeker_id=${seekerId}`;
      });
    }

  } catch (err) {
    console.error("Fetch error:", err);
    alert("Error loading dashboard.");
  }
});
