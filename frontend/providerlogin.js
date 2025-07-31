document.getElementById("providerLoginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const secretCode = e.target.secret_code.value;
console.log("Form submitted with secret code:", secretCode);


  fetch("http://192.168.145.78:5000/providerdashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ secret_code: secretCode })
  })
  .then(res => res.json())
  
  .then(result => {
  console.log("Result from backend:", result);

  if (result.provider && result.provider.company_name) {
    window.location.href = `providerdashboard.html?secret_code=${secretCode}`;
  } else {
    document.getElementById("message").innerText = "Invalid Secret Code.";
  }
})


  .catch(() => {
    document.getElementById("message").innerText = "Login failed. Server error.";
  });
});
