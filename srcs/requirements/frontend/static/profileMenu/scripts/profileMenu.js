
document.getElementById('settings').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game')
        return cancelNavigation(undefined, '/profile');
    await navigateTo('/profile');
})