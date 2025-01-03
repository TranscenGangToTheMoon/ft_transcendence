if (document.getElementById('modals').friendListened !== true){
    document.getElementById('modals').friendListened = true;
    document.getElementById('modals').addEventListener('click', async function(event){
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
                    await loadSentFriendRequests();
            }
            catch (error) {
                console.log(error);
                if (error.code === 404)
                    document.getElementById('searchResults').innerText = 'user not found';
            }
        }
        if (event.target.matches('#simulateFriends')){
            const nb = document.getElementById('simulateNb').value;
            if (!nb) return;
            document.getElementById('loading').style.display = 'unset';
            for (let i = 0; i < nb; i++){
                try {
                    let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST');
                    data = await apiRequest(data.access, `${baseAPIUrl}/auth/register/guest/`, 'PUT', undefined, undefined, {
                        'username' : `test${localStorage.getItem('currentState') + i}`,
                        'password' : `password${i}`
                    });
                    await apiRequest(data.access, `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
                        'username' : 'flo',
                    })
                }
                catch (error){
                    console.log(error);
                }
            }
            document.getElementById('loading').style.display = 'none'
            await loadReceivedFriendRequests();
        }
        if (event.target.matches('.deleteFriend')){
            try {
                const friendshipId = `${event.target.parentElement.id}`.substring(6);
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friends/${friendshipId}/`, 'DELETE');
                console.log('deleted friendship : ', friendshipId);
                document.getElementById(event.target.parentElement.id).remove();
                const displayedFriends = getDisplayedFriends();
                if (displayedFriends < 15){
                    nextFriend = decrementOffset(nextFriend);
                    getMoreFriends();
                }
                if (displayedFriends === 0){
                    document.getElementById('knownFriends').innerText = "you don't have any friends"
                }   
            }
            catch (error){
                console.log(error);
            }
        }
    })
}

function decrementOffset(url) {
    if (!url) return;
    const urlObj = new URL(url);
    const params = urlObj.searchParams;

    const offset = parseInt(params.get('offset'), 10) || 0;
    if (offset > 0) {
        params.set('offset', offset - 1);
    }
    return urlObj.toString();
}

function getDisplayedFriendRequests(sent) {
    let pendingRequests = document.querySelectorAll('.friendRequestBlock.pending');
    if (sent) pendingRequests = document.querySelectorAll('friendRequestsBlock.sent')
    return pendingRequests.length;
}

function getDisplayedFriends(){
    let friends = document.querySelectorAll('.friendRequestBlock.knownFriend');
    return friends.length;
}

if (typeof nextFriendRequest === undefined)
    var nextFriendRequest;
if (typeof nextFriend === undefined)
    var nextFriend;
if (typeof nextSentFriendRequest === undefined)
    var nextSentFriendRequest;
if (typeof loading === undefined)
    var loading = false;

async function getMoreFriendRequests() {
    if (!nextFriendRequest) return;
    nextFriendRequest = `${nextFriendRequest.substring(0, 4)}s${nextFriendRequest.substring(4)}`
    try {
        let data = await apiRequest(getAccessToken(), nextFriendRequest);
        const friendRequestsDiv = document.getElementById('friendRequests');
        nextFriendRequest = data.next;
        for (result of data.results){
            const requestDiv = document.createElement('div');
            requestDiv.id = `fr${result.id}`;
            friendRequestsDiv.appendChild(requestDiv);
            await loadContent('/friends/friendRequestBlock.html', `${requestDiv.id}`);
            requestDiv.querySelector(`.senderUsername`).innerText = result.sender.username;
        }
    }
    catch (error) {
        console.log(error);
    }
}

