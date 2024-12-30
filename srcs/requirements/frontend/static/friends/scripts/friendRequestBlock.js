
async function decrementFriendRequests(sent){
    if (getDisplayedFriendRequests(sent) < 10){
        // console.log(nextFriendRequest);
        if (sent) return await getMoreSentFriendRequests();
        else await getMoreFriendRequests();
        // console.log(nextFriendRequest);
    }
    // let old = document.getElementById('innerFriendRequests-tab').innerText.match(/\((.*?)\)/);
    // old = parseInt(old[1]);
    // if (old < 2)
    //     document.getElementById('innerFriendRequests-tab').innerText = `Friend Requests`;
    // else 
    //     document.getElementById('innerFriendRequests-tab').innerText = `Friend Requests (${old - 1})`;
}

async function acceptFriendRequest(id){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/${id}/`, 'POST');
        document.getElementById(`${id}`).remove();
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
        document.getElementById(`${id}`).remove();
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
                await declineFriendRequest(declineButton.parentElement.parentElement.parentElement.id, sent);
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
