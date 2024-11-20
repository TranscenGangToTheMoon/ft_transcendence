async function guestProfileInit() {
    await loadContent('/authenticationForm.html', 'authenticate');
}

guestProfileInit();