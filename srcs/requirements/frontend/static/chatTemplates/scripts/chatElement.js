// ==========Utils==========

function createButtonClose(id){
	let buttonClose = document.createElement('button');
	buttonClose.id = id;
	buttonClose.className = 'btn-close';
	return buttonClose;
}

// ==========Chat User Card==========

function addChatUserCardListeners(chatUserCard, chatUserCardDeleteButton, chatUserCardLastMessage, chatInfo) {
	chatUserCard.addEventListener('mouseover', () => {
		chatUserCardDeleteButton.style.display = 'block';
	});
	chatUserCard.addEventListener('mouseout', () => {
		chatUserCardDeleteButton.style.display = 'none';
	});
	chatUserCardDeleteButton.addEventListener('click',async e => {
		e.preventDefault();
		try {
			clearChatError();
			const APIAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/`, 'DELETE');
			console.log('Chat: Chat deleted:', APIAnswer);
			if (APIAnswer && APIAnswer.detail) throw {'code': 400, 'detail': APIAnswer.detail};
			chatUserCard.remove();
			await closeChatTab(chatInfo);
			displayChatsList();
		} catch(error) {
			console.log('Error chat:', error);
			if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
			if (error.detail === undefined) error.detail = 'Error when attempting to delete chat';
			displayChatError(error, 'chatsListError');
		}
	});
	chatUserCard.addEventListener('click', async e => {
		if (e.target === chatUserCard.querySelector('.chatUserCardButtonDeleteChat')) return;
		chatUserCardLastMessage.classList.remove('chatMessageNotRead');
		let chatTab = document.getElementById('chatTab' + chatInfo.target + 'Link');
		if (chatTab) {
			if (chatTab.classList.contains('active')) {
				closeChatListModal();
				if (isChatCollapsed()) {
					chatTab.click();
				}
			}
			else {
				chatTab.click();
			}
			return;
		}
		removeChatCollapse();
		await openChatTab(chatInfo.chatId);
	});
}

async function setChatUserCard(chatInfo, chatUserCard) {
	chatUserCard.id = 'chatListElement' + chatInfo.target;
	chatUserCard.className = "chatUserCard bg-light bg-gradient d-flex position-relative p-1 border rounded gap-2";

	await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
	chatUserCard.querySelector('.chatUserCardAvatar').src = chatInfo.targetAvatar.small;
	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatInfo.target + ':';
	if (chatInfo.lastMessage === null) {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = 'Start the conversation ;)';
	}
	else {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatInfo.lastMessage);
	}
	var chatUserCardLastMessage = chatUserCard.querySelector('.chatUserCardLastMessage');
	if (chatInfo.unreadMessage) {
		console.log('setChatUserCard:', chatInfo.unreadMessage);
		console.log('setChatUserCard:', chatInfo.unreadMessage);
		chatUserCardLastMessage.classList.add('chatMessageNotRead');
	}
	let chatUserCardDeleteButton = chatUserCard.querySelector('.chatUserCardButtonDeleteChat');
	chatUserCardDeleteButton.style.display = 'none';
	addChatUserCardListeners(chatUserCard, chatUserCardDeleteButton, chatUserCardLastMessage, chatInfo);
}

// ==========Chat Message==========

function createMessage(message, chatInfo) {
	console.log('createMessage:', message);
	let messageDiv = document.createElement('div');
	let messageContent = document.createElement('p');
	let messageAuthor = document.createElement('strong');
	messageDiv.appendChild(messageContent);
	
	messageDiv.className = 'gap-1';
	if (message.author && message.author !== chatInfo.targetId) {
		messageAuthor.innerText = 'You: ';
	}
	else {
		messageAuthor.innerText = chatInfo.target + ': ';
		if (message.is_read === false) {
			messageContent.classList.add('chatMessageNotRead');
		}
	}
	messageContent.innerText = message.content;
	messageContent.insertAdjacentElement('afterbegin', messageAuthor);
	return messageDiv;
}

async function createChatGameInviteMessage(inviteInfo, chatMessagesDiv){
	var chatInviteGameBox = document.getElementById('chatInviteGameBox' + inviteInfo.user);
	if (chatInviteGameBox) chatInviteGameBox.remove();
	chatInviteGameBox = document.createElement('div');
	chatMessagesDiv.appendChild(chatInviteGameBox);
	chatInviteGameBox.id = 'chatInviteGameBox' + inviteInfo.user;
	chatInviteGameBox.className = 'chatInviteGameBox bg-info bg-gradient border border-dark rounded mb-1 p-1';
	await loadContent('/chatTemplates/chatInviteGameBox.html', 'chatInviteGameBox' + inviteInfo.user);
	chatInviteGameBox.querySelector('.chatInviteGameUsername').innerText = chatInfo.target;
	chatInviteGameBox.querySelector('.chatInviteGameType').innerText = inviteInfo.game_mode;

}

// ==========Chat Tab==========

async function chatTabListener(chatInfo)
{
	document.getElementById('chatTab' + chatInfo.target).addEventListener('click', async e => {
		e.preventDefault();
		if (e.target.id === 'chatTab' + chatInfo.target + 'Button') {
			await closeChatTab(chatInfo);
			return;
		}
		if (e.target.id === 'chatTab' + chatInfo.target + 'Link') {
			console.log('chatTabListener:', e.target.id, lastClick);
			let buttonCollapseChat = document.getElementById('chatTabsCollapse');
			if (buttonCollapseChat) {
				if (lastClick === e.target.id) {
					buttonCollapseChat.click();
					if (buttonCollapseChat.getAttribute('aria-expanded') === 'false') return;
				}
				else {
					removeChatCollapse();
				}
			}
			openChatTab(chatInfo.chatId);
			lastClick = e.target.id;
			return;
		}
	});
}

async function scrollMessagesListener(chatInfo) {
	messagesDiv = document.getElementById('messages'+chatInfo.target);
	messagesDiv.addEventListener('scroll', async event => {
		const scrollHeight = messagesDiv.scrollHeight;
		const clientHeight = messagesDiv.clientHeight;
		const scrollTop = messagesDiv.scrollTop;
		const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
		if (scrollPercentage <= 25 && !loading) {
			loading = true;
			await getMoreOldsMessages(chatInfo);
			loading = false;
		}
	});
}

function sendMessageListener(chatInfo) {
    const chatForm = document.getElementById('sendMessageForm'+chatInfo.target);
	chatForm.addEventListener('submit', async function (e) {
		e.preventDefault();
		if (socket && socket.disconnected === true) {
			await connect(getAccessToken(), chatInfo);
		}
		if (!socket) {
			await connect(getAccessToken(), chatInfo);
		}
		const message = this.querySelector('input').value;
		if (message === '') return;
		socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
		chatForm.reset();
	});
}

async function createChatTab(chatInfo) {
    let idChatTab = "chatTab" + chatInfo.target;
    let idChatBox = "chatBox" + chatInfo.target;

    let chatTabs = document.getElementById('chatTabs');

    let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
    if (chatActiveTab) {
        chatActiveTab.classList.remove('active');
        let lastTabId = chatActiveTab.getAttribute('href').substring(1);
        let lastChatBox = document.getElementById(lastTabId);
        if (lastChatBox) {
            lastChatBox.classList.remove('active');
        }
    }

    let chatTab = document.createElement('li');
    chatTab.id = idChatTab;
    chatTab.className = 'chatTab nav-item';
    chatTabs.setAttribute('role', 'presentation');

    let chatTabLink = document.createElement('a');
    chatTabLink.id = idChatTab + "Link";
    chatTabLink.innerText = chatInfo.target;
    chatTabLink.setAttribute('data-bs-toggle', 'tab');
    chatTabLink.setAttribute('role', 'tab');
    chatTabLink.setAttribute('href', "#" + idChatBox);
	chatTabLink.setAttribute('aria-controls', idChatBox);
	chatTabLink.setAttribute('aria-selected', 'true');
    chatTabLink.className = 'nav-link active';

    let chatTabButton = createButtonClose(idChatTab + "Button");
    chatTabLink.appendChild(chatTabButton);
    chatTab.appendChild(chatTabLink);
	gameChatTab = chatTabs.querySelector('#chatGameTab');
	chatTabs.appendChild(chatTab);

    let chatBody = document.getElementById('chatBody');
    let chatBox = document.createElement('div');
    chatBox.id = idChatBox;
	chatBox.className = 'message-box tab-pane fade show active';
    chatBox.setAttribute('role', 'tabpanel');
    chatBox.setAttribute('aria-labelledby', idChatTab);
    chatBody.appendChild(chatBox);

    await loadContent('/chatTemplates/chatBox.html', idChatBox);
	const messagesDiv = chatBox.querySelector('.messages');
	if (messagesDiv){
		messagesDiv.id = 'messages' + chatInfo.target;
	}
	const sendMessageForm = chatBox.querySelector('.sendMessageForm');
	if (sendMessageForm){
		sendMessageForm.id = 'sendMessageForm' + chatInfo.target;
	}

	lastClick = chatTabLink.id;

	await chatTabListener(chatInfo);
	await scrollMessagesListener(chatInfo);
	sendMessageListener(chatInfo);
}
