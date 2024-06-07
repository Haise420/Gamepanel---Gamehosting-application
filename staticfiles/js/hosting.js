window.addEventListener('load', function () {
    // Nakon što se stranica učita, postavite timeout za 2 sekunde
    setTimeout(function () {
        // Sakrijte loading ekran
        document.querySelector('.loading-screen').style.opacity = 0;

        // Pričekajte još neko vrijeme (npr. 0.5 sekundi) prije nego konačno sakrijete loading ekran
        setTimeout(function () {
            document.querySelector('.loading-screen').style.display = 'none';
        }, 500);

        // Prikažite glavni sadržaj
        document.querySelector('.background').style.opacity = 1;
    }, 1500); // 2000 milisekundi = 2 sekunde
});