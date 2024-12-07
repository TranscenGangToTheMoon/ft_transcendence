if (!document.getElementById('modals').friendListened){
    this.friendListened = true;
    document.getElementById('modals').addEventListener('click', async function(event){
        event.preventDefault();
        if (event.target.matches('#sendFriendRequest')){
            event.preventDefault();
            const userInput = document.getElementById('friendSearched').value;
            try {
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
                    'username' : userInput,
                })
                if (data.detail){
                    document.getElementById('searchResults').innerText = data.detail;
                }
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
    console.log('je load')
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
                    resultDiv.innerHTML += `<div>${friend1 === userInformations.username ? friend2 : friend1}</div>\n`;
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