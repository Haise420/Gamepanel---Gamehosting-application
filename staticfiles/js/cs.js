
    // Dohvatite sve elemente sa klasom "nav-button"
var navButtons = document.querySelectorAll('.nav-button');

    // Dodajte event listenere za svaki od njih
    navButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Dohvatite URL iz a taga unutar trenutno kliknutog "nav-buttona"
            var url = button.querySelector('a').getAttribute('href');
            
            // Preusmerite korisnika na taj URL
            window.location.href = url;
        });
    });


var navGTButtons = document.querySelectorAll('.navlink');

    // Dodajte event listenere za svaki od njih
    navGTButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Dohvatite URL iz a taga unutar trenutno kliknutog "nav-buttona"
            var url = button.querySelector('a').getAttribute('href');
            
            // Preusmerite korisnika na taj URL
            window.location.href = url;
        });
    });

var GTAddServerButton = document.querySelectorAll('.addserver-btn');

    // Dodajte event listenere za svaki od njih
    GTAddServerButton.forEach(function(button) {
        button.addEventListener('click', function() {
            // Dohvatite URL iz a taga unutar trenutno kliknutog "nav-buttona"
            var url = button.querySelector('a').getAttribute('href');
            
            // Preusmerite korisnika na taj URL
            window.location.href = url;
        });
    });

    