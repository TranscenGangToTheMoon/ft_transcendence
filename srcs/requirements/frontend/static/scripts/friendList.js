if (document.getElementById('modals').friendListened !== true){
    document.getElementById('modals').friendListened = true;
    document.getElementById('modals').addEventListener('click', async function(event){
        console.log('click')
        event.preventDefault();
        if (event.target.matches('#sendFriendRequest')){
            document.getElementById('searchResults').innerText = "";
            event.preventDefault();
            const userInput = document.getElementById('friendSearched').value;
            try {
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
                    'username' : userInput,
                })
                const detail = data.detail ? data.detail : data.username;
                if (detail){
                    document.getElementById('searchResults').innerText = detail;
                }
                else
                    friendListInit();
            }
            catch (error) {
                console.log(error);
                if (error.code === 404)
                    document.getElementById('searchResults').innerText = 'user not found';
            }
        }
    })
}

// document.getElementById('sendFriendRequest').addEventListener('click', async event => {
//     console.log('salut')
//     event.preventDefault();
//     const userInput = document.getElementById('friendSearched').value;
//     try {
//         let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
//             'username' : userInput,
//         })
//     }
//     catch (error) {
//         console.log(error);
//         if (error.code === 404)
//             document.getElementById('searchResults').innerText = 'user not found';
//     }
// })

async function friendListInit(){
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/friends/`)
        .then(data => {
            const resultDiv = document.getElementById('knownFriends');
            if (!data.count)
                resultDiv.innerText = "you don't have any friends";
            else{
                resultDiv.innerText = "";
                for (let friend of data.results){   
                    const friend1 = friend.friends[0];
                    const friend2 = friend.friends[1];
                    resultDiv.innerHTML += `<div class="friendRequestBlock" id="friend${friend.id}">\
                    <div>${friend1 === userInformations.username ? friend2 : friend1}</div>\
                    <button class='deleteFriend'>delete X</button></div>\n`;
                }
                // document.getElementById('knownFriends').innerText = "unable to fetch friend list";
            }
        })
        .catch(error => {
            console.log(error);
        })
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/received/`);
        const friendRequestsDiv = document.getElementById('friendRequests');
        if (data.count === 0){
            friendRequestsDiv.innerText = 'no pending friend requests';
            document.getElementById('innerFriendRequests-tab').innerText = 'Friend Requests';
        }
        else if (data.count){
            document.getElementById('innerFriendRequests-tab').innerText = `Friend Requests (${data.count})`;
            for (result of data.results){
                const requestDiv = document.createElement('div');
                requestDiv.id = result.id;
                friendRequestsDiv.appendChild(requestDiv);
                await loadContent('/friends/friendRequestBlock.html', `${requestDiv.id}`);
                requestDiv.querySelector('.senderUsername').innerText = result.sender.username;
            }
        }
        data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'GET');
        const sentFriendRequestsDiv = document.getElementById('sentFriendRequests');
        if (data.count === 0){
            sentFriendRequestsDiv.innerText = 'no sent friend requests';
        }
        else if (data.count){
            sentFriendRequestsDiv.innerHTML = "sent friend requests:";
            for (result of data.results){
                const requestDiv = document.createElement('div');
                requestDiv.id = result.id;
                sentFriendRequestsDiv.appendChild(requestDiv);
                await loadContent('/friends/sentFriendRequestBlock.html', `${requestDiv.id}`);
                requestDiv.querySelector('.receiverUsername').innerText = result.receiver.username;
            }
        }
    }
    catch(error) {
        console.log(error);
    }
}


(async function deleteFriend(){
    await friendListInit();
    const deleteFriendButtons = document.querySelectorAll('.deleteFriend');
    console.log(deleteFriendButtons);
    for (let deleteFriendButton of deleteFriendButtons){
        if (!deleteFriendButton.listened){
            deleteFriendButton.addEventListener('click', async event => {
                try {
                    const friendshipId = `${deleteFriendButton.parentElement.id}`.substring(6);
                    let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friends/${friendshipId}/`, 'DELETE');
                    console.log('deleted friendship : ', friendshipId);
                    await friendListInit();

                }
                catch (error){
                    console.log(error);
                }
            })
        }
        deleteFriendButton.listened = true;
    }
})()
