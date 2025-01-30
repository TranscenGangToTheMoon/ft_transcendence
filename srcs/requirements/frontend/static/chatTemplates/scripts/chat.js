//==========Utils==========

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

// =========Server==========

async function disconnect() {
	console.log('Chat: Disconnecting from the chat server');
	if (typeof window.socket === 'undefined')	return;
	if (socket === null)	return;
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
	setupSocketListeners(chatInfo);
}

function setupSocketListeners(chatInfo)
{
	const chatBox = document.getElementById('messages' + chatInfo.target);
	if (chatBox === null) return;

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
		console.log("Message received: ", data);
		if (chatBox === null) return;
		messagesNotRead = chatBox.querySelectorAll('.chatMessageNotRead');
		for (let message of messagesNotRead) {
			message.classList.remove('chatMessageNotRead');
		}
		chatBox.insertAdjacentElement('beforeend', createMessage(data, chatInfo));
		chatBox.scrollTop = chatBox.scrollHeight;
	});

	socket.on("error", async (data) => {
		console.log("Error received from chat server: ", data);
		if (data.error === 401){
			socket.emit('message', {'content': data.retry_content, 'token' : 'Bearer ' + await refreshToken(), 'retry': true});
		}
		if (data.error === 404 || data.error === 403) {
			if (data.message === undefined) data.message = 'Chat not found';
			await closeChatTab(chatInfo);
			displayChatError({'code':data.error, 'detail': data.message}, 'container');
		}
	});

	socket.on("chat-server", (data) => {
		console.log("Chat: Server message received: ", data);
	});
}


//==========ChatListView==========

function closeChatListModal() {
	const chatModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
	if (chatModal && chatModal._isShown) {
		chatModal.hide();
		document.getElementById('searchChatForm').reset();
	}
}

async function createChatUserCard(chatInfo) {
	verifChatCard = document.getElementById('chatListElement' + chatInfo.target);
	if (verifChatCard) return;
	if (!chatInfo) return;
	let chatUserCard = document.createElement('div');
	chatsList.appendChild(chatUserCard);
	await setChatUserCard(chatInfo, chatUserCard);
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
		if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
		if (error.detail === undefined) error.detail = 'Error while loading chats list';
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
	removeChatCollapse();
	if (apiAnswer.count === 0)
	{
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
	}
	else {
		let chatTabLink = 'chatTab' + apiAnswer.results[0].chat_with.username + 'Link';
		if (lastClick === chatTabLink) {
			closeChatListModal();
			return;
		}
		let chatTab = document.getElementById(chatTabLink);
		if (chatTab) {
			chatTab.click();
			return;
		}
		chatInfo = parsChatInfo(apiAnswer.results[0]);
	}
	document.getElementById('searchChatForm').reset();
	await displayChatsList();
	await openChatTab(chatInfo.chatId);
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
				await setChatUserCard(data);
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

// =========ChatMessage==========

function displayMessages(chatInfo, chatMessages, isMore = false){
	const chatBox = document.getElementById('messages'+chatInfo.target);
	chatMessages.forEach(element => {
		chatBox.insertAdjacentElement('afterbegin', createMessage(element, chatInfo));
	});
	if (!isMore)
		chatBox.scrollTop = chatBox.scrollHeight;
}

async function displayGameInviteInChat(inviteInfo) {
	chatInfo = openChat[userChat[inviteInfo.user]];
	if (!chatInfo) return;
	var messagesDiv = document.getElementById('messages'+chatInfo.target);
	if (!messagesDiv) return;
	createChatGameInviteMessage(inviteInfo, messagesDiv);
	
	messagesDiv.scrollTop = messagesDiv.scrollHeight;
	chatInviteGameBox.querySelector('.chatInviteGameButton').addEventListener('click', async e => {
		e.preventDefault();
		await navigateTo(inviteInfo.game_url.slice(0, -1));
	});
	chatInviteGameBox.querySelector('.chatInviteGameDelete').addEventListener('click', async e => {
		e.preventDefault();
		e.target.parentElement.parentElement.remove();
	});
}

async function getMoreOldsMessages(chatInfo){
	if (!chatInfo.chatMessageNext) return;
	try {
		clearChatError();
		let apiAnswer = await apiRequest(getAccessToken(), chatInfo.chatMessageNext);
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		if (apiAnswer.count !== 0) {
			displayMessages(chatInfo, apiAnswer.results, true);
			const chatBox = document.getElementById('messages'+chatInfo.target);
			chatBox.scrollTop = chatBox.scrollTop * 0.7;
		}
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

// =========ChatView==========

function removeFirstInactiveChatTab() {
	for (let key in openChat) {
		openedChat = openChat[key];
		tabLink = document.getElementById('chatTab' + openedChat.target + 'Link');
		if (tabLink && !tabLink.classList.contains('active')) {
			closeChatTab(openedChat)
			return;
		}
	}
	return null;
}

async function closeChatTab(chatInfo)
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
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
		let chatCollapseButton = document.getElementById('chatTabsCollapse');
		if (chatCollapseButton.getAttribute('aria-expanded') === 'false') {
			lastClick = lastTab.querySelector('a').id;
			lastTab.querySelector('a').classList.add('active');
			if (lastTab.id === 'chatGameTab') {
				document.getElementById('chatGameBox').classList.add('active');
			}
			else {
				document.getElementById(lastTab.querySelector('a').getAttribute('aria-controls')).classList.add('active');
			}
		}
		else {
			lastClick = undefined;
			lastTab.querySelector('a').click();
		}
	}
}

function removeChatCollapse() {
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
		buttonCollapseChat.click();
	}
}

