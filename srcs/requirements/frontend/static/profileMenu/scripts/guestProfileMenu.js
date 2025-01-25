async function guestProfileInit() {
    await loadContent('/profileMenu/authenticateForm/authenticationForm.html', 'authenticate');
}

guestProfileInit();