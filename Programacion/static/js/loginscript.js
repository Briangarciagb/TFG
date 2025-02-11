const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});
document.addEventListener("DOMContentLoaded", () => {
    const signInBtn = document.getElementById("sign-in-btn");
    const signUpBtn = document.getElementById("sign-up-btn");
    const container = document.querySelector(".container");
  
    signUpBtn.addEventListener("click", () => {
      container.classList.add("sign-up-mode");
    });
  
    signInBtn.addEventListener("click", () => {
      container.classList.remove("sign-up-mode");
    });
  });

  
  
  