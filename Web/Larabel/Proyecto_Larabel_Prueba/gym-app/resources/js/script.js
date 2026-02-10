document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('boton');
    if (boton) {
        boton.addEventListener('click', () => {
            alert('¡Has hecho clic! 😎');
        });
    }
});
