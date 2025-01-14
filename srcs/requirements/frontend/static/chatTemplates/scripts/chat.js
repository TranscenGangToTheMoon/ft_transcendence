function parsChatInfo(chat)
{
	let chatInfo = {
		'chatId': chat.id,
		'target': chat.chat_with.username,
		'targetId': chat.chat_with.id,
		'lastMessage': '< Say hi! >',
		'isLastMessageRead': false,
		'chatMessageNext': null,
	};
	if (chat.last_message) {
		if (chat.last_message.content.length > 37){
			chatInfo.lastMessage = chat.last_message.content.slice(0, 37) + '...';
		}
		else chatInfo.lastMessage = chat.last_message.content;
		chatInfo.isLastMessageRead = chat.last_message.is_read;
	}
	return chatInfo;
}

function disconnect() {
	if (typeof window.socket === 'undefined')	return;
	if (socket === null)	return;
	console.log("Closing the connection to the server...");
	socket.off();
	socket.disconnect();
	socket = null;
}

async function connect(token, chatInfo) {
	if(typeof window.socket !== 'undefined')	disconnect();
	console.log(chatInfo);
	let socket = await io("/", {
		path: "/ws/chat/",
		transports: ['websocket'],
		auth: {
			"token": 'Bearer ' + token,
			"chatId": chatInfo.chatId
		}
	});
	console.log(socket);
	window.socket = socket;
	console.log("Connecting to the server...");
	setupSocketListeners(chatInfo);
	return true;
}

