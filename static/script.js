function expandir(elemento) {
    const tarjetas = document.querySelectorAll('.tarjeta');
    tarjetas.forEach(t => t.classList.remove('expandido'));
    elemento.classList.add('expandido');

    const overlay = document.getElementById('overlay');
    overlay.style.display = 'block';
}

function cerrarExpandido() {
    const tarjetas = document.querySelectorAll('.tarjeta.expandido');
    tarjetas.forEach(t => t.classList.remove('expandido'));

    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
}

function scrollToHoja(nombre) {
    const seccion = document.getElementById(`hoja-${nombre}`);
    if (seccion) {
        seccion.scrollIntoView({ behavior: 'smooth' });
    }
}

document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('click', function() {
    const data = JSON.parse(this.getAttribute('data-json'));
    expandirCard(this, data);
  });
});
 