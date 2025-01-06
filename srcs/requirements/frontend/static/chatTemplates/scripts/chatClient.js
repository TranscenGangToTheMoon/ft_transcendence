function parsChatRequest(chat)
{
	let chatData = {
		'chatId': chat.id,
		'target': chat.chat_with.username,
		'targetId': chat.chat_with.id,
		'lastMessage': '< Say hi! >',
	};
	if (chat.last_message) {
		if (chat.last_message.content.length > 37){
			chatData.lastMessage = chat.last_message.content.slice(0, 37) + '...';
		}
		else chatData.lastMessage = chat.last_message.content;
	}
	return chatData;
}

async function getMoreOldsMessages(chatData){
	if (!nextMessagesRequest) return;
	nextMessagesRequest = `${nextMessagesRequest.substring(0, 4)}s${nextMessagesRequest.substring(4)}`
	try {
		let apiAnswer = await apiRequest(getAccessToken(), nextMessagesRequest);
		if (apiAnswer.count !== 0) {
			chatBox = document.getElementById('messages');
			apiAnswer.results.forEach(element => {
				console.log(element);
				if (element.author === chatData.targetId) {
					chatBox.insertAdjacentHTML('afterbegin', `<div><strong>${chatData.target}:</strong> ${element.content}</div>`);
				} else {
					chatBox.insertAdjacentHTML('afterbegin', `<div><strong>You:</strong> ${element.content}</div>`);
				}
			});
		}
		nextMessagesRequest = apiAnswer.next;
	}
	catch (error) {
		console.log('something went wrong');
		console.log(error);
	}
}

async function loadOldMessages(chatData){
	const chatBox = document.getElementById('messages');
	let apiAnswer = undefined;
	try {
		apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatData.chatId}/messages`, 'GET');
	}
	catch (error) {
		console.log(error);
		return error;
	}
	if (apiAnswer.count !== 0) {
		apiAnswer.results.forEach(element => {
			console.log(chatData.targetId, chatData.target, element.author);
			if (element.author === chatData.targetId) {
				chatBox.insertAdjacentHTML('afterbegin', `<div><strong>${chatData.target}:</strong> ${element.content}</div>`);
			} else {
				chatBox.insertAdjacentHTML('afterbegin', `<div><strong>You:</strong> ${element.content}</div>`);
			}
		});
		nextMessagesRequest = apiAnswer.next;
	}
	chatBox.scrollTop = chatBox.scrollHeight;
	return {'code': 200};
}

async function connect(token, chatData) {
	closeChat();
	try {
		res = await loadOldMessages(chatData);
		if (res.code !== 200)
			throw (res);
	}
	catch (error) {
		console.log(error);
		return false;
	}
	let socket = await io("/", {
		path: "/ws/chat/",
		transports: ['websocket'],
		auth: {
			"token": 'Bearer ' + token,
			"chatId": chatData.chatId
		}
	});
	console.log(socket);
	window.socket = socket;
	window.chatData = chatData;
	console.log("Connecting to the server...");
	setupSocketListeners(chatData);
	return true;
}

function closeChat()
{
	if (typeof window.socket === 'undefined')	return;
	console.log('je close la socket');
	try {
		console.log("Closing the connection to the server...");
		socket.off();
		socket.disconnect();
		lastClick = undefined;
		document.getElementById('chatView').style.display = 'none';
		document.getElementById('messages').innerHTML = "";
		socket = null;
	}
	catch (error) {
		console.log(error);
	}
}




function send(chatData) {
    const chatForm = document.getElementById('sendMessageForm');
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = e.target.message.value;
			if (message === '') return;
            socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
            console.log('Message sent: ', message);
            chatForm.reset();
        });
    }
}


function setupSocketListeners(chatData)
{
	document.getElementById('endChat').addEventListener('click', () => {
		closeChat();
		lastClick = undefined;
	});
	document.getElementById('logOut').addEventListener('click', () => {
		closeChat();
		lastClick = undefined;
	});

	const chatBox = document.getElementById('messages');

	socket.off();
	
	socket.on("connect", () => {
		console.log("Connected to the server");
		console.log(socket);
		document.getElementById('chatView').style.display = 'block';
		document.getElementById('chatName').innerHTML = chatData.target;
	});

	socket.on("connect_error", async (data) => {
		console.log("Connection error: ", data);
		console.log('You\'ve got some issues mate');
		if (data.error === 401){
			console.log('reattempting connection');
			await connect(await refreshToken(), chatData.chatId);
		}
		else {
			lastClick = undefined;
			console.log('You\'ve got some issues mate');
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
		lastClick = undefined;
		document.getElementById('chatView').style.display = 'none';
		document.getElementById('messages').innerHTML = "";
	});
	
	socket.on("message", (data) => {
		console.log("Message received: ", data);
		console.log(chatData.targetId, chatData.target, data.author);
		if (data.author === '')
			chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>:</strong> ${data.content}</p></div>`);
		else{
			document.getElementById('chatListElement' + chatData.target).querySelector('.chatUserCardLastMessage').innerText = data.content;
			if (data.author === chatData.targetId) {
				chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>${chatData.target}:</strong> ${data.content}</p></div>`);
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
		else{
			closeChat();
			console.log('You\'ve got some issues mate');
		}
	});
	
	socket.on("debug", (data) => {
		console.log("Debug received: ", data);
	});

	send(chatData);
}

function parsChatRequest(chat)
{
	let chatData = {
		'chatId': chat.id,
		'target': chat.chat_with.username,
		'targetId': chat.chat_with.id,
		'lastMessage': '< Say hi! >',
	};
	if (chat.last_message) {
		if (chat.last_message.content.length > 37){
			chatData.lastMessage = chat.last_message.content.slice(0, 37) + '...';
		}
		else chatData.lastMessage = chat.last_message.content;
	}
	return chatData;
}

async function createUserCard(chatData) {
	let chatUserCard = document.createElement('div');
	chatUserCard.id = 'chatListElement' + chatData.target;
	chatUserCard.classList.add('chatUserCard');
	chatsList.appendChild(chatUserCard);

	await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
	console.log(chatUserCard);
	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatData.target + ':';
	chatUserCard.querySelector('.chatUserCardTitleStatus').innerText = 'prout';
	chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatData.lastMessage);
	chatUserCard.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
		e.preventDefault();
		try {
			const response = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatData.chatId}/`, 'DELETE');
			document.getElementById('chatListElement' + chatData.target).remove();
			lastClick = undefined;
			console.log('Chat view deleted', lastClick);
		}catch(error){
			console.log(error);
		}
	});
	chatUserCard.addEventListener('click', async e => {
		if (lastClick === e.target.closest('#chatListElement' + chatData.target)) return;
		if (e.target === chatUserCard.querySelector('.chatUserCardButtonDeleteChat')) return;
		console.log("lastClickAfter: ",lastClick);
		await connect(getAccessToken(), chatData);
		lastClick = e.target.closest('#chatListElement' + chatData.target);
	});
}

