async function acceptFriendRequest(id){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'POST');
        document.getElementById(`${id}`).remove();
        friendListInit();
    }
    catch (error){
        console.log(error);
    }
}

async function declineFriendRequest(id){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'DELETE');
        document.getElementById(`${id}`).remove();
    }
    catch (error) {
        console.log(error);
    }
}

(async function friendRequests(){
    const declineButtons = document.querySelectorAll('.declineFriendRequest');

    for (let declineButton of declineButtons){
        if (!declineButton.listened){
            declineButton.addEventListener('click', async event => {
                await declineFriendRequest(declineButton.parentElement.parentElement.parentElement.id);
                console.log('declined friend request: ', declineButton.parentElement.parentElement.parentElement.id);
            })
        }
        declineButton.listened = true;
    }

    const acceptButtons = document.querySelectorAll('.acceptFriendRequest');

    for (let acceptButton of acceptButtons){
        if (!acceptButton.listened){
            acceptButton.addEventListener('click', async event => {
                await acceptFriendRequest(acceptButton.parentElement.parentElement.parentElement.id);
                console.log('accepted friend request: ', acceptButton.parentElement.parentElement.parentElement.id);
            })
        }
        acceptButton.listened = true;
    }
})()
