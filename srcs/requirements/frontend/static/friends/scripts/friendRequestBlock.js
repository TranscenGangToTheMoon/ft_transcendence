async function acceptFriendRequest(id){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'POST');
    }
    catch (error){
        console.log(error);
    }
}

(async function friendRequests(){
    const declineButtons = document.querySelectorAll('.declineFriendRequest');

    for (let declineButton of declineButtons){
        if (!declineButton.listened){
            declineButton.addEventListener('click', async event => {
                await declineFriendRequest(declineButton.parentElement.parentElement.id);
                console.log('declined friend request: ', declineButton.parentElement.parentElement.id);
            })
        }
        declineButton.listened = true;
    }

    const acceptButtons = document.querySelectorAll('.acceptFriendRequest');

    for (let acceptButton of acceptButtons){
        if (!acceptButton.listened){
            acceptButton.addEventListener('click', async event => {
                await acceptFriendRequest(acceptButton.parentElement.parentElement.id);
                console.log('accepted friend request: ', acceptButton.parentElement.parentElement.id);
            })
        }
        acceptButton.listened = true;
    }
})()
