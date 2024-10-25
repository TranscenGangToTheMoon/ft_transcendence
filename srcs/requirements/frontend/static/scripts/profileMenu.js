document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    generateGuestToken();
    await fetchUserInfos(true);
    await loadUserProfile();
    await loadContent('/homePage.html');
})