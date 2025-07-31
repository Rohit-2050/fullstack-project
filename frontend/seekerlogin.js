document.getElementById("seekerLoginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const secret_code = e.target.secret_code.value; 

  fetch("http://192.168.145.78:5000/jobseekerdashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ secret_code })
  })
  .then(res => res.json())
  .then(result => {
    if (result.seeker && result.seeker.name) {
      window.location.href = `seekerdashboard.html?secret_code=${secret_code}`; 
    } else {
      document.getElementById("message").innerText = "Invalid secret code.";
    }
  })
  .catch(() => {
    document.getElementById("message").innerText = "Login failed. Server error.";
  });
});
