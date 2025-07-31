document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector("#jobForm");

  const urlParams = new URLSearchParams(window.location.search);
  const provider_id = urlParams.get("provider_id");
  const secret_code = urlParams.get("secret_code");

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const jobFields = {
      title: document.getElementById("title"),
      jobDescription: document.getElementById("jobDescription"),
      experience: document.getElementById("experience"),
      jobtype: document.getElementById("jobType"),
      category: document.getElementById("category"),
      location: document.getElementById("location"),
      deadline: document.getElementById("deadline")
    };

    let isvalid = true;
    let firstvalid = null;

    for (key in jobFields) {
      const field = jobFields[key];
      if (field.value.trim() === "") {
        field.style.border = "2px solid red";
        if (!firstvalid) firstvalid = field;
        isvalid = false;
      } else {
        field.style.border = "";
      }
    }

    if (!isvalid) {
      alert("fill all the fields");
      return;
    }


    const data = {
      title: jobFields.title.value,
      job_description: jobFields.jobDescription.value.substring(0,100),
      experience: jobFields.experience.value,
      job_type: jobFields.jobtype.value,
      category: jobFields.category.value,
      location: jobFields.location.value,
      application_deadline: jobFields.deadline.value,
      provider_id: provider_id
    };
console.log("Sending job data:", data);

    try {
      const res = await fetch(`http://192.168.145.78:5000/createJob/${provider_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        alert("Job posted");
        window.location.href = `providerdashboard.html?secret_code=${secret_code}`;
        
        form.reset();
      } else {
        alert("failed to post the job");
      }
    } catch (err) {
      alert("error while sending data");
    }
  });
});
