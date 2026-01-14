// Authentication functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Perform logout directly without confirmation
            fetch('/api/auth/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to home page
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Logout error:', error);
                // Fallback - just redirect
                window.location.href = '/api/auth/logout/';
            });
        });
    }
    
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Switch between modals with proper cleanup
    const showLoginFromRegister = document.getElementById('showLoginFromRegister');
    const showRegisterFromLogin = document.getElementById('showRegisterFromLogin');
    
    if (showLoginFromRegister) {
        showLoginFromRegister.addEventListener('click', function(e) {
            e.preventDefault();
            const registerModalEl = document.getElementById('registerModal');
            const loginModalEl = document.getElementById('loginModal');
            
            const registerModal = bootstrap.Modal.getInstance(registerModalEl);
            if (registerModal) {
                registerModal.hide();
                // Wait for hide animation to complete
                registerModalEl.addEventListener('hidden.bs.modal', function onHidden() {
                    registerModalEl.removeEventListener('hidden.bs.modal', onHidden);
                    const loginModal = new bootstrap.Modal(loginModalEl);
                    loginModal.show();
                }, { once: true });
            } else {
                const loginModal = new bootstrap.Modal(loginModalEl);
                loginModal.show();
            }
        });
    }
    
    if (showRegisterFromLogin) {
        showRegisterFromLogin.addEventListener('click', function(e) {
            e.preventDefault();
            const loginModalEl = document.getElementById('loginModal');
            const registerModalEl = document.getElementById('registerModal');
            
            const loginModal = bootstrap.Modal.getInstance(loginModalEl);
            if (loginModal) {
                loginModal.hide();
                // Wait for hide animation to complete
                loginModalEl.addEventListener('hidden.bs.modal', function onHidden() {
                    loginModalEl.removeEventListener('hidden.bs.modal', onHidden);
                    const registerModal = new bootstrap.Modal(registerModalEl);
                    registerModal.show();
                }, { once: true });
            } else {
                const registerModal = new bootstrap.Modal(registerModalEl);
                registerModal.show();
            }
        });
    }

    // Clear errors when input changes
    function clearFieldError(inputId, errorId) {
        const input = document.getElementById(inputId);
        const error = document.getElementById(errorId);
        if (input && error) {
            input.addEventListener('input', function() {
                input.classList.remove('is-invalid');
                error.textContent = '';
            });
        }
    }

    clearFieldError('registerUsername', 'usernameError');
    clearFieldError('registerEmail', 'emailError');
    clearFieldError('registerPassword', 'passwordError');
    clearFieldError('registerConfirmPassword', 'confirmPasswordError');
    clearFieldError('loginUsername', 'loginUsernameError');
    clearFieldError('loginPassword', 'loginPasswordError');

    // Register Form Submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
            document.getElementById('registerGeneralError').classList.add('d-none');
            document.getElementById('registerSuccess').classList.add('d-none');
            
            // Get form data
            const formData = {
                username: document.getElementById('registerUsername').value.trim(),
                email: document.getElementById('registerEmail').value.trim(),
                password: document.getElementById('registerPassword').value,
                confirm_password: document.getElementById('registerConfirmPassword').value
            };
            
            // Show loading state
            const registerBtn = document.getElementById('registerBtn');
            const registerBtnText = document.getElementById('registerBtnText');
            const registerSpinner = document.getElementById('registerSpinner');
            registerBtn.disabled = true;
            registerBtnText.classList.add('d-none');
            registerSpinner.classList.remove('d-none');
            
            try {
                const response = await fetch('/api/auth/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    const successAlert = document.getElementById('registerSuccess');
                    successAlert.textContent = data.message;
                    successAlert.classList.remove('d-none');
                    
                    // Reset form
                    registerForm.reset();
                    
                    // Close modal after 2 seconds and reload page
                    setTimeout(() => {
                        const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
                        if (registerModal) registerModal.hide();
                        location.reload();
                    }, 2000);
                } else {
                    // Show validation errors
                    if (data.errors) {
                        if (data.errors.username) {
                            document.getElementById('registerUsername').classList.add('is-invalid');
                            document.getElementById('usernameError').textContent = data.errors.username;
                        }
                        if (data.errors.email) {
                            document.getElementById('registerEmail').classList.add('is-invalid');
                            document.getElementById('emailError').textContent = data.errors.email;
                        }
                        if (data.errors.password) {
                            document.getElementById('registerPassword').classList.add('is-invalid');
                            document.getElementById('passwordError').textContent = data.errors.password;
                        }
                        if (data.errors.confirm_password) {
                            document.getElementById('registerConfirmPassword').classList.add('is-invalid');
                            document.getElementById('confirmPasswordError').textContent = data.errors.confirm_password;
                        }
                        if (data.errors.general) {
                            const generalError = document.getElementById('registerGeneralError');
                            generalError.textContent = data.errors.general;
                            generalError.classList.remove('d-none');
                        }
                    }
                }
            } catch (error) {
                console.error('Registration error:', error);
                const generalError = document.getElementById('registerGeneralError');
                generalError.textContent = 'An error occurred. Please try again.';
                generalError.classList.remove('d-none');
            } finally {
                // Reset button state
                registerBtn.disabled = false;
                registerBtnText.classList.remove('d-none');
                registerSpinner.classList.add('d-none');
            }
        });
    }

    // Login Form Submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
            document.getElementById('loginGeneralError').classList.add('d-none');
            document.getElementById('loginSuccess').classList.add('d-none');
            
            // Get form data
            const formData = {
                username: document.getElementById('loginUsername').value.trim(),
                password: document.getElementById('loginPassword').value
            };
            
            // Show loading state
            const loginBtn = document.getElementById('loginBtn');
            const loginBtnText = document.getElementById('loginBtnText');
            const loginSpinner = document.getElementById('loginSpinner');
            loginBtn.disabled = true;
            loginBtnText.classList.add('d-none');
            loginSpinner.classList.remove('d-none');
            
            try {
                const response = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    const successAlert = document.getElementById('loginSuccess');
                    successAlert.textContent = data.message;
                    successAlert.classList.remove('d-none');
                    
                    // Reset form
                    loginForm.reset();
                    
                    // Close modal after 1 second and reload page
                    setTimeout(() => {
                        const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                        if (loginModal) loginModal.hide();
                        location.reload();
                    }, 1000);
                } else {
                    // Show error
                    if (data.errors && data.errors.general) {
                        const generalError = document.getElementById('loginGeneralError');
                        generalError.textContent = data.errors.general;
                        generalError.classList.remove('d-none');
                    }
                }
            } catch (error) {
                console.error('Login error:', error);
                const generalError = document.getElementById('loginGeneralError');
                generalError.textContent = 'An error occurred. Please try again.';
                generalError.classList.remove('d-none');
            } finally {
                // Reset button state
                loginBtn.disabled = false;
                loginBtnText.classList.remove('d-none');
                loginSpinner.classList.add('d-none');
            }
        });
    }
});
