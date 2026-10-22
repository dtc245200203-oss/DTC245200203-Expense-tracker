const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const passwordToggle = document.getElementById('passwordToggle');
const loginMessage = document.getElementById('loginMessage');

fetch('/api/auth/session').then((response) => {
  if (response.ok) window.location.replace('/');
}).catch(() => {});

passwordToggle.addEventListener('click', () => {
  const isHidden = passwordInput.type === 'password';
  passwordInput.type = isHidden ? 'text' : 'password';
  passwordToggle.setAttribute('aria-label', isHidden ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
  passwordToggle.setAttribute('aria-pressed', String(isHidden));
  passwordToggle.querySelector('i').className = isHidden ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
});

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginMessage.className = 'login-message';
  if (!loginForm.checkValidity()) {
    loginMessage.textContent = 'Vui lòng nhập email hợp lệ và mật khẩu có ít nhất 8 ký tự.';
    loginMessage.classList.add('is-error');
    loginForm.reportValidity();
    return;
  }
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: emailInput.value.trim(),
        password: passwordInput.value,
        remember: document.getElementById('rememberMe').checked
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể đăng nhập');
    loginMessage.textContent = 'Đăng nhập thành công. Đang chuyển đến bảng điều khiển…';
    loginMessage.classList.add('is-success');
    window.setTimeout(() => window.location.assign('/'), 450);
  } catch (error) {
    loginMessage.textContent = error.message || 'Không thể kết nối đến máy chủ.';
    loginMessage.classList.add('is-error');
  }
});

function showUnavailable(event, message) {
  event.preventDefault();
  loginMessage.textContent = message;
  loginMessage.className = 'login-message is-info';
}

document.getElementById('forgotPassword').addEventListener('click', (event) => showUnavailable(event, 'Tính năng khôi phục mật khẩu sẽ được bổ sung khi hệ thống có tài khoản người dùng.'));
document.getElementById('registerLink').addEventListener('click', (event) => {
  event.preventDefault();
  window.location.assign('/register.html');
});
