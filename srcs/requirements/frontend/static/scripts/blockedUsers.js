document.getElementById('modals').addEventListener('click', async event => {
    if (!event.target.listened && event.target.matches('#blockXavier')){
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
                'username': 'xavier',
            })
            initBlockedUsers();
        }
        catch (error) {
            console.log(error);
        }
        event.target.listened = true;
    }
    if (!event.target.listened && event.target.matches('#createXavier')){
        try {
            let xavierToken = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST');
            xavierToken = await apiRequest(xavierToken.access, `${baseAPIUrl}/auth/register/`, 'PUT', undefined, undefined, {
                'username': 'xavier',
                'password': 'xavier'
            })
            localStorage.setItem('xavierToken', xavierToken.access);
            await apiRequest(xavierToken.access, `${baseAPIUrl}/users/me/`, 'GET');
        }
        catch(error) {
            console.log('error', error);
        }
        event.target.listened = true;
    }
    if (!event.target.listened && event.target.matches('#deleteXavier')){
        let xavierToken = localStorage.getItem('xavierToken');
        if (!xavierToken)
            return;
        try {
            await apiRequest(xavierToken, `${baseAPIUrl}/users/me/`, 'DELETE', undefined, undefined, {
                'password':'xavier'
            });
        }
        catch(error) {
            console.log('error', error);
        }
        event.target.listened = true;
    }
    if (!event.target.listened && event.target.matches('#blockJules')){
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
                'username': 'jules',
            })
            initBlockedUsers();
        }
        catch (error) {
            console.log(error);
        }
        event.target.listened = true;
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


