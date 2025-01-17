function parsChatInfo(chat) {
	let chatInfo = {
		'chatId': chat.id,
		'target': chat.chat_with.username,
		'targetId': chat.chat_with.id,
		'lastMessage': null,
		'isLastMessageRead': false,
		'chatMessageNext': null,
	};
	if (chat.last_message) {
		if (chat.last_message.content.length > 37){
			chatInfo.lastMessage = chat.last_message.content.slice(0, 37) + '...';
		}
		else chatInfo.lastMessage = chat.last_message.content;
		chatInfo.isLastMessageRead = chat.unread_messages === 0;
	}
	return chatInfo;
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
		divError.innerHTML = error;
		divToDisplayError.appendChild(divError);
	}
	else {
		console.log('Error chat: div for chat error not found');
	}
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
	if(typeof window.socket !== 'undefined')	await disconnect();
	let socket = await io("/", {
		path: "/ws/chat/",
		transports: ['websocket'],
		auth: {
			"token": 'Bearer ' + token,
			"chatId": chatInfo.chatId
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
		console.log("Chat: Connected to the chat server to chat with", chatInfo.target);
	});

	socket.on("connect_error", async (data) => {
		if (data.error === 401){
			console.log('Chat: Reattempting connection to the server...');
			await connect(await refreshToken(), chatInfo.chatId);
		}
		else {
			console.log('Error chat:', data);
			closeChatTab(chatInfo);
			if (data.message === undefined) data.message = 'Error while connecting to the chat server';
			displayChatError(data.message, 'container');
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Chat: Disconnected from the server");
	});
	
	socket.on("message", (data) => {
		console.log("Message received: ", data);
		if (chatBox === null) return;
		if (data.author === ''){
			var serverMessage = document.getElementById('serverMessage');
			if (serverMessage) serverMessage.remove();
			chatBox.insertAdjacentHTML('beforeend', `<div id='serverMessage'><p><strong>:</strong> ${data.content}</p></div>`);
		}
		else{
			if (data.author === chatInfo.targetId) {
				chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>${chatInfo.target}:</strong> ${data.content}</p></div>`);
			}
			else {
				chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>You:</strong> ${data.content}</p></div>`);
			}
		}
		chatBox.scrollTop = chatBox.scrollHeight;
	});

	socket.on("error", async (data) => {
		console.log("Error received from chat server: ", data);
		if (data.error === 401){
			socket.emit('message', {'content': data.retry_content, 'token' : 'Bearer ' + await refreshToken(), 'retry': true});
		}
		else {
			console.log('Error chat:', data);
			if (data.message === undefined) data.message = 'Error with chat server';
			closeChatTab(chatInfo);
			displayChatError(data.message, 'container');
		}
	});

	socket.on("debug", (data) => {
		console.log("Debug received: ", data);
	});
}

