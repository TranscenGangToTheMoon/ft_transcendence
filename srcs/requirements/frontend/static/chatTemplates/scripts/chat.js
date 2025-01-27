function parsChatInfo(chat) {
	let chatInfo = {
		'chatId': chat.id,
		'target': chat.chat_with.username,
		'targetId': chat.chat_with.id,
		'targetAvatar': chat.chat_with.profile_picture,
		'lastMessage': null,
		'lastMessagesNotRead': 0,
		'chatMessageNext': null,
	};
	if (chat.last_message) {
		if (chat.last_message.content.length > 37){
			chatInfo.lastMessage = chat.last_message.content.slice(0, 37) + '...';
		}
		else chatInfo.lastMessage = chat.last_message.content;
		chatInfo.lastMessagesNotRead = chat.unread_messages;
	}
	return chatInfo;
}

async function getChatInstance(chatId) {
	try {
		clearChatError();
		let apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatId}/`, 'GET');
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		return apiAnswer;
	}
	catch (error) {
		console.log('Error chat:', error);
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		if (error.detail === undefined) error.detail = 'Error while loading chat';
		displayChatError(error, 'container');
		return undefined;
	}
}

function clearChatError() {
	var divError = document.getElementById('chatAlert');
	if (divError) divError.remove();
}

function displayChatError(error, idDiv) {
	let divToDisplayError = document.getElementById(idDiv);
	clearChatError();
	if (divToDisplayError) {
		var divError = document.createElement('div');
		divError.className = 'alert alert-danger';
		divError.id = 'chatAlert';
		divError.innerText = "Error: " + error.detail;
		divToDisplayError.appendChild(divError);
	}
	else {
		console.log('Error chat: div for chat error not found');
	}
}

async function closeChatView() {
	chatView = document.getElementById('chatView');
	if (!chatView) return;
	chatView.remove();
	await disconnect();
	openChat = {};
	userChat = {};
	chatView = document.getElementById('chatView');
}

async function disconnect() {
	if (typeof window.socket === 'undefined')	return;
	if (socket === null)	return;
	console.log("Chat: Closing the connection to the server...");
	socket.off();
	await socket.disconnect();
	socket = null;
}

async function connect(token, chatInfo) {
	clearChatError();
	if(typeof window.socket !== 'undefined' && window.socket != null && window.socket.connected) await disconnect();
	let socket = await io("/", {
		path: "/ws/chat/",
		transports: ['websocket'],
		auth: {
			"token": 'Bearer ' + token,
			"chatId": chatInfo.chatId,
		}
	});
	window.socket = socket;
	console.log("Chat: Connecting to the server...");
	setupSocketListeners(chatInfo);
}

function setupSocketListeners(chatInfo)
{
	const chatBox = document.getElementById('messages' + chatInfo.target);

	socket.off();
	
	socket.on("connect", () => {
		console.log("Chat: Connected to the chat server to talk with", chatInfo.target);
	});

	socket.on("connect_error", async (data) => {
		if (data.error === 401){
			console.log('Chat: Reattempting connection to the server...');
			await connect(await refreshToken(), chatInfo.chatId);
		}
		else {
			console.log('Error chat:', data);
			await closeChatTab(chatInfo);
			if (data.message === undefined) data.message = 'Error while connecting to the chat server';
			displayChatError({'code':data.error, 'detail': data.message}, 'container');
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Chat: Disconnected from the server");
	});
	
	socket.on("message", (data) => {
		let messageDiv = document.createElement('div');
		let messageContent = document.createElement('p');
		let messageAuthor = document.createElement('strong');
		messageDiv.appendChild(messageAuthor);
		messageDiv.appendChild(messageContent);
		messageDiv.style.display = 'flex';
		console.log("Message received: ", data);
		messagesNotRead = chatBox.querySelectorAll('.chatMessageNotRead');
		for (let message of messagesNotRead) {
			message.classList.remove('chatMessageNotRead');
		}
		if (chatBox === null) return;
		if (data.author === chatInfo.targetId) {
			messageAuthor.innerText = chatInfo.target + ': ';
		}
		else {
			messageAuthor.innerText = 'You: ';
		}
		messageContent.innerText = data.content;
		chatBox.insertAdjacentElement('beforeend', messageDiv);
		chatBox.scrollTop = chatBox.scrollHeight;
	});

	socket.on("error", async (data) => {
		console.log("Error received from chat server: ", data);
		if (data.error === 401){
			socket.emit('message', {'content': data.retry_content, 'token' : 'Bearer ' + await refreshToken(), 'retry': true});
		}
		else if (data.error === 409){
			await closeChatTab(chatInfo);
		}
		else {
			console.log('Error chat:', data);
			if (data.message === undefined) data.message = 'Error with chat server';
			await closeChatTab(chatInfo);
			displayChatError({'code':data.error, 'detail': data.message}, 'container');
		}
	});

	socket.on("chat-server", (data) => {
		console.log("Chat: Server message received: ", data);
	});
}

function displayMessages(chatInfo, chatMessages, isMore = false, method='afterbegin'){
	const chatBox = document.getElementById('messages'+chatInfo.target);
	chatMessages.forEach(element => {
		let messageDiv = document.createElement('div');
		let messageContent = document.createElement('p');
		let messageAuthor = document.createElement('strong');
		console.log('Chat: Displaying message:', element);
		if (element.author !== chatInfo.targetId) {
			messageAuthor.innerText = 'You: ';
		} else {
			messageAuthor.innerText = chatInfo.target + ': ';
			if (element.is_read === false) {
				messageContent.classList.add('chatMessageNotRead');
			}
		}
		messageContent.innerText = element.content;
		messageDiv.style.display = 'flex';
		messageDiv.appendChild(messageAuthor);
		messageDiv.appendChild(messageContent);
		chatBox.insertAdjacentElement(method, messageDiv);
	});
	if (!isMore)
		chatBox.scrollTop = chatBox.scrollHeight;
}

async function getMoreOldsMessages(chatInfo){
	if (!chatInfo.chatMessageNext) return;
	try {
		clearChatError();
		let apiAnswer = await apiRequest(getAccessToken(), chatInfo.chatMessageNext);
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		if (apiAnswer.count !== 0) displayMessages(chatInfo, apiAnswer.results, true);
		chatInfo.chatMessageNext = apiAnswer.next;
	}
	catch (error) {
		console.log('Error chat:', error);
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		if (error.detail === undefined) error.detail = 'Error while loading more old messages';
		displayChatError(error, 'messages' + chatInfo.target);
	}
}

async function loadOldMessages(chatInfo){
	try {
		clearChatError();
		console.log('Chat: Loading old messages');
		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/messages/`, 'GET');
		if (apiAnswer.detail){
			return {'code': 400, 'detail': apiAnswer.detail};
		};
		if (apiAnswer.count !== 0){
			displayMessages(chatInfo, apiAnswer.results);
			chatInfo.chatMessageNext = apiAnswer.next;
		}
		else {
			document.getElementById('messages'+ chatInfo.target).insertAdjacentHTML('afterbegin', `<div><p><strong>:</strong> Start the conversation ;)</p></div>`);
		}
	}
	catch (error) {
		return error;
	}
	return {'code': 200};
}