async function closeChatView() {
	chatView = document.getElementById('chatView');
	if (!chatView) return;
	chatView.remove();
	await disconnect();
	openChat = {};
	userChat = {};
}

async function setChatView()
{
	if (document.getElementById('chatView')) return;
	await loadContent('/chatTemplates/chatTabs.html', 'container', true);

	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	buttonCollapseChat.addEventListener('click', async e => {
		console.log('Chat: Collapse chat', buttonCollapseChat.getAttribute('aria-expanded'));
		if (!buttonCollapseChat) return;
		if (buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
			await disconnect();
		}
	});

	let buttonTabsAdd = document.getElementById('chatTabsAdd');
	buttonTabsAdd.addEventListener('click', async e => {
		e.preventDefault();
		await displayChatsList();
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
		if (!openChat[chatId] && chatTabs.childElementCount >= 3){
			removeFirstInactiveChatTab();
		}
	}

	if (!document.getElementById('chatTab'+chatInfo.target))
	{
		openChat[chatInfo.chatId] = chatInfo;
		userChat[chatInfo.targetId] = chatInfo.chatId;
		await createChatTab(chatInfo);
	}
	closeChatListModal();
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	if (buttonCollapseChat && buttonCollapseChat.getAttribute('aria-expanded') === 'true') {
		try {
			userInformations.notifications['chats'] -= chatInfo.lastMessagesNotRead;
			if (userInformations.notifications['chats'] <= 0)
				removeBadges('chats');
			else
				displayBadges();
			messageBox = document.getElementById('messages'+chatInfo.target);
			messageBox.innerHTML = '';
			res = await loadOldMessages(chatInfo);
			if (res.code !== 200)
				throw (res);
			await connect(getAccessToken(), chatInfo);
		}
		catch (error) {
			console.log('Error chat:', error);
			await closeChatTab(chatInfo);
			if (error.code === 404 && error.detail === undefined) error.detail = 'No chat found';
			if (error.detail === undefined) error.detail = 'Error while loading old messages';
			displayChatError(error, 'container');
			return;
		}
	}
}

// =========Main==========

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

loadScript('/chatTemplates/scripts/chatElement.js');
loadScript('/chatTemplates/scripts/chatGame.js');

document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	if (e.key === 'Escape') return;
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