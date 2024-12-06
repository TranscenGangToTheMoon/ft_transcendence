document.getElementById('modals').addEventListener('click', async event => {
    if (event.target.matches('#sendFriendRequest') && !event.target.listened){
        event.preventDefault();
        event.target.listened = true;
        const userInput = document.getElementById('friendSearched').value;
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
                'username' : userInput,
            })
        }
        catch (error) {
            console.log(error);
            if (error.code === 404)
                document.getElementById('searchResults').innerText = 'user not found';
        }
    }
})


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
    console.log('je load')
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/friends/`)
        .then(data => {
            if (!data.count)
                document.getElementById('knownFriends').innerText = "you don't have any friends";
            else{
                
                document.getElementById('knownFriends').innerText = "unable to fetch friend list";
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
        }
        else if (data.count){
            for (result of data.results){
                const requestDiv = document.createElement('div');
                requestDiv.id = result.id;
                requestDiv.style.backgroundColor = 'red';
                requestDiv.style.margin = '2px';
                console.log(requestDiv.id);
                friendRequestsDiv.appendChild(requestDiv);
                await loadContent('/friends/friendRequestBlock.html', `${requestDiv.id}`);
                requestDiv.querySelector('.senderUsername').innerText = result.sender.username;
            }
        }
    }
    catch(error) {
        console.log(error);
    }
}

friendListInit();