function createButtonClose(id){
	let buttonClose = document.createElement('button');
	buttonClose.id = id;
	buttonClose.className = 'btn-close';
	return buttonClose;
}

async function createChatUserCard(chatInfo) {
	verifChatCard = document.getElementById('chatListElement' + chatInfo.target);
	if (verifChatCard) return;
	if (!chatInfo) return;
	let chatUserCard = document.createElement('div');
	chatUserCard.id = 'chatListElement' + chatInfo.target;
	chatUserCard.classList.add('chatUserCard');
	chatUserCard.style.display = 'flex';
	chatsList.appendChild(chatUserCard);

	await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
	chatUserCard.querySelector('.chatUserCardAvatar').src = chatInfo.targetAvatar;
	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatInfo.target + ':';
	if (chatInfo.lastMessage === null) {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = 'Start the conversation ;)';
	}
	else {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatInfo.lastMessage);
	}
	var chatUserCardLastMessage = chatUserCard.querySelector('.chatUserCardLastMessage');
	if (chatInfo.lastMessagesNotRead)
		chatUserCardLastMessage.classList.add('chatMessageNotRead');
	chatUserCard.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
		e.preventDefault();
		try {
			clearChatError();
			const APIAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/`, 'DELETE');
			console.log('Chat: Chat deleted:', APIAnswer);
			if (APIAnswer && APIAnswer.detail) throw {'code': 400, 'detail': APIAnswer.detail};
			userInformations.notifications['chats'] -= chatInfo.lastMessagesNotRead;
			if (userInformations.notifications['chats'] <= 0)
				removeBadges('chats');
			else
				displayBadges();
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
		await openChatTab(chatInfo.chatId);
	});
}

async function getMoreChats() {
	if (!nextChatsRequest) return;
	try {
		clearChatError();
		let apiAnswer = await apiRequest(getAccessToken(), nextChatsRequest);
		if (apiAnswer.detail) {
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		if (apiAnswer.count !== 0) {
			chatBox = document.getElementById('chatsList');
			apiAnswer.results.forEach(async element => {
				data = parsChatInfo(element);
				await createChatUserCard(data);
			});
		}
		nextChatsRequest = apiAnswer.next;
	}
	catch (error) {
		console.log('Error chat:', error);
		if (error.detail === undefined) error.detail = 'Error while loading more chats';
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		displayChatError(error, 'chatsListError');
	}
}

async function displayChatsList(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML= '';
	try {
		clearChatError();
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		if (apiAnswer.count > 0) {
			for(element of apiAnswer.results) {
				console.log('Chat: Displaying chat:', element);
				data = parsChatInfo(element);
				await createChatUserCard(data);
			}
			nextChatsRequest = apiAnswer.next;
		}
		else {
			console.log('Chat: No chat found');
		}
	}
	catch(error) {
		console.log('Error chat:', error);
		if (error.code === 503 || error.code === 502) return;
		if (error.detail === undefined) error.detail = 'Error while loading chats list';
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		displayChatError(error, 'chatsListError');
	}
	chatListModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
	if (chatListModal && !chatListModal._isShown)
		chatListModal.show();
}

async function searchChatButton(username) {
	try{
		clearChatError();
		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${username}`);
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
	}
	catch(error) {
		console.log('Error chat:', error);
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		if (error.detail === undefined) error.detail = 'Error while searching chat';
		displayChatError(error, 'chatListError');
		return;
	}

	chatRequest = undefined;
	chatInfo = undefined;
	if (apiAnswer.count === 0)
	{
		console.log('Chat: Chat doesn\'t exist => creating chat');
		try {
			clearChatError();
			var chatRequest = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'POST', undefined, undefined, {'username': username, 'type':"private_message"});
			if (chatRequest.detail){
				throw {'code': 400, 'detail': chatRequest.detail};
			}
			chatInfo = parsChatInfo(chatRequest);
		}
		catch (error) {
			console.log('Error chat:', error);
			if (error.code === 404 && error.detail === undefined) error.detail = 'No User found';
			if (error.detail === undefined) error.detail = 'Error while creating chat';
			displayChatError(error, 'chatListError');
			return;
		}
		console.log('Chat: New chat created:', chatRequest);
	}
	else {
		if (lastClick === 'chatTab' + apiAnswer.results[0].chat_with.username + 'Link') {
			console.log('Chat: Chat already open');
			const chatModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
			chatModal.hide();
			return;
		}
		console.log('Chat: Chat already exist => loading chat');
		chatInfo = parsChatInfo(apiAnswer.results[0]);
	}
	document.getElementById('searchChatForm').reset();
	await displayChatsList();
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	if (buttonCollapseChat) {
		if (buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
			lastClick = undefined;
			buttonCollapseChat.click();
		}
	}
	await openChatTab(chatInfo.chatId);
}

