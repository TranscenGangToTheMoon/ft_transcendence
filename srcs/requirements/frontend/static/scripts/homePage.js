

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

document.getElementById('searchButton').addEventListener('click', event => {
    event.preventDefault();
    document.getElementById('searchResults').innerText = "euh je sais pas comment ca marche l'API";
    document.getElementById('searchResults').style = 'color:red';
})

document.getElementById('ranked').addEventListener('click', event => {
    navigateTo('/lobby');
})

async function homePageInit() {
    await indexInit(false);
}

homePageInit();