async function getMoreChats(){
	if (!nextChatsRequest) return;
	if (nextChatsRequest.substring(0, 5) === "https") return;
	nextChatsRequest = `${nextChatsRequest.substring(0, 4)}s${nextChatsRequest.substring(4)}`
	try {
		let apiAnswer = await apiRequest(getAccessToken(), nextChatsRequest);
		if (apiAnswer.count !== 0) {
			chatBox = document.getElementById('chasList');
			apiAnswer.results.forEach(async element => {
				console.log(element);
				data = parsChatRequest(element);
				await createUserCard(data);
			});
		}
		nextMessagesRequest = apiAnswer.next;
	}
	catch (error) {
		console.log('something went wrong');
		console.log(error);
	}
}

async function selectChatMenu(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	console.log('filter', filter);
	try {
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (apiAnswer.count > 0) {
			apiAnswer.results.forEach(async element => {
				console.log(element, "proooooooout");
				data = parsChatRequest(element);
				await createUserCard(data);
			});
			nextChatsRequest = apiAnswer.next;
			console.log('chats fouuuuuuuuuuuuuuuuuuuuuuuuuuuuund', nextChatsRequest);
		}
		else {
			console.log('no chats found');
		}
	}
	catch(error) {
		console.log(error);
	}
}

async function startChat(username) {
	try{
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${username}`);
		let chatData = undefined;
		if (apiAnswer.count === 0)
		{
			console.log('Chat doesn\'t exist: creating chat');
			const newchat = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'POST', undefined, undefined, {'username': username, 'type':"private_message"});
			console.log(newchat);
			chatData = parsChatRequest(newchat);
			await connect(getAccessToken(), chatData);
		}
		else {
			console.log('Chat already exist: loading chat');
			chatData = parsChatRequest(apiAnswer.results[0]);
			await connect(getAccessToken(), chatData);
		}
		lastClick = document.getElementById("chatListElement" + chatData.target);
		document.getElementById('searchChatForm').reset();
		selectChatMenu();
		console.log('Chat started', lastClick);
	}
	catch(error) {
		console.log(error);
	}
}


async function chatClientInit() {
	await indexInit(false);
}

var lastClick = undefined;
if (typeof loading === 'undefined')
	var loading = false;
if (typeof nextMessagesRequest === 'undefined')
	var nextMessagesRequest = undefined;
if (typeof nextChatsRequest === 'undefined')
	var nextChatsRequest = undefined;

chatClientInit();
selectChatMenu();

document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	console.log("dewpokdowek", e.key === 'Enter');
	if (e.key === 'Enter') return;
	selectChatMenu(e.target.value);
});

document.getElementById('searchChatForm').addEventListener('submit', (e) => {
	e.preventDefault();
	if (e.target.searchUser.value === '') return;
	startChat(e.target.searchUser.value);
});

document.addEventListener('scroll', async event => {
	console.log('scrolling');
	if (event.target.id === 'messages'){
		console.log('scrolling in messages');
		const chatBox = document.getElementById('messages');
		const scrollHeight = chatBox.scrollHeight;
		const clientHeight = chatBox.clientHeight;
		const scrollTop = chatBox.scrollTop;
		const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
		if (scrollPercentage <= 15 && !loading) {
			loading = true;
			await getMoreOldsMessages(chatData);
			loading = false;
		}
	}
	if (event.target.id === 'chatsList'){
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
	}
}, true);

