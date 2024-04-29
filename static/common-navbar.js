document.addEventListener("DOMContentLoaded", function() {
  // Get current URL
  const currentPath = window.location.pathname;

  // Function to set the 'active' class on the matching nav button
  function setActive(navId) {
    const link = document.getElementById(navId);
    if (link) {
      link.classList.add('active');
    }
  }

  // Determine which nav item to activate based on currentPath
  if (currentPath === '/' || currentPath === '/home') {
    setActive('homeLink');
  } else if (currentPath === '/eventos') {
    setActive('eventosLink');
  } else if (currentPath === '/contenido') {
    setActive('contenidoLink');
  } else if (currentPath === '/miembros') {
    setActive('miembrosLink');
  } else if (currentPath === '/galeria') {
    setActive('galeriaLink');
  } else if (currentPath === '/formatos') {
    setActive('formatosLink');
  } else if (currentPath === '/contacto') {
    setActive('contactoLink');
  }
  // add more conditions as necessary for other pages
});
