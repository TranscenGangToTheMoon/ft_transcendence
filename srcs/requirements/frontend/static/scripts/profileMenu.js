document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    generateToken();
    await fetchUserInfos(true);
    await loadUserProfile();
    await navigateTo(window.location.pathname);
})

document.getElementById('settings').addEventListener('click', event => {
    event.preventDefault();
    navigateTo('/profile');
})