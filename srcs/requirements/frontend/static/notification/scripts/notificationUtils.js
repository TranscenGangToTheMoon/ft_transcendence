
function displayBadges(){
    if (userInformations.notifications){
        let totalNotifications = 0;
        for (let type in userInformations.notifications){
            if (!userInformations.notifications[type] || type === 'all') continue;
            totalNotifications += userInformations.notifications[type];
            for (let badgeDiv of badgesDivs[type]){
                addNotificationIndicator(badgeDiv, userInformations.notifications[type]);
            }
        }
        userInformations.notifications['all'] = totalNotifications;
        if (!totalNotifications) return;
        for (let allBadgesDiv of badgesDivs['all']){
            addNotificationIndicator(allBadgesDiv, totalNotifications);
        }
    }
}

function removeBadges(type){
    console.log('je remove pourtant')
    let toDelete = 0;
    userInformations.notifications[type] = 0;
    getBadgesDivs(document);
    for (let badgeDiv of badgesDivs[type]){
        let indicator = badgeDiv.querySelector(`.indicator`);
        if (indicator){
            toDelete = parseInt(indicator.innerText);
            console.log(toDelete);
            if (isNaN(toDelete))
                toDelete = 0;
            indicator.remove();
        }
    }
    if (toDelete){
        userInformations.notifications['all'] -= toDelete;
        if (!userInformations.notifications['all']){
            for (let badgeDiv of badgesDivs['all']){
                let indicator = badgeDiv.querySelector(`.indicator`);
                if (indicator)
                    indicator.remove();
            }
        }
        else {
            for (let allBadgesDiv of badgesDivs['all']){
                let indicator = allBadgesDiv.querySelector(`.indicator`);
                if (indicator)
                    indicator.innerText = userInformations.notifications['all'];
            }
        }
    }
}

function addNotificationIndicator(div, number){
    // console.log(div.cloneNode(true));
    if (!div.querySelector('.indicator')){
        const indicator = document.createElement('div');
        indicator.classList.add('indicator');
        indicator.innerText = number;
        div.appendChild(indicator);
    }
    else {
        div.querySelector('.indicator').innerText = number;
    }
}

function getBadgesDivs(container){
    badgesDivs['all'] = container.querySelectorAll('.all-badges');
    badgesDivs['friend_requests'] = container.querySelectorAll('.friend-badges');
    badgesDivs['chats'] = container.querySelectorAll('.chat-badges');
}


function handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance){
    img.addEventListener('click', async event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        try {
            let data = await apiRequest(getAccessToken(), '/' + target.url, target.method);
            if (target.url.includes('friend_request')){
                userInformations.notifications['friend_requests'] -= 1;
                if (userInformations.notifications['friend_requests'])
                    displayBadges();
                else
                    removeBadges('friend_requests');
                removeFriendRequest(target.url.match(/\/(\d+)\/?$/)[1]);
                if (target.method === 'POST')
                    addFriend(data);
            }
        }
        catch(error){
            console.log(error);
        }
        notification.clicked = true;
        dismissNotification(notification, toastInstance, toastContainer);
    })
}

function handleProfilePicNotification(target, img, notification, toastContainer, toastInstance){
    img.addEventListener('click', async event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        try {
            let data = await apiRequest(getAccessToken(), '/' + target.url, target.method);
            if (target.url.includes('friend_request')){
                userInformations.notifications['friend_requests'] -= 1;
                if (userInformations.notifications['friend_requests'])
                    displayBadges();
                else
                    removeBadges('friend_requests');
                removeFriendRequest(target.url.match(/\/(\d+)\/?$/)[1]);
                if (target.method === 'POST')
                    addFriend(data);
            }
        }
        catch(error){
            console.log(error);
        }
        notification.clicked = true;
        dismissNotification(notification, toastInstance, toastContainer);
    })
}

async function addTargets(notification, targets, toastInstance, toastContainer){
    console.log(targets);
    const notificationBody = notification.querySelector('.toast-body');
    Object.entries(targets).forEach(([i, target]) => {
        if (target.display_icon){
            var img = document.createElement('img');
            img.id = `notif${notification.id}-target${i}`;
            img.className = 'notif-img';
            img.src = target.display_icon;
            
            notificationBody.appendChild(img);
        }
        if (target.display_name){
            var button = document.createElement('button');
            button.id = `notif${notification.id}-nametarget${i}`;
            button.className = 'notif-button btn btn-secondary mx-1';
            button.innerText = target.display_name;

            notificationBody.appendChild(button);
        }
        if (target.type === 'api') {
            if (target.display_name === 'use')
                handleProfilePicNotification(target, button, notification, toastContainer, toastInstance);
            else
                handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance);
        }
        else if (target.type === 'url'){
            button.addEventListener('click', async () => {
                await navigateTo(target.url);
                notification.clicked = true;
                dismissNotification(notification, toastInstance, toastContainer);
            })
        }
    });
}

function dismissNotification(notification, toastInstance, toastContainer){
    toastInstance.hide();
    setTimeout (() => {
        displayedNotifications--;
        console.log(notification);
        toastContainer.removeChild(document.getElementById(notification.id));
        if (notificationQueue.length){
            let notif= notificationQueue.shift();
            console.log(notificationQueue);
            displayNotification(notif[0], notif[1], notif[2], notif[3], notif[4]);
        }
    }, 500);
}

async function displayNotification(icon=undefined, title=undefined, body=undefined, mainListener=undefined, target=undefined){

    if (displayedNotifications >= MAX_DISPLAYED_NOTIFICATIONS) {
        notificationQueue.push([icon, title, body, mainListener, target]);
        return;
    }
    const toastContainer = document.getElementById('toastContainer');

    await loadContent('/notification/notification.html', 'toastContainer', true);
    const notification = document.getElementById('notification');
    notification.id = `notification${notificationIdentifier}`;
    if (icon)
        notification.querySelector('img').src = icon;
    if (title)
        notification.querySelector('strong').innerText = title;
    if (body)
        notification.querySelector('.toast-body').innerText = body.length > 200 ? body.slice(0, 200) + "..." : body;
    if (mainListener)
        notification.addEventListener('click', event => {
            if (event.target.classList.contains('btn-close')) return;
            mainListener(event);
            notification.clicked = true;
            dismissNotification(notification, toastInstance, toastContainer);
        }, {once: true});
    const toastInstance = new bootstrap.Toast(notification);
    if (target)
        addTargets(notification, target, toastInstance, toastContainer);
    toastInstance.show();
    notificationIdentifier++;
    displayedNotifications++;
    setTimeout(() => {
        if (!notification.clicked){
            dismissNotification(notification, toastInstance, toastContainer)
        }
    }, 5000);
}

function emptyNotificationQueue(){
    notificationQueue = [];
    document.getElementById('toastContainer').innerHTML = '';
}