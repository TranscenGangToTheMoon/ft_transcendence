
async function decrementFriendRequests(sent){
    if (getDisplayedFriendRequests(sent) < 10){
        if (sent) return await getMoreSentFriendRequests();
        else await getMoreFriendRequests();
    }
}

async function acceptFriendRequest(id){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'POST');
        document.getElementById(`fr${id}`).remove();
        nextFriendRequest = decrementOffset(nextFriendRequest);
        await decrementFriendRequests();
        await loadFriendList();
    }
    catch (error){
        console.log(error);
    }
}

async function declineFriendRequest(id, sent=false){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'DELETE');
        document.getElementById(`fr${id}`).remove();
        if (!sent){
            nextFriendRequest = decrementOffset(nextFriendRequest);
            decrementFriendRequests();
        }
        else {
            nextSentFriendRequest = decrementOffset(nextSentFriendRequest);
            decrementFriendRequests(sent);
        }
    }
    catch (error) {
        console.log(error);
    }
}

(async function friendRequests(){
    const declineButtons = document.querySelectorAll('.declineFriendRequest');

    for (let declineButton of declineButtons){
        if (!declineButton.listened){
            declineButton.addEventListener('click', async function (event){
                let sent = false;
                if (this.classList.contains('sent')) sent = true;
                let id = declineButton.parentElement.parentElement.parentElement.id;
                await declineFriendRequest(id.substring(2), sent);
            })
        }
        declineButton.listened = true;
    }

    const acceptButtons = document.querySelectorAll('.acceptFriendRequest');

    for (let acceptButton of acceptButtons){
        if (!acceptButton.listened){
            acceptButton.addEventListener('click', async event => {
                let id = acceptButton.parentElement.parentElement.parentElement.id
                await acceptFriendRequest(id.substring(2));
            })
        }
        acceptButton.listened = true;
    }
})()
