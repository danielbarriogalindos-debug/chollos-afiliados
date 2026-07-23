
document.addEventListener('DOMContentLoaded', function () {
  if (!localStorage.getItem('cookie_ok')) {
    document.getElementById('cookie-banner').style.display = 'block';
  }
  document.getElementById('cookie-accept').addEventListener('click', function () {
    localStorage.setItem('cookie_ok', '1');
    document.getElementById('cookie-banner').style.display = 'none';
  });
});