async function getMoreFriends() {
    if (!nextFriend) return;
    nextFriend = `${nextFriend.substring(0, 4)}s${nextFriend.substring(4)}`
    try {
        let data = await apiRequest(getAccessToken(), nextFriend);
        const resultDiv = document.getElementById('knownFriends');
        nextFriend = data.next;
        for (result of data.results){
            const friend1 = result.friends[0];
            const friend2 = result.friends[1];
            resultDiv.innerHTML += `<div class="friendRequestBlock knownFriend" id="friend${result.id}">\
            <div>${friend1 === userInformations.username ? friend2 : friend1}</div>\
            <button class='deleteFriend'>delete X</button></div>\n`;
        }
    }
    catch (error) {
        console.log(error);
    }
}

async function getMoreSentFriendRequests() {
    if (!nextSentFriendRequest) return;
    nextSentFriendRequest = `${nextSentFriendRequest.substring(0, 4)}s${nextSentFriendRequest.substring(4)}`
    try {
        let data = await apiRequest(getAccessToken(), nextSentFriendRequest);
        const friendRequestsDiv = document.getElementById('sentFriendRequests');
        nextSentFriendRequest = data.next;
        for (result of data.results){
            const requestDiv = document.createElement('div');
            requestDiv.id = `fr${result.id}`;
            friendRequestsDiv.appendChild(requestDiv);
            await loadContent(`/friends/sentFriendRequestBlock.html`, `${requestDiv.id}`);
            requestDiv.querySelector(`.receiverUsername`).innerText = result.receiver.username;
        }
    }
    catch (error) {
        console.log(error);
    }
}

document.addEventListener('scroll', async event => {
    if (event.target.id === 'friendRequests'){
        const friendRequests = document.getElementById('friendRequests');
        const scrollHeight = friendRequests.scrollHeight;
        const clientHeight = friendRequests.clientHeight;
        const scrollTop = friendRequests.scrollTop;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        if (scrollPercentage >= 75 && !loading) {
            loading = true;
            await getMoreFriendRequests();
            loading = false;
        }
    }
    if (event.target.id === 'sentFriendRequests'){
        const friendRequests = document.getElementById('sentFriendRequests');
        const scrollHeight = friendRequests.scrollHeight;
        const clientHeight = friendRequests.clientHeight;
        const scrollTop = friendRequests.scrollTop;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        if (scrollPercentage >= 75 && !loading) {
            loading = true;
            await getMoreSentFriendRequests();
            loading = false;
        }
    }
    if (event.target.id === "knownFriends"){
        const friends = document.getElementById('knownFriends');
        const scrollHeight = friends.scrollHeight;
        const clientHeight = friends.clientHeight;
        const scrollTop = friends.scrollTop;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        if (scrollPercentage >= 75 && !loading) {
            loading = true;
            await getMoreFriends();
            loading = false;
        }
    }
}, true)

