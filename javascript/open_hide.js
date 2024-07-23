document.addEventListener('DOMContentLoaded', function() {

    const createMenuBtn = document.getElementById('createMenuBtn');
    createMenuBtn.addEventListener('click', function() {
        document.getElementById('createMenu').style.display = "block";
        document.getElementById("titleDiv").style.display = 'none';
        document.getElementById('subMenuBtnsDiv').style.display = 'none';
    });

    const connectMenuBtn = document.getElementById('connectMenuBtn');
    connectMenuBtn.addEventListener('click', function() {
        document.getElementById('connectMenu').style.display = "block";
        document.getElementById("titleDiv").style.display = 'none';
        document.getElementById('subMenuBtnsDiv').style.display = 'none';
    });
});