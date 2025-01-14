document.getElementById('switchAcceptFriendRequests').addEventListener('change', async function (event){
    event.preventDefault();
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, 'PATCH', undefined, undefined, {
            'accept_friend_request': this.checked,
        })
    }
    catch(error){
        console.log(error);
        this.checked=false;
    }
})

function initSwitch(){
    const FRswitch = document.getElementById('switchAcceptFriendRequests');
    if (FRswitch)
        FRswitch.checked = userInformations.accept_friend_request;
}

async function initFriendsTemplate() {
    await loadBlockedModal();
    getBadgesDivs();
    displayBadges();
    initSwitch();
}

initFriendsTemplate();