async function loadFriendList(){
    let data;
    try {
        data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friends/?limit=15&offset=0`);
    }
    catch (error){
        console.log(error);
    }

    const resultDiv = document.getElementById('knownFriends');
    resultDiv.style.maxHeight = `${30 * MAX_DISPLAYED_FRIENDS}px`;
    nextFriend = data.next;
    if (!data.count)
        resultDiv.innerText = "you don't have any friends";
    else{
        resultDiv.innerText = "";
        for (let friend of data.results){
            const friend1 = friend.friends[0].username;
            const friend2 = friend.friends[1].username;
            resultDiv.innerHTML += `<div class="friendRequestBlock knownFriend" id="friend${friend.id}">\
            <div>${friend1 === userInformations.username ? friend2 : friend1}</div>\
            <button class='deleteFriend'>delete X</button></div>\n`;
        }
    }
}

function addFriend(friendInstance){
    const friendDiv = document.getElementById('knownFriends');
    friendDiv.innerText = '';
    const friend1 = friendInstance.friends[0].username;
    const friend2 = friendInstance.friends[1].username;
    friendDiv.innerHTML += `<div class="friendRequestBlock knownFriend" id="friend${friendInstance.id}">\
            <div>${friend1 === userInformations.username ? friend2 : friend1}</div>\
            <button class='deleteFriend'>delete X</button></div>\n`;
}

function removeFriend(friendInstance){
    console.log(friendInstance);
    document.getElementById(`friend${friendInstance.id}`).remove();
    const friendListDiv = document.getElementById('knownFriends');
    if (!friendListDiv.querySelector('div'))
        friendListDiv.innerText = "You don't have any friends";
}

async function addFriendRequest(result){
    const friendRequestTitleDiv = document.getElementById('friendRequestsTitle');
    friendRequestTitleDiv.innerText = 'friend requests:';
    const friendRequestsDiv = document.getElementById('friendRequests');
    const requestDiv = document.createElement('div');
    requestDiv.id = `fr${result.id}`;
    if (document.getElementById(result.id)) return;
    friendRequestsDiv.appendChild(requestDiv);
    await loadContent('/friends/friendRequestBlock.html', `${requestDiv.id}`);
    requestDiv.querySelector('.senderUsername').innerText = result.sender.username;
}

async function removeFriendRequest(id){
    // const friendRequestsDiv = document.getElementById('friendRequests');
    // console.log(friendRequestsDiv);
    // console.log(`#fr${id}`, friendRequestsDiv.querySelector(`#fr${id}`));
    const friendRequestDiv = document.getElementById(`fr${id}`);
    console.log(friendRequestDiv);
    if (friendRequestDiv)
        friendRequestDiv.remove();
}

async function loadReceivedFriendRequests(){
    let data;
    try {
        data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/received/`);
    }
    catch(error){
        console.log(error);
    }
    nextFriendRequest = data.next;
    const friendRequestsDiv = document.getElementById('friendRequests');
    friendRequestsDiv.style.maxHeight = `${MAX_DISPLAYED_FRIEND_REQUESTS * 30}px`
    const friendRequestTitleDiv = document.getElementById('friendRequestsTitle');
    if (data.count === 0){
        friendRequestTitleDiv.innerText = 'no pending friend requests';
    }
    else if (data.count){
        friendRequestsDiv.innerHTML = "";
        friendRequestTitleDiv.innerText = 'friend requests:';
        for (result of data.results){
            const requestDiv = document.createElement('div');
            requestDiv.id = `fr${result.id}`;
            friendRequestsDiv.appendChild(requestDiv);
            await loadContent('/friends/friendRequestBlock.html', `${requestDiv.id}`);
            requestDiv.querySelector('.senderUsername').innerText = result.sender.username;
        }
    }
}

async function loadSentFriendRequests(){
    let data;
    try {
        data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'GET');
    }
    catch (error){
        console.log(error);
    }
    nextSentFriendRequest = data.next;
    const requestsDiv = document.getElementById('sentFriendRequests');
    requestsDiv.style.maxHeight = `${MAX_DISPLAYED_FRIEND_REQUESTS * 30}px`
    const requestsDivTitle = document.getElementById('sentFriendRequestsTitle');
    if (data.count === 0){
        requestsDivTitle.innerText = 'no sent friend requests';
    }
    else if (data.count){
        requestsDiv.innerHTML = "";
        requestsDivTitle.innerText = "sent friend requests:";
        for (result of data.results){
            const requestDiv = document.createElement('div');
            requestDiv.id = `fr${result.id}`;
            requestsDiv.appendChild(requestDiv);
            await loadContent('/friends/sentFriendRequestBlock.html', `${requestDiv.id}`);
            requestDiv.querySelector('.receiverUsername').innerText = result.receiver.username;
        }
    }
}

async function  initFriendModal(){
    await loadFriendList();
    const friendRequestsTab = document.getElementById('innerFriendRequests-tab');
    if (friendRequestsTab.classList.contains('active')){
        await loadReceivedFriendRequests();
        await loadSentFriendRequests();
        friendRequestsTab.clicked = true;
    }
    else if (friendRequestsTab.clicked){
        friendRequestsTab.clicked = false;
        friendRequestsTab.addEventListener('click', async ()=>{
            this.clicked = true;
            await loadReceivedFriendRequests();
            await loadSentFriendRequests();
        }, {once:true});
    }
}

// initFriendModal();