function displayMessages(chatInfo, chatMessages, method='afterbegin'){
	const chatBox = document.getElementById('messages'+chatInfo.target);
	chatMessages.forEach(element => {
		console.log(element);
		if (element.author === chatInfo.targetId) {
			chatBox.insertAdjacentHTML(method, `<div><p><strong>You:</strong> ${element.content}</p></div>`);
		} else {
			chatBox.insertAdjacentHTML(method, `<div><p><strong>${chatInfo.target}:</strong> ${element.content}</p></div>`);
		}
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
		if (apiAnswer.count !== 0) displayMessages(chatInfo, apiAnswer.results);
		chatInfo.chatMessageNext = apiAnswer.next;
	}
	catch (error) {
		console.log('Error chat:', error);
		if (error.detail === undefined) error.detail = 'Error while loading more old messages';
		displayChatError(error.detail, 'messages' + chatInfo.target);
	}
}

async function loadOldMessages(chatInfo){
	try {
		clearChatError();
		console.log('Chat: Loading old messages', chatInfo);
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
	let chatUserCard = document.createElement('div');
	chatUserCard.id = 'chatListElement' + chatInfo.target;
	chatUserCard.classList.add('chatUserCard');
	chatsList.appendChild(chatUserCard);

	await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
	if (!chatUserCard.querySelector('.chatUserCardTitleUsername') || !chatInfo.target) return;
	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatInfo.target + ':';
	if (chatInfo.lastMessage === null) {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = 'Start the conversation ;)';
	}
	else {
		chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatInfo.lastMessage);
	}
	var chatUserCardLastMessage = chatUserCard.querySelector('.chatUserCardLastMessage');
	if (chatInfo.isLastMessageRead === false)
		chatUserCardLastMessage.classList.add('chatMessageNotRead');
	chatUserCard.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
		e.preventDefault();
		try {
			clearChatError();
			const APIAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/`, 'DELETE');
			console.log('Chat: Chat deleted:', APIAnswer);
			if (APIAnswer && APIAnswer.detail) throw {'code': 400, 'detail': APIAnswer.detail};
			chatUserCard.remove();
			closeChatTab(chatInfo);
		} catch(error) {
			console.log('Error chat:', error);
			if (error.detail === undefined) error.detail = 'Error when attempting to delete chat';
			displayChatError(error.detail, 'chatsList');
		}
	});
	chatUserCard.addEventListener('click', async e => {
		if (e.target === chatUserCard.querySelector('.chatUserCardButtonDeleteChat')) return;
		chatUserCardLastMessage.classList.remove('chatMessageNotRead');
		await openChatTab(chatInfo);
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
				await createUserCard(data);
			});
		}
		nextMessagesRequest = apiAnswer.next;
	}
	catch (error) {
		console.log('Error chat:', error);
		if (error.detail === undefined) error.detail = 'Error while loading more chats';
		displayChatError(error.detail, 'chatsList');
	}
}

async function displayChatsList(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	try {
		clearChatError();
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (apiAnswer.detail){
			throw {'code': 400, 'detail': apiAnswer.detail};
		}
		if (apiAnswer.count > 0) {
			console.log('Chat: Chats found');
			apiAnswer.results.forEach(async element => {
				data = parsChatInfo(element);
				await createChatUserCard(data);
			});
			nextChatsRequest = apiAnswer.next;
		}
		else {
			console.log('Chat: No chat found');
		}
	}
	catch(error) {
		console.log('Error chat:', error);
		if (error.detail === undefined) error.detail = 'Error while loading chats list';
		displayChatError(error.detail, 'chatsList');
	}
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
		if (error.detail === undefined) error.detail = 'Error while searching chat';
		displayChatError(error.detail, 'searchChatForm');
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
		}
		catch (error) {
			console.log('Error chat:', error);
			if (error.detail === undefined) error.detail = 'Error while creating chat';
			displayChatError(error.detail, 'searchChatForm');
			return;
		}
		console.log('Chat: New chat created:', chatRequest);
	}
	else {
		console.log('Chat: Chat already exist => loading chat');
		try {
			clearChatError();
			var chatRequest = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${apiAnswer.results[0].id}/`, 'GET');
			if (chatRequest.detail){
				throw {'code': 400, 'detail': chatRequest.detail};
			}
		}
		catch (error) {
			console.log('Error chat:', error);
			if (error.detail === undefined) error.detail = 'Error while loading chat';
			displayChatError(error.detail, 'searchChatForm');
			return;
		}
		console.log('Chat: Chat loaded:', chatRequest);
	}
	document.getElementById('searchChatForm').reset();
	chatInfo = parsChatInfo(chatRequest);
	await displayChatsList();
	await openChatTab(chatInfo);
}

