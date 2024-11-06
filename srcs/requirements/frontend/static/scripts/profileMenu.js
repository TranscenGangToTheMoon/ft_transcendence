document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
})

document.getElementById('settings').addEventListener('click', event => {
    event.preventDefault();
    navigateTo('/profile');
})