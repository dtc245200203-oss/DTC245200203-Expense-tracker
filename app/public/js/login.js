const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const passwordToggle = document.getElementById('passwordToggle');
const loginMessage = document.getElementById('loginMessage');

passwordToggle.addEventListener('click', () => {
  const isHidden = passwordInput.type === 'password';
  passwordInput.type = isHidden ? 'text' : 'password';
  passwordToggle.setAttribute('aria-label', isHidden ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
  passwordToggle.setAttribute('aria-pressed', String(isHidden));
  passwordToggle.querySelector('i').className = isHidden ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
});

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();
  loginMessage.className = 'login-message';
  if (!loginForm.checkValidity()) {
    loginMessage.textContent = 'Vui lòng nhập email hợp lệ và mật khẩu có ít nhất 6 ký tự.';
    loginMessage.classList.add('is-error');
    loginForm.reportValidity();
    return;
  }
  // Replace this client-side transition with a server-side /api/auth/login call when authentication is added.
  const storage = document.getElementById('rememberMe').checked ? localStorage : sessionStorage;
  storage.setItem('expenseTrackerUser', emailInput.value.trim());
  loginMessage.textContent = 'Đăng nhập thành công. Đang chuyển đến bảng điều khiển…';
  loginMessage.classList.add('is-success');
  window.setTimeout(() => window.location.assign('/'), 450);
});

function showUnavailable(event, message) {
  event.preventDefault();
  loginMessage.textContent = message;
  loginMessage.className = 'login-message is-info';
}

document.getElementById('forgotPassword').addEventListener('click', (event) => showUnavailable(event, 'Tính năng khôi phục mật khẩu sẽ được bổ sung khi hệ thống có tài khoản người dùng.'));
document.getElementById('registerLink').addEventListener('click', (event) => showUnavailable(event, 'Tính năng đăng ký sẽ được bổ sung cùng mô-đun xác thực.'));