async function closeChatTab(chatInfo, )
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
	if (!chatActiveTab) return;
	if (chatActiveTab.id === 'chatTab' + chatInfo.target + 'Link') isTabActive = true;
	document.getElementById('chatTab' + chatInfo.target).remove();
	document.getElementById('chatBox' + chatInfo.target).remove();
	openChat['chatTab' + chatInfo.target] = undefined;
	let lastTab = document.getElementById('chatTabs').lastElementChild;
	if (!lastTab) {
		await disconnect();
		console.log('Chat: No more chat', lastTab);
		document.getElementById('chatView').remove();
	}
	else if (isTabActive) {
		await disconnect();
		lastTab.querySelector('a').click();
		await connect(getAccessToken(), openChat[lastTab.id]);
		lastClick = lastTab;
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
    chatTab.className = 'nav-item';
    chatTabs.setAttribute('role', 'presentation');

    let chatTabLink = document.createElement('a');
    chatTabLink.id = idChatTab + "Link";
    chatTabLink.innerHTML = chatInfo.target;
    chatTabLink.setAttribute('data-bs-toggle', 'tab');
    chatTabLink.setAttribute('role', 'tab');
    chatTabLink.setAttribute('href', "#" + idChatBox);
    chatTabLink.style = 'display:flex';
    chatTabLink.className = 'nav-link active';

    let chatTabButton = createButtonClose(idChatTab + "Button");
    chatTabLink.appendChild(chatTabButton);
    chatTab.appendChild(chatTabLink);
    chatTabs.appendChild(chatTab);

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

	lastClick = chatTabLink;

	closeTabListener(chatInfo);
	switchChatListner(chatInfo);
	sendMessageListener(chatInfo.target);
}

async function closeTabListener(chatInfo)
{
	let closeChatButton = document.getElementById('chatTab' + chatInfo.target + 'Button');
	closeChatButton.addEventListener('click', async e => {
		e.preventDefault();
		closeChatTab(chatInfo);
    });
}

async function switchChatListner(chatInfo)
{
	let chatTabLink = document.getElementById('chatTab' + chatInfo.target + 'Link');
	chatTabLink.addEventListener('click', async e => {
		e.preventDefault();
		if (lastClick === chatTabLink) return;
		if (e.target === document.getElementById('chatTab' + chatInfo.target + 'Button')) return;
		if (!document.getElementById('chatTabs').lastElementChild) return;
		lastClick = chatTabLink;
		await connect(getAccessToken(), chatInfo);
		console.log('Chat: Switching chat', e.target);
	});
}

function sendMessageListener(target) {
	console.log('Chat: Adding listener to chatForm', target);
    const chatForm = document.getElementById('sendMessageForm'+target);
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = this.querySelector('input').value;
			if (message === '') return;
            socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
            console.log('Chat: Message sent: ', message);
            chatForm.reset();
        });
    }
}

async function openChatTab(chatInfo)
{
	chatTabs = document.getElementById('chatTabs');
	if (!chatTabs) {
		await loadContent('/chatTemplates/chatTabs.html', 'container', true);
	}
	if (!document.getElementById('chatTab'+chatInfo.target))
	{
		openChat['chatTab' + chatInfo.target] = chatInfo;
		createChatTab(chatInfo);
		try {
			res = await loadOldMessages(chatInfo);
			if (res.code !== 200)
				throw (res);
		}
		catch (error) {
			console.log('Error chat:', error);
			closeChatTab(chatInfo);
			if (error.detail === undefined) error.detail = 'Error while loading old messages';
			displayChatError(error.detail, 'container');
			return;
		}
	}
	else {
		document.getElementById('chatTab'+chatInfo.target).querySelector('a').click();
	}
	const chatModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
	chatModal.hide();
	console.log(chatModal);
	await connect(getAccessToken(), chatInfo);
	document.getElementById('searchChatForm').reset();

	document.getElementById('logOut').addEventListener('click', async () => {
		await disconnect();
		openChat = {};
		document.getElementById('chatTabs').remove();
	});

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

var lastClick = undefined;
if (typeof openChat === 'undefined')
	var openChat = {};
if (typeof loading === 'undefined')
	var loading = false;
if (typeof nextMessagesRequest === 'undefined')
	var nextMessagesRequest = undefined;
if (typeof nextChatsRequest === 'undefined')
	var nextChatsRequest = undefined;

document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	if (e.target.value === '' && e.key === 'Backspace') return;
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
	console.log('scrolling in chatsList');
}, true);