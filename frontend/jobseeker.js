document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("jobseekerForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const data = new FormData(form);  

    fetch("http://192.168.145.78:5000/jobseekerregister", {
      method: "POST",
      body: data
    })
    .then(res => res.json())
    .then(result => {
      console.log(result);
      const messageDiv = document.getElementById("message");
      messageDiv.innerHTML = "";

      if (result.secret_code) {
        const msg = document.createElement("p");
        msg.innerText = `Profile created successfully.\nYour Secret Code is: ${result.secret_code}\nPlease save this code for future login.`;
        messageDiv.appendChild(msg);

        const loginBtn = document.createElement("button");
        loginBtn.innerText = "Login Now";
        loginBtn.style.marginTop = "10px";
        loginBtn.addEventListener("click", function () {
          window.location.href = "seekerlogin.html";
        });

        messageDiv.appendChild(loginBtn);
      } else {
        messageDiv.innerText = result.message || "Something went wrong. Please try again.";
      }
    })
    .catch(() => {
      document.getElementById("message").innerText = "Failed to connect to server.";
    });
  });
});
