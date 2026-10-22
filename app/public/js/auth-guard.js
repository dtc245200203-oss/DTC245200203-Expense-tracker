fetch('/api/auth/session')
  .then((response) => {
    if (!response.ok) window.location.replace('/login.html');
  })
  .catch(() => window.location.replace('/login.html'));

document.getElementById('logoutLink').addEventListener('click', async (event) => {
  event.preventDefault();
  await fetch('/api/auth/logout', { method: 'POST' });
  window.location.replace('/login.html');
});
