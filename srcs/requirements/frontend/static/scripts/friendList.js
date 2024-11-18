document.getElementById('searchButton').addEventListener('click', event => {
    event.preventDefault();
    document.getElementById('searchResults').innerText = "euh je sais pas comment ca marche l'API";
    document.getElementById('searchResults').style = 'color:red';
})

function friendListInit(){
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/friends/`)
        .then(data => {
            console.log(data);
            if (!data.count)
                document.getElementById('knownFriends').innerText = "you don't have any friends";
            else
                document.getElementById('knownFriends').innerText = "unable to fetch friend list";
        })
        .catch(error => {
            console.log(error);
        })
}

friendListInit();