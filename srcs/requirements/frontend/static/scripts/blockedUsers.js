if (!document.getElementById('modals').blockListened){
    document.getElementById('modals').blockListened = true;
    document.getElementById('modals').addEventListener('click', async event => {
        if (event.target.matches('#simulateBlock')){
            const blockNb = document.getElementById('blockedNb').value;
            console.log(blockNb)
            if (!blockNb) return;
            for (let i = 0; i < blockNb; i++){
                try {
                    let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, "POST");
                    data = await apiRequest(data.access, `${baseAPIUrl}/auth/register/`, 'POST', undefined, undefined, {
                        'username' : `test${localStorage.getItem('currentState') + i}`,
                        'password' : 'test'
                    })
                    data = await apiRequest(data.access, `${baseAPIUrl}/users/me/`);
                    await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
                        'user_id' : data.id,
                    })
                }
                catch (error){
                    console.log('error', error);
                }
            }
            initBlockedUsers();
        }
    })
}

if (typeof window.nextBlocked === undefined){
    var nextBlocked;
}
if (typeof loading === undefined){
    var loading = false;
}

document.addEventListener('scroll', async event => {
    if (event.target.id === 'blockedUsersList'){
        const Blocked = document.getElementById('blockedUsersList');
        const scrollHeight = Blocked.scrollHeight;
        const clientHeight = Blocked.clientHeight;
        const scrollTop = Blocked.scrollTop;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        if (scrollPercentage >= 75 && !loading) {
            loading = true;
            await getMoreBlocked();
            loading = false;
        }
    }
}, true);

async function getMoreBlocked(){
    if (!nextBlocked) return;
    try {
        let data = await apiRequest(getAccessToken(), nextBlocked, 'GET');
        const blockedUsersDiv = document.getElementById('blockedUsersList');
        nextBlocked = data.next;
        for (let blockedUser of data.results){
            const blockedUserDiv = document.createElement('div');
            blockedUserDiv.id = `blocked${blockedUser.id}`;
            blockedUsersDiv.appendChild(blockedUserDiv);
            await loadContent('/blockedUserBlock.html', `${blockedUserDiv.id}`);
            blockedUserDiv.querySelector('.blockedUsername').innerText = blockedUser.blocked.username;
        }
    }
    catch(error){
        console.log(error);
    }
}

function setBlockedTitle(title){
    document.getElementById('blockedTitle').innerText = title;
}

function getDisplayedBlockedUsers(){
    const blockedUsersDiv = document.querySelectorAll('.friendRequestBlock.block');
    return blockedUsersDiv.length;
}

function decrementNextBlock(url){
    if (!url) return;
    const urlObj = new URL(url);
    const params = urlObj.searchParams;

    const offset = parseInt(params.get('offset'), 10) || 0;
    if (offset > 0) {
        params.set('offset', offset - 1);
    }
    return urlObj.toString();
}

async function initBlockedUsers() {
    const blockedUsersDiv = document.getElementById('blockedUsersList');
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/?limit=15&offset=0`, 'GET');
        if (!data)
            return;
        if (data.count === 0)
            setBlockedTitle("you haven't blocked anyone");
        else {
            setBlockedTitle("Blocked users :");
            blockedUsersDiv.innerHTML = "";
            blockedUsersDiv.style.maxHeight = `${MAX_DISPLAYED_BLOCKED_USERS * 30}px`;
            nextBlocked = data.next;
            for (let blockedUser of data.results){
                const blockedUserDiv = document.createElement('div');
                blockedUserDiv.id = `blocked${blockedUser.id}`;
                blockedUsersDiv.appendChild(blockedUserDiv);
                await loadContent('/blockedUserBlock.html', `${blockedUserDiv.id}`);
                blockedUserDiv.querySelector('.blockedUsername').innerText = blockedUser.blocked.username;
            }
        }
    }
    catch (error) {
        console.log(error);
        blockedUsersDiv.innerText = "unable to retrieve blocked users list";
    }
    
}

initBlockedUsers();


