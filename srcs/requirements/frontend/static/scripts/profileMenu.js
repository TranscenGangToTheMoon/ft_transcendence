document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    generateToken();
    await fetchUserInfos(true);
    await loadUserProfile();
    await loadContent('/homePage.html');
})