function setupSocketListeners(chatInfo)
{
	const chatBox = document.getElementById('messages' + chatInfo.target);

	socket.off();
	
	socket.on("connect", () => {
		console.log("Connected to the server");
		console.log(socket);
	});

	socket.on("connect_error", async (data) => {
		console.log("Connection error: ", data);
		console.log('You\'ve got some issues mate');
		if (data.error === 401){
			console.log('reattempting connection');
			await connect(await refreshToken(), chatInfo.chatId);
		}
		else {
			console.log('You\'ve got some issues mate ', data);
			closeChatTab(chatInfo);
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
		closeChatTab(chatInfo);
	});
	
	socket.on("message", (data) => {
		console.log("Message received: ", data);
		console.log(chatInfo.targetId, chatInfo.target, data.author);
		if (chatBox === null) return;
		if (data.author === '')
			chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>:</strong> ${data.content}</p></div>`);
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
		console.log("Error received: ", data);
		if (data.error === 401){
			socket.emit('message', {'content': data.retry_content, 'token' : 'Bearer ' + await refreshToken(), 'retry': true});
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
		let apiAnswer = await apiRequest(getAccessToken(), chatInfo.chatMessageNext);
		if (apiAnswer.detail){
			console.log('Error:', apiAnswer.detail);
			return;
		}
		if (apiAnswer.count !== 0) displayMessages(chatInfo, apiAnswer.results);
		chatInfo.chatMessageNext = apiAnswer.next;
	}
	catch (error) {
		console.log('Something went wrong:', error);
	}
}

async function loadOldMessages(chatInfo){
	try {
		console.log('Loading old messages', chatInfo);
		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/messages`, 'GET');
		if (apiAnswer.detail){
			console.log('Error:', apiAnswer.detail);
			return {'code': 400, 'details': apiAnswer.detail};
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
		console.log(error);
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
	console.log(chatUserCard);
	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatInfo.target + ':';
	chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatInfo.lastMessage);
	if (chatInfo.isLastMessageRead === false)
		chatUserCard.querySelector('.chatUserCardLastMessage').classList.add('chatMessageNotRead');
	chatUserCard.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
		e.preventDefault();
		try {
			const APIAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/`, 'DELETE');
			if (APIAnswer.detail) return;
			chatUserCard.remove();
			console.log('Chat view deleted', lastClick);
		}catch(error){
			console.log(error);
		}
	});
	chatUserCard.addEventListener('click', async e => {
		if (lastClick === e.target.closest('#chatListElement' + chatInfo.target)) return;
		if (e.target === chatUserCard.querySelector('.chatUserCardButtonDeleteChat')) return;
		console.log("lastClickAfter: ",lastClick);
		await openChatTab(chatInfo);
	});
}

async function getMoreChats(){
	if (!nextChatsRequest) return;
	// if (nextChatsRequest.substring(0, 5) === "https") return;
	// nextChatsRequest = `${nextChatsRequest.substring(0, 4)}s${nextChatsRequest.substring(4)}`

	try {
		let apiAnswer = await apiRequest(getAccessToken(), nextChatsRequest);
		if (apiAnswer.details){
			console.log('Error:', apiAnswer.details);
			return;
		}
		if (apiAnswer.count !== 0) {
			chatBox = document.getElementById('chatsList');
			apiAnswer.results.forEach(async element => {
				console.log(element);
				data = parsChatInfo(element);
				await createUserCard(data);
			});
		}
		nextMessagesRequest = apiAnswer.next;
	}
	catch (error) {
		console.log('Something went wrong:', error);
	}
}

async function displayChatsList(filter='') {
	console.log('Displaying chats list');
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	try {
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (apiAnswer.detail){
			console.log('Error:', apiAnswer.detail);
			return;
		}
		if (apiAnswer.count > 0) {
			console.log('Chats found');
			apiAnswer.results.forEach(async element => {
				data = parsChatInfo(element);
				await createChatUserCard(data);
			});
			nextChatsRequest = apiAnswer.next;
		}
		else {
			console.log('No chat found');
		}
	}
	catch(error) {
		console.log(error);
	}
	console.log('Selecting chat');
}

async function searchChatButton(username) {
	try{
		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${username}`);
		if (apiAnswer.detail){
			console.log('Error:', apiAnswer.detail);
			return;
		}
	}
	catch(error) {
		console.log(error);
		return;
	}

	chatRequest = undefined;
	chatInfo = undefined;
	if (apiAnswer.count === 0)
	{
		console.log('Chat doesn\'t exist => creating chat');
		try {
			var chatRequest = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'POST', undefined, undefined, {'username': username, 'type':"private_message"});
			if (chatRequest.detail){
				console.log('Error:', chatRequest.detail);
				return;
			}
		}
		catch (error) {
			console.log(error);
			return;
		}
		console.log('New chat created:', chatRequest);
	}
	else {
		console.log('Chat already exist => loading chat');
		try {
			var chatRequest = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${apiAnswer.results[0].id}`, 'GET');
			if (chatRequest.detail){
				console.log('Error:', chatRequest.detail);
				return;
			}
		}
		catch (error) {
			console.log(error);
			return;
		}
		console.log('Chat loaded:', chatRequest);
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
	if (chatActiveTab.id === 'chatTab' + chatInfo.target + 'Link') isTabActive = true;
	document.getElementById('chatTab' + chatInfo.target).remove();
	document.getElementById('chatBox' + chatInfo.target).remove();
	openChat['chatTab' + chatInfo.target] = undefined;
	let lastTab = document.getElementById('chatTabs').lastElementChild;
	if (!lastTab) {
		disconnect();
		console.log('No more chat', lastTab);
		document.getElementById('chatView').remove();
	}
	else if (isTabActive) {
		disconnect();
		lastTab.querySelector('a').click();
		console.log('lastClickBefore nananananana: ', lastTab.id);
		if (await connect(getAccessToken(), openChat[lastTab.id]) === false) return;
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
		console.log('Switching chat', e.target);
	});
}

function sendMessageListener(target) {
	console.log('Adding listener to chatForm', target);
    const chatForm = document.getElementById('sendMessageForm'+target);
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = this.querySelector('input').value;
			if (message === '') return;
            socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
            console.log('Message sent: ', message);
            chatForm.reset();
        });
    }
}

async function openChatTab(chatInfo)
{
	chatTabs = document.getElementById('chatTabs');
	if (!chatTabs) {
		await loadContent('/chatTemplates/chatTabs.html', 'content', true);
	}
	else {
		disconnect();
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
			console.log(error);
		}
		const chatModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('chatListModal'));
		chatModal.hide();
		console.log(chatModal);
	}
	else {
		document.getElementById('chatTab'+chatInfo.target).querySelector('a').click();
	}
	if (await connect(getAccessToken(), chatInfo) === false) return;
	document.getElementById('searchChatForm').reset();

	document.getElementById('logOut').addEventListener('click', () => {
		disconnect();
		openChat = {};
		document.getElementById('chatView').remove();
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