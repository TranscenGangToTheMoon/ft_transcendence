document.getElementById('switchAcceptFriendRequests').addEventListener('change', function (event){
    event.preventDefault();
    document.getElementById('tempError').innerText = "aled ya pas d'enpoint pour ca dans l'API encore";
    document.getElementById('tempError').style = 'color:red';
    setTimeout(() => this.checked=false, 150);
})

async function initFriendsTemplate() {
    // console.log(userInformations);
    let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, 'PATCH', undefined, undefined, {
        'acception_friend_request': true
    })
}

initFriendsTemplate();