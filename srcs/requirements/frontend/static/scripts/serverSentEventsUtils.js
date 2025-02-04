
async function handleSSEListenerRemoval(url){
    if (window.pathName.includes('/lobby') && !url.includes('/lobby')){
        removeSSEListeners('lobby');
    }
    if (window.pathName.includes('/tournament')){
        removeSSEListeners('tournament');
    }
}

function checkEventDuplication(data){
    const now = Date.now();

    const lastTimeStamp = eventTimestamps.get(data.event_code);
    if (lastTimeStamp && (now - lastTimeStamp < DEBOUNCE_TIME)){
        if (data.event_code === 'lobby-update-participant' && data.data && data.data.team === 'Spectator')
            return 1;
        return 0;
    }

    eventTimestamps.set(data.event_code, now);
    return 1;
}

function removeSSEListeners(type){
    for (const [key, value] of SSEListeners) {
        if (key.includes(type)) {
            sse.removeEventListener(key, value);
            SSEListeners.delete(key);
        }
    }
}

function addFriendSSEListeners(){
    sse.addEventListener('receive-friend-request', async event => {
        const friendListModal = bootstrap.Modal.getInstance(document.getElementById('friendListModal'));
        const isModalShown = friendListModal ? friendListModal._isShown : friendListModal;
        const isTabActive = document.getElementById('innerFriendRequests-tab').classList.contains('active');
        event = JSON.parse(event.data);
        if (!isModalShown || !isTabActive) {
            await displayNotification(undefined, 'friend request', event.message, event => {
                const friendListModal = new bootstrap.Modal(document.getElementById('friendListModal'));
                friendListModal.show();
                document.getElementById('innerFriendRequests-tab').click();
            }, event.target);
            userInformations.notifications['friend_requests'] += 1;
            getBadgesDivs(document);
            displayBadges();
        }
        addFriendRequest(event.data);
    });

    sse.addEventListener('accept-friend-request', async event => {
        event = JSON.parse(event.data);
        if (!(bootstrap.Modal.getInstance(document.getElementById('friendListModal'))._isShown))
            await displayNotification(undefined, 'friend request', event.message);
        removeFriendRequest(event.data.id);
        addFriend(event.data);
    })

    sse.addEventListener('cancel-friend-request', async event => {
        event = JSON.parse(event.data);
        if (userInformations.notifications['friend_requests'])
            userInformations.notifications['friend_requests'] -= 1;
        if (!userInformations.notifications['friend_requests'])
            removeBadges('friend_requests');
        else{
            getBadgesDivs(document);
            displayBadges();
        }
        removeFriendRequest(event.data.id);
    })

    sse.addEventListener('reject-friend-request', async event => {
        event = JSON.parse(event.data);
        removeFriendRequest(event.data.id);
    })

    sse.addEventListener('delete-friend', event => {
        event = JSON.parse(event.data);
        removeFriend(event.data);
    })
}

function addInviteSSEListeners(){
    sse.addEventListener('invite-clash', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        displayGameInviteInChat({'user': event.data.id, 'game_mode': 'clash', 'game_url': event.target[0].url, 'game_code': event.data.code});
    })

    sse.addEventListener('invite-3v3', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        displayGameInviteInChat({'user': event.data.id, 'game_mode': 'clash', 'game_url': event.target.url, 'game_code': event.data.code});
    })

    sse.addEventListener('invite-1v1', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        displayGameInviteInChat({'user': event.data.id, 'game_mode': 'clash', 'game_url': event.target[0].url, 'game_code': event.data.code});
    })

    sse.addEventListener('invite-tournament', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
    })

}

function addChatSSEListeners(){
    sse.addEventListener('receive-message', async event => {
        event = JSON.parse(event.data);
        chatId = event.data.chat_id;
        await displayNotification(undefined, 'message received', event.message, async event => {
            let buttonCollapseChat = document.getElementById('chatTabsCollapse');
			if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
				lastClick = undefined;
				buttonCollapseChat.click();
			}

            if (openChat[chatId]){
                chatTab = document.getElementById(`chatTab${openChat[chatId].target}Link`);
                chatTab.click();
            }
            else
                await openChatTab(chatId);
        });
        userInformations.notifications['chats'] += 1;
        getBadgesDivs(document);
        displayBadges();
    })
}

function addSSEListeners(){
    sse.addEventListener('profile-picture-unlocked', event => {
        event = JSON.parse(event.data);
        displayNotification(event.data.small, 'achievement', event.message, undefined, [event.target[0]]);
    })

    sse.addEventListener('delete-user', async event => {
        event = JSON.parse(event.data);
        await logOut();
        setTimeout(async ()=>{
            displayMainAlert('Error', 'Your account has been deleted on another client. Switching to guest account.', 'danger', 5000)
        }, 500);
    })
    addFriendSSEListeners();
    addInviteSSEListeners();
    addChatSSEListeners();
}

function initSSE(){
    sse = new EventSource(`/sse/users/?token=${getAccessToken()}`);

    sse.onopen = () => {
        console.log('SSE connection initialized');
    }

    sse.onmessage = event => {
        let data = JSON.parse(event.data);
        console.log(data);
    }

    sse.onerror = async error => {
        console.log(error);
        displayMainAlert('Error', 'connection with server lost');
    }

    addSSEListeners();
}