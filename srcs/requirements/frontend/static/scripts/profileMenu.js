document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    navigateTo(window.location.pathname);
})

document.getElementById('settings').addEventListener('click', event => {
    event.preventDefault();
    navigateTo('/profile');
})