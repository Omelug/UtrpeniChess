
document.addEventListener('DOMContentLoaded', function() {

    const button0 = document.getElementById("mainText")
    const button1 = document.getElementById('gamemenu');
    const button2 = document.getElementById('enjoyGame');

    button1.addEventListener('click', function() {
        button2.remove();
        button1.remove();
        button0.remove();

    });
});