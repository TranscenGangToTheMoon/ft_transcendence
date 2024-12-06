function acceptFriendRequest(id){
    try {
        let data = apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'POST');
    }
    catch (error){
        console.log(error);
    }
}

(function friendRequests(){
    const declineButtons = document.querySelectorAll('.declineFriendRequest');

    for (let declineButton of declineButtons){
        if (!declineButton.listened){
            declineButton.addEventListener('click', event => {
                declineFriendRequest(declineButton.parentElement.parentElement.id);
                console.log('declined friend request: ', declineButton.parentElement.parentElement.id);
            })
        }
        declineButton.listened = true;
    }

    const acceptButtons = document.querySelectorAll('.acceptFriendRequest');

    for (let acceptButton of acceptButtons){
        if (!acceptButton.listened){
            acceptButton.addEventListener('click', event => {
                acceptFriendRequest(acceptButton.parentElement.parentElement.id);
                console.log('accepted friend request: ', acceptButton.parentElement.parentElement.id);
            })
        }
        acceptButton.listened = true;
    }
})()
