

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

document.getElementById('friends').addEventListener('click', event => {
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/friends/`)
        .then(data => {
            console.log(data);
        })
})

async function atStart() {
    await fetchUserInfos();
}

atStart();