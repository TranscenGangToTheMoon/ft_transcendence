
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
    // console.log(lastTimeStamp);f
    if (lastTimeStamp && (now - lastTimeStamp < DEBOUNCE_TIME)){
        console.log('skip', data);
        if (data.event_code === 'lobby-update-participant' && data.data && data.data.team === 'Spectator')
            return 1;
        return 0;
    }

    eventTimestamps.set(data.event_code, now);
    // console.log('cala',eventTimestamps.get(data));
    return 1;
}

function removeSSEListeners(type){
    for (const [key, value] of SSEListeners) {
        if (key.includes(type)) {
            sse.removeEventListener(key, value);
            SSEListeners.delete(key);
            // console.log('removed sse listener:', key);
        }
    }
}

function addFriendSSEListeners(){
    sse.addEventListener('receive-friend-request', async event => {
        const friendListModal = bootstrap.Modal.getInstance(document.getElementById('friendListModal'));
        const isModalShown = friendListModal ? friendListModal._isShown : friendListModal;
        const isTabActive = document.getElementById('innerFriendRequests-tab').classList.contains('active');
        event = JSON.parse(event.data);
        console.log(event);
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
        console.log(event);
        if (!(bootstrap.Modal.getInstance(document.getElementById('friendListModal'))._isShown))
            await displayNotification(undefined, 'friend request', event.message);
        removeFriendRequest(event.data.id);
        console.log(event.data);
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
        console.log(event);
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
        console.log(event);
    })

    sse.addEventListener('invite-3v3', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        displayGameInviteInChat({'user': event.data.id, 'game_mode': 'clash', 'game_url': event.target.url, 'game_code': event.data.code});
        console.log(event);
    })

    sse.addEventListener('invite-1v1', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        displayGameInviteInChat({'user': event.data.id, 'game_mode': 'clash', 'game_url': event.target[0].url, 'game_code': event.data.code});
        console.log(event);
    })

    sse.addEventListener('invite-tournament', event => {
        event = JSON.parse(event.data);
        console.log(event);
    })

}

function addChatSSEListeners(){
    sse.addEventListener('receive-message', async event => {
        event = JSON.parse(event.data);
        chatId = event.data.chat_id;
        console.log(event);
        await displayNotification(undefined, 'message received', event.message, async event => {
            let buttonCollapseChat = document.getElementById('chatTabsCollapse');
			if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
				lastClick = undefined;
				buttonCollapseChat.click();
			}
            chatTab = document.getElementById(`chatTab${openChat[chatId].target}Link`);
            if (chatTab)
                chatTab.click();
            else
                await openChatTab(chatId);
        });
        userInformations.notifications['chats'] += 1;
        getBadgesDivs(document);
        displayBadges();
    })
}

function addSSEListeners(){

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
        const shownModal = document.querySelector('.modal.show[aria-modal="true"]');
        if (shownModal)
            return;
        displayMainAlert('Error', 'Unable to connect to Server Sent Events. Note that several services will be unavailable.');
    }

    addSSEListeners();
}