function removeFirstInactiveChatTab() {
    let chatTabs = document.getElementById('chatTabs');
    let tabLinks = chatTabs.querySelectorAll('.nav-link');

    for (let tabLink of tabLinks) {
        if (!tabLink.classList.contains('active') && tabLinks.id !== 'chatGameTabLink') {
			console.log('Chat: Removing first inactive chat tab', tabLink.id.slice(0, -4));
			chatTabs.querySelector('#' + tabLink.id.slice(0, -4) + "Button").click();
			return ;
        }
    }
    return null;
}

async function closeChatTab(chatInfo)
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	if (!chatActiveTab) return;
	if (chatActiveTab.id === 'chatTab' + chatInfo.target + 'Link') isTabActive = true;
	document.getElementById('chatTab' + chatInfo.target).remove();
	document.getElementById('chatBox' + chatInfo.target).remove();
	openChat[chatInfo.chatId] = undefined;
	userChat[chatInfo.targetId] = undefined;
	let lastTab = document.getElementById('chatTabs').lastElementChild;
	await disconnect();
	if (!lastTab) {
		lastClick = undefined;
		document.getElementById('chatView').remove();
	}
	else if (isTabActive) {
		lastClick = undefined;
		if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'true') {
			lastTab.querySelector('a').click();
		}
		else {
			lastClick = lastTab.querySelector('a').id;
		}
	}
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
	if (gameChatTab) {
		chatTabs.insertBefore(chatTab, gameChatTab);
	} else {
		chatTabs.appendChild(chatTab);
	}

    let chatBody = document.getElementById('chatBody');
    let chatBox = document.createElement('div');
    chatBox.id = idChatBox;
	chatBox.className = 'tab-pane fade show active';
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
	const tab = new bootstrap.Tab(chatTabLink);
	tab.show();

	lastClick = chatTabLink.id;

	await chatTabListener(chatInfo);
	await scrollMessagesListener(chatInfo);
	sendMessageListener(chatInfo);
}

