// Salva usuário na sessão
function salvarUsuario(usuario) {
  sessionStorage.setItem('usuario', JSON.stringify(usuario));
}

// Retorna o usuário ou redireciona para login
function getUsuario() {
  const u = sessionStorage.getItem('usuario');
  if (!u) { window.location.href = '/'; return null; }
  return JSON.parse(u);
}

// Preenche o nome na navbar
function preencherNavbar() {
  const u = getUsuario();
  if (u) document.getElementById('nav-nome').textContent = u.nome.split(' ')[0];
}

// Logout
function logout() {
  sessionStorage.removeItem('usuario');
  window.location.href = '/';
}

// Exibe mensagem de feedback
function mostrarMsg(id, texto, tipo) {
  const el = document.getElementById(id);
  el.textContent = texto;
  el.className = 'msg ' + tipo;
  el.style.display = 'block';
}
