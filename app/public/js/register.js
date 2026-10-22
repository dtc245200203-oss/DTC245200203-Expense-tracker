const registerForm = document.getElementById('registerForm');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirmPassword');
const passwordToggle = document.getElementById('passwordToggle');
const registerMessage = document.getElementById('registerMessage');

fetch('/api/auth/session').then((response) => {
  if (response.ok) window.location.replace('/');
}).catch(() => {});

passwordToggle.addEventListener('click', () => {
  const isHidden = passwordInput.type === 'password';
  passwordInput.type = isHidden ? 'text' : 'password';
  passwordToggle.querySelector('i').className = isHidden ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
  passwordToggle.setAttribute('aria-label', isHidden ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
});

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  registerMessage.className = 'login-message';
  if (!registerForm.checkValidity()) {
    registerMessage.textContent = 'Vui lòng hoàn tất các trường bắt buộc.';
    registerMessage.classList.add('is-error');
    registerForm.reportValidity();
    return;
  }
  if (passwordInput.value !== confirmPasswordInput.value) {
    registerMessage.textContent = 'Mật khẩu xác nhận chưa khớp.';
    registerMessage.classList.add('is-error');
    confirmPasswordInput.focus();
    return;
  }
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: passwordInput.value,
        remember: document.getElementById('rememberMe').checked
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể tạo tài khoản');
    registerMessage.textContent = 'Tạo tài khoản thành công. Đang chuyển đến bảng điều khiển…';
    registerMessage.classList.add('is-success');
    window.setTimeout(() => window.location.assign('/'), 450);
  } catch (error) {
    registerMessage.textContent = error.message || 'Không thể kết nối đến máy chủ.';
    registerMessage.classList.add('is-error');
  }
});