async function chatTabListener(chatInfo)
{
	document.getElementById('chatTab' + chatInfo.target).addEventListener('click', async e => {
		e.preventDefault();
		if (e.target.id === 'chatTab' + chatInfo.target + 'Button') {
			await closeChatTab(chatInfo);
			return;
		}
		if (e.target.id === 'chatTab' + chatInfo.target + 'Link') {
			let buttonCollapseChat = document.getElementById('chatTabsCollapse');
			if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
				buttonCollapseChat.click();
				lastClick = undefined;
			}
			if (lastClick === e.target.id) return;
			lastClick = e.target.id;
			openChatTab(chatInfo.chatId);
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
		if (scrollPercentage <= 15 && !loading) {
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
		const message = this.querySelector('input').value;
		if (message === '') return;
		socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
		chatForm.reset();
	});
}

async function setChatView()
{
	if (document.getElementById('chatView')) return;
	await loadContent('/chatTemplates/chatTabs.html', 'container', true);
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	buttonCollapseChat.addEventListener('click', async e => {
		e.preventDefault();
		if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'true') {
			if (!lastClick) return;
			let lastTab = document.getElementById(lastClick);
			if (lastTab) {
				lastClick = undefined;
				lastTab.click();
			}
		}
		else {
			await disconnect();
		}
	});
	logOutButton = document.getElementById('logOut');
	if (logOutButton) {
		logOutButton.addEventListener('click', async () => {
		closeChatView();
		});
	}
}

