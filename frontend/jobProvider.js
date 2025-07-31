document.getElementById("providerForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const form = e.target;
  const data = {
    company_name: form.company_name.value,
    name: form.name.value,
    email: form.email.value,
    phone: form.phone.value,
  };

  fetch("http://192.168.145.78:5000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
  const messageDiv = document.getElementById("message");
  messageDiv.innerHTML = ""; 

  if (result.secret_code) {
    const msg = document.createElement("p");
    msg.innerText = `Your Secret Code is: ${result.secret_code}`;
    messageDiv.appendChild(msg);

    const loginBtn = document.createElement("button");
    loginBtn.innerText = "Login Now";
    loginBtn.style.marginTop = "10px";
    loginBtn.addEventListener("click", function () {
      window.location.href = "providerlogin.html";
    });

    messageDiv.appendChild(loginBtn);
  } else {
    messageDiv.innerText = result.message || "Something went wrong.";
  }
})

  .catch(() => {
    document.getElementById("message").innerText =
      "Failed to connect to server.";
  });
});
