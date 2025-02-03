if (typeof isClickStartingInside === 'undefined')
    var isClickStartingInside = false;

document.getElementById('loginMenu').addEventListener('click', event => {
    event.stopPropagation();
})

document.getElementById('loginMenu').addEventListener('mousedown', event => {
    isClickStartingInside = true;
})

document.getElementById('loginMenu').addEventListener('mouseup', event => {
    isClickStartingInside = false;
})

document.addEventListener("hide.bs.dropdown", function (event) {
    if (isClickStartingInside)
        event.preventDefault();
    isClickStartingInside = false;
});

async function guestProfileInit() {
    await loadContent('/profileMenu/authenticateForm/authenticationForm.html', 'authenticate');
}

guestProfileInit();