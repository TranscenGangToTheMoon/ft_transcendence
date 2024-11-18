document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
})

document.getElementById('chats').addEventListener('click', async event => {
    event.preventDefault();
    console.log('zizi')
    await navigateTo('/chat');
})

document.getElementById('settings').addEventListener('click', async event => {
    event.preventDefault();
    await navigateTo('/profile');
})