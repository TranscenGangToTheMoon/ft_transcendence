document.getElementById('blockXavier').addEventListener('click', async event => {
    event.preventDefault();
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
            'username': 'xavier',
        })
        initBlockedUsers();
    }
    catch (error) {
        console.log(error);
    }
})

document.getElementById('blockJules').addEventListener('click', async event => {
    event.preventDefault();
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
            'username': 'jules',
        })
        initBlockedUsers();
    }
    catch (error) {
        console.log(error);
    }
})

async function initBlockedUsers() {
    const blockedUsersDiv = document.getElementById('blockedUsersList');
    blockedUsersDiv.innerHTML = "";
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'GET');
        if (!data)
            return;
        if (data.count === 0)
            blockedUsersDiv.innerText = "you haven't blocked anyone";
        else {
            for (blockedUser of data.results) {
                blockedUsersDiv.innerHTML += `<div class="blockedUser">${blockedUser.blocked.username} <button class="unblockUser" value="${blockedUser.id}" onclick="unblockUser(${blockedUser.id})">unblock</button></div>`;
            }
        }
    }
    catch (error) {
        console.log(error);
        blockedUsersDiv.innerText = "unable to retrieve blocked users list";
    }
    
}

async function unblockUser(userId) {
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/${userId}/`, 'DELETE');
        initBlockedUsers();
    }
    catch(error) {
        console.log(error);
    }
}

initBlockedUsers();


