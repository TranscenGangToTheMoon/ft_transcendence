

// document.getElementById('logoutButton').addEventListener('click', () => {
//     relog();
// })

// document.getElementById('testRefresh').addEventListener('click', event => {
//     event.preventDefault();
//     getDataFromApi(localStorage.getItem('token'), `${baseAPIUrl}/users/me/`)
//     .then (data => {
//         console.log(data);
//     })
//     .catch (error => {
//         console.log( error);
//     })
// })

// document.getElementById('delete').addEventListener('click', event => {
//     event.preventDefault();
//     console.log('delete');
//     removeTokens();
// })

// NAVIGAtORS

document.getElementById('chat').addEventListener('click', async event => {
    await navigateTo('/chat');
})

document.getElementById('ranked').addEventListener('click', async event => {
    await navigateTo('/game');
})
    
async function homePageInit() {
    await indexInit(false);
}

homePageInit();