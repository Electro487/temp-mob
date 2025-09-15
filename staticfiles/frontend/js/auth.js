document.addEventListener("DOMContentLoaded", () => {
  // -----------------------------
  // Helper: Change page title
  // -----------------------------
  function setPageTitle(newTitle) {
    document.title = newTitle;
  }

  // -----------------------------
  // Password toggle - Using exact IDs from Django forms
  // -----------------------------
  function setupPasswordToggles() {
    const passwordToggles = [
      { iconSelector: ".signup_section .toggle-password", inputId: "signup-password" },
      { iconSelector: ".login_section .toggle-password", inputId: "login-password" },
      { iconSelector: ".toggle-confirm-password", inputId: "confirm-password" }
    ];

    passwordToggles.forEach(({ iconSelector, inputId }) => {
      const icon = document.querySelector(iconSelector);
      const input = document.getElementById(inputId);
      
      if (icon && input) {
        icon.addEventListener("click", () => {
          if (input.type === "password") {
            input.type = "text";
            icon.src = window.VISIBLE_IMAGE_URL;
            icon.alt = "hide password";
          } else {
            input.type = "password";
            icon.src = window.HIDE_IMAGE_URL;
            icon.alt = "show password";
          }
        });
      }
    });
  }

  // -----------------------------
  // SPA form toggling with proper title updates
  // -----------------------------
  function setupFormToggling() {
    const mainEl = document.querySelector("main");
    const dinoImg = document.querySelector(".dino_container .dino_img");
    const signupSection = document.querySelector(".signup_section");
    const loginSection = document.querySelector(".login_section");

    const toggleLogin = document.querySelector("#toggle-login");
    const toggleSignup = document.querySelector("#toggle-signup");

    if (toggleLogin) {
      toggleLogin.addEventListener("click", (e) => {
        e.preventDefault();
        
        // Update UI state
        if (mainEl) mainEl.classList.add("login-active");
        if (signupSection) signupSection.classList.add("hidden");
        if (loginSection) loginSection.classList.remove("hidden");
        
        // Update dinosaur image
        // if (dinoImg && window.DINO_REVERSE_URL) {
        //   dinoImg.src = window.DINO_REVERSE_URL;
        // }
        
        // Update page title
        setPageTitle("Login | Mobizilla");
        
        // Clear any form errors when switching
        clearFormErrors();
      });
    }

    if (toggleSignup) {
      toggleSignup.addEventListener("click", (e) => {
        e.preventDefault();
        
        // Update UI state
        if (mainEl) mainEl.classList.remove("login-active");
        if (loginSection) loginSection.classList.add("hidden");
        if (signupSection) signupSection.classList.remove("hidden");
        
        // Update dinosaur image
        if (dinoImg && window.DINO_3D_URL) {
          dinoImg.src = window.DINO_3D_URL;
        }
        
        // Update page title
        setPageTitle("Sign Up | Mobizilla");
        
        // Clear any form errors when switching
        clearFormErrors();
      });
    }
  }

  // -----------------------------
  // Helper: Clear form errors when switching forms
  // -----------------------------
  function clearFormErrors() {
    document.querySelectorAll('.error, .non-field-errors').forEach(error => {
      error.style.display = 'none';
    });
    document.querySelectorAll('.form-field-error').forEach(field => {
      field.classList.remove('form-field-error');
    });
  }

  // -----------------------------
  // Set initial title based on current state
  // -----------------------------
  function setInitialTitle() {
    const mainEl = document.querySelector("main");
    
    if (mainEl && mainEl.classList.contains("login-active")) {
      setPageTitle("Login | Mobizilla");
    } else {
      setPageTitle("Sign Up | Mobizilla");
    }
  }

  // -----------------------------
  // Dinosaur eye movement
  // -----------------------------
  function setupEyeMovement() {
    const rightEye = document.querySelector(".right-eye .pupil");

    if (rightEye && window.matchMedia("(pointer: fine)").matches) {
      let animationFrameId;

      window.addEventListener("mousemove", (e) => {
        if (animationFrameId) {
          cancelAnimationFrame(animationFrameId);
        }

        animationFrameId = requestAnimationFrame(() => {
          const eyeElement = document.querySelector(".right-eye");
          if (!eyeElement) return;
          
          const eyeRect = eyeElement.getBoundingClientRect();
          const centerX = eyeRect.left + eyeRect.width / 2;
          const centerY = eyeRect.top + eyeRect.height / 2;
          
          const deltaX = e.clientX - centerX;
          const deltaY = e.clientY - centerY;
          const angle = Math.atan2(deltaY, deltaX);
          
          const maxDistanceX = 5;
          const maxDistanceY = 5;
          
          const moveX = Math.cos(angle) * Math.min(maxDistanceX, Math.abs(deltaX) * 0.1);
          const moveY = Math.sin(angle) * Math.min(maxDistanceY, Math.abs(deltaY) * 0.1);
          
          rightEye.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
        });
      });
    }
  }

  // -----------------------------
  // Alert timeout
  // -----------------------------
  function setupAlertTimeout() {
    document.querySelectorAll(".alert").forEach((alert) => {
      alert.style.opacity = "1";
      alert.style.transition = "opacity 300ms ease-out";
      
      setTimeout(() => {
        alert.style.opacity = "0";
        setTimeout(() => {
          if (alert.parentNode) {
            alert.remove();
          }
        }, 300);
      }, 5000);
    });
  }

  // -----------------------------
  // Initialize everything
  // -----------------------------
  setInitialTitle();
  setupPasswordToggles();
  setupFormToggling();
  setupEyeMovement();
  setupAlertTimeout();
});