async function openChatTab(chatId)
{
	chat = await getChatInstance(chatId);
	if (!chat) return;
	userInformations.notifications['chats'] -= chat.unread_messages;
	if (userInformations.notifications['chats'] <= 0)
		removeBadges('chats');
	else
		displayBadges();
	chatInfo = parsChatInfo(chat);
	chatTabs = document.getElementById('chatTabs');
	if (!chatTabs) {
		await setChatView();
	}
	else {
		if (openChat[chatInfo.chatId] && openChat[chatInfo.chatId].target !== chatInfo.target) {
			await closeChatTab(openChat[chatInfo.chatId]);
			await setChatView();
			
		}
		if (!openChat[chatId] && chatTabs.childElementCount >= 4){
			removeFirstInactiveChatTab();
		}
	}
	
	if (!document.getElementById('chatTab'+chatInfo.target))
	{
		console.log('Chat: Creating chat tab');
		openChat[chatInfo.chatId] = chatInfo;
		userChat[chatInfo.targetId] = chatInfo.chatId;
		await createChatTab(chatInfo);
	}
	try {
		messageBox = document.getElementById('messages'+chatInfo.target);
		messageBox.innerHTML = '';
		res = await loadOldMessages(chatInfo);
		if (res.code !== 200)
			throw (res);
	}
	catch (error) {
		console.log('Error chat:', error);
		await closeChatTab(chatInfo);
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		if (error.detail === undefined) error.detail = 'Error while loading old messages';
		displayChatError(error, 'container');
		return;
	}
	const chatModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
	if (chatModal && chatModal._isShown) {
		chatModal.hide();
		document.getElementById('searchChatForm').reset();
	}
	await connect(getAccessToken(), chatInfo);
}

async function displayGameInviteInChat(inviteInfo) {
	chatInfo = openChat[userChat[inviteInfo.user]];
	var messagesDiv = document.getElementById('messages'+chatInfo.target);
	if (!messagesDiv) {
		return;
	}
	var chatInviteGameBox = document.getElementById('chatInviteGameBox' + inviteInfo.user);
	if (chatInviteGameBox) chatInviteGameBox.remove();
	chatInviteGameBox = document.createElement('div');
	messagesDiv.appendChild(chatInviteGameBox);
	chatInviteGameBox.id = 'chatInviteGameBox' + inviteInfo.user;
	chatInviteGameBox.classList.add('chatInviteGameBox');
	await loadContent('/chatTemplates/chatInviteGameBox.html', 'chatInviteGameBox' + inviteInfo.user);
	chatInviteGameBox.querySelector('.chatInviteGameUsername').innerText = chatInfo.target;
	chatInviteGameBox.querySelector('.chatInviteGameType').innerText = inviteInfo.game_mode;
	chatInviteGameBox.querySelector('.chatInviteGameButton').addEventListener('click', async e => {
		e.preventDefault();
		console.log('Chat: Accepting game invite');
		await navigateTo(inviteInfo.game_url.slice(0, -1));
	});
	chatInviteGameBox.querySelector('.chatInviteGameDelete').addEventListener('click', async e => {
		e.preventDefault();
		e.target.parentElement.parentElement.remove();
	});
	messagesDiv.scrollTop = messagesDiv.scrollHeight;
}


var lastClick = undefined;
if (typeof openChat === 'undefined')
	var openChat = {};
if (typeof userChat === 'undefined')
	var userChat = {};
if (typeof loading === 'undefined')
	var loading = false;
if (typeof nextMessagesRequest === 'undefined')
	var nextMessagesRequest = undefined;
if (typeof nextChatsRequest === 'undefined')
	var nextChatsRequest = undefined;

loadScript('/chatTemplates/scripts/chatGame.js');

document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	displayChatsList(e.target.value);
});

document.getElementById('searchChatButton').addEventListener('click', (e) => {
	e.preventDefault();
	let request = document.getElementById('searchChat').value;
	if (request === '') return;
	searchChatButton(request);
});

document.getElementById('chatsList').addEventListener('scroll', async event => {
	const chatsListBox = document.getElementById('chatsList');
	const scrollHeight = chatsListBox.scrollHeight;
	const clientHeight = chatsListBox.clientHeight;
	const scrollTop = chatsListBox.scrollTop;
	const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
	if (scrollPercentage >= 85 && !loading) {
		loading = true;
		await getMoreChats();
		loading = false;
	}
}, true);
