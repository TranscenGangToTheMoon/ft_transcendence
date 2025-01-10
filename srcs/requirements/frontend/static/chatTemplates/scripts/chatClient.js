// function parsChatInfo(chat)
// {
// 	let chatInfo = {
// 		'chatId': chat.id,
// 		'target': chat.chat_with.username,
// 		'targetId': chat.chat_with.id,
// 		'lastMessage': '< Say hi! >',
// 		'isLastMessageRead': false,
// 	};
// 	if (chat.last_message) {
// 		if (chat.last_message.content.length > 37){
// 			chatInfo.lastMessage = chat.last_message.content.slice(0, 37) + '...';
// 		}
// 		else chatInfo.lastMessage = chat.last_message.content;
// 		chatInfo.isLastMessageRead = chat.last_message.is_read;
// 	}
// 	return chatInfo;
// }

// function disconnect() {
// 	if (socket === null) return;
// 	console.log("Closing the connection to the server...");
// 	socket.off();
// 	socket.disconnect();
// 	socket = null;
// }

// async function connect(token, chatInfo) {
// 	if(typeof window.socket !== 'undefined')	disconnect();
// 	try {
// 		res = await loadOldMessages(chatInfo);
// 		if (res.code !== 200)
// 			throw (res);
// 	}
// 	catch (error) {
// 		console.log(error);
// 		return false;
// 	}
// 	let socket = await io("/", {
// 		path: "/ws/chat/",
// 		transports: ['websocket'],
// 		auth: {
// 			"token": 'Bearer ' + token,
// 			"chatId": chatInfo.chatId
// 		}
// 	});
// 	console.log(socket);
// 	window.socket = socket;
// 	console.log("Connecting to the server...");
// 	return true;
// }

// async function openChat(chatInfo)
// {
// 	if (await connect(getAccessToken(), chatInfo) === false) return;

// 	document.getElementById('searchChatForm').reset();
// 	lastClick = document.getElementById('chatListElement' + chatInfo.target);
// 	lastClick.querySelector('.chatUserCardLastMessage').classList.remove('chatMessageNotRead');

// 	setupSocketListeners(chatInfo);

// 	document.getElementById('endChat').addEventListener('click', () => {
// 		closeChat();
// 		lastClick = undefined;
// 	});
// 	document.getElementById('logOut').addEventListener('click', () => {
// 		closeChat();
// 		lastClick = undefined;
// 	});

// 	document.getElementById('messages').addEventListener('scroll', async event => {
// 		const chatBox = document.getElementById('messages');
// 		const scrollHeight = chatBox.scrollHeight;
// 		const clientHeight = chatBox.clientHeight;
// 		const scrollTop = chatBox.scrollTop;
// 		const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
// 		if (scrollPercentage <= 15 && !loading) {
// 			loading = true;
// 			await getMoreOldsMessages(chatInfo);
// 			loading = false;
// 			console.log(chatBox.scrollTop, chatBox.scrollHeight, chatBox.clientHeight);
// 		}
// 	});

// 	send();
// }

// function closeChat()
// {
// 	if (typeof window.socket !== 'undefined')	disconnect();
// 	lastClick = undefined;
// 	document.getElementById('chatView').style.display = 'none';
// 	document.getElementById('messages').innerHTML = "";
// 	socket = null;
// }

// function send() {
//     const chatForm = document.getElementById('sendMessageForm');
//     if (!chatForm.hasAttribute('data-listener-added')) {
//         chatForm.setAttribute('data-listener-added', 'true');
//         chatForm.addEventListener('submit', (e) => {
//             e.preventDefault();
//             const message = e.target.message.value;
// 			if (message === '') return;
//             socket.emit('message', {'content': message, 'token' : 'Bearer ' + getAccessToken()});
//             console.log('Message sent: ', message);
//             chatForm.reset();
//         });
//     }
// }

// function setupSocketListeners(chatData)
// {
// 	const chatBox = document.getElementById('messages');

// 	socket.off();
	
// 	socket.on("connect", () => {
// 		console.log("Connected to the server");
// 		console.log(socket);
// 		document.getElementById('chatView').style.display = 'block';
// 		document.getElementById('chatName').innerHTML = chatData.target;
// 	});

// 	socket.on("connect_error", async (data) => {
// 		console.log("Connection error: ", data);
// 		console.log('You\'ve got some issues mate');
// 		if (data.error === 401){
// 			console.log('reattempting connection');
// 			await connect(await refreshToken(), chatData.chatId);
// 		}
// 		else {
// 			lastClick = undefined;
// 			console.log('You\'ve got some issues mate ', data);
// 		}
// 	});
	
// 	socket.on("disconnect", () => {
// 		console.log("Disconnected from the server");
// 		lastClick = undefined;
// 		document.getElementById('chatView').style.display = 'none';
// 		document.getElementById('messages').innerHTML = "";
// 	});
	
// 	socket.on("message", (data) => {
// 		console.log("Message received: ", data);
// 		console.log(chatData.targetId, chatData.target, data.author);
// 		if (data.author === '')
// 			chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>:</strong> ${data.content}</p></div>`);
// 		else{
// 			document.getElementById('chatListElement' + chatData.target).querySelector('.chatUserCardLastMessage').innerText = data.content;
// 			if (data.author === chatData.targetId) {
// 				chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>${chatData.target}:</strong> ${data.content}</p></div>`);
// 			}
// 			else {
// 				chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>You:</strong> ${data.content}</p></div>`);
// 			}
// 		}
// 		chatBox.scrollTop = chatBox.scrollHeight;
// 	});

// 	socket.on("error", async (data) => {
// 		console.log("Error received: ", data);
// 		if (data.error === 401){
// 			socket.emit('message', {'content': data.retry_content, 'token' : 'Bearer ' + await refreshToken(), 'retry': true});
// 		}
// 	});

// 	socket.on("debug", (data) => {
// 		console.log("Debug received: ", data);
// 	});
// }

// function displayMessages(chatInfo, chatMessages, method='afterbegin'){
// 	const chatBox = document.getElementById('messages');
// 	chatMessages.forEach(element => {
// 		console.log(element);
// 		if (element.author === chatInfo.targetId) {
// 			chatBox.insertAdjacentHTML(method, `<div><p><strong>You:</strong> ${element.content}</p></div>`);
// 		} else {
// 			chatBox.insertAdjacentHTML(method, `<div><p><strong>${chatInfo.target}:</strong> ${element.content}</p></div>`);
// 		}
// 	});
// }

// async function getMoreOldsMessages(chatInfo){
// 	if (!nextMessagesRequest) return;
// 	if (nextMessagesRequest.substring(0, 5) === "https") return;
// 	nextMessagesRequest = `${nextMessagesRequest.substring(0, 4)}s${nextMessagesRequest.substring(4)}`
// 	try {
// 		let apiAnswer = await apiRequest(getAccessToken(), nextMessagesRequest);
// 		if (apiAnswer.details){
// 			console.log('Error:', apiAnswer.details);
// 			return;
// 		}
// 		if (apiAnswer.count !== 0) displayMessages(chatInfo, apiAnswer.results);
// 		nextMessagesRequest = apiAnswer.next;
// 	}
// 	catch (error) {
// 		console.log('Something went wrong:', error);
// 	}
// }

// async function loadOldMessages(chatInfo){
// 	try {
// 		console.log('Loading old messages', chatInfo);
// 		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/messages`, 'GET');
// 		if (apiAnswer.details){
// 			console.log('Error:', apiAnswer.details);
// 			return {'code': 400, 'details': apiAnswer.details};
// 		};
// 		if (apiAnswer.count !== 0){
// 			displayMessages(chatInfo, apiAnswer.results);
// 			nextMessagesRequest = apiAnswer.next;
// 		}
// 		else {
// 			document.getElementById('messages').insertAdjacentHTML('afterbegin', `<div><p><strong>:</strong> Start the conversation ;)</p></div>`);
// 		}
// 	}
// 	catch (error) {
// 		console.log(error);
// 		return error;
// 	}
// 	return {'code': 200};
// }

// async function getMoreChats(){
// 	if (!nextChatsRequest) return;
// 	if (nextChatsRequest.substring(0, 5) === "https") return;

// 	nextChatsRequest = `${nextChatsRequest.substring(0, 4)}s${nextChatsRequest.substring(4)}`

// 	try {
// 		let apiAnswer = await apiRequest(getAccessToken(), nextChatsRequest);
// 		if (apiAnswer.details){
// 			console.log('Error:', apiAnswer.details);
// 			return;
// 		}
// 		if (apiAnswer.count !== 0) {
// 			chatBox = document.getElementById('chasList');
// 			apiAnswer.results.forEach(async element => {
// 				console.log(element);
// 				data = parsChatInfo(element);
// 				await createUserCard(data);
// 			});
// 		}
// 		nextMessagesRequest = apiAnswer.next;
// 	}
// 	catch (error) {
// 		console.log('Something went wrong:', error);
// 	}
// }

// async function createUserCard(chatInfo) {
// 	let chatUserCard = document.createElement('div');
// 	chatUserCard.id = 'chatListElement' + chatInfo.target;
// 	chatUserCard.classList.add('chatUserCard');
// 	chatsList.appendChild(chatUserCard);

// 	await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
// 	console.log(chatUserCard);
// 	chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatInfo.target + ':';
// 	chatUserCard.querySelector('.chatUserCardTitleStatus').innerText = 'prout';
// 	chatUserCard.querySelector('.chatUserCardLastMessage').innerText = (chatInfo.lastMessage);
// 	if (chatInfo.isLastMessageRead === false)
// 		chatUserCard.querySelector('.chatUserCardLastMessage').classList.add('chatMessageNotRead');
// 	chatUserCard.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
// 		e.preventDefault();
// 		try {
// 			const APIAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatInfo.chatId}/`, 'DELETE');
// 			if (APIAnswer.details){
// 				console.log('Error:', APIAnswer.details);
// 				return;
// 			}
// 			document.getElementById('chatListElement' + chatInfo.target).remove();
// 			console.log('Chat view deleted', lastClick);
// 		}catch(error){
// 			console.log(error);
// 		}
// 	});
// 	chatUserCard.addEventListener('click', async e => {
// 		if (lastClick === e.target.closest('#chatListElement' + chatInfo.target)) return;
// 		if (e.target === chatUserCard.querySelector('.chatUserCardButtonDeleteChat')) return;
// 		console.log("lastClickAfter: ",lastClick);
// 		await openChat(chatInfo);
// 	});
// }

// async function selectChatMenu(filter='') {
// 	chatsList = document.getElementById('chatsList');
// 	chatsList.innerHTML = '';
// 	console.log('filter', filter);
// 	try {
// 		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
// 		if (apiAnswer.count > 0) {
// 			apiAnswer.results.forEach(async element => {
// 				data = parsChatInfo(element);
// 				await createUserCard(data);
// 			});
// 			nextChatsRequest = apiAnswer.next;
// 		}
// 		else {
// 			console.log('No chat found');
// 		}
// 	}
// 	catch(error) {
// 		console.log(error);
// 	}
// }

// async function startChat(username) {
// 	try{
// 		var apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${username}`);
// 		if (apiAnswer.details){
// 			console.log('Error:', apiAnswer.details);
// 			return;
// 		}
// 	}
// 	catch(error) {
// 		console.log(error);
// 		return;
// 	}

// 	chatInfo = undefined;
// 	if (apiAnswer.count === 0)
// 	{
// 		console.log('Chat doesn\'t exist => creating chat');
// 		try {
// 			var newChat = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'POST', undefined, undefined, {'username': username, 'type':"private_message"});
// 			if (newChat.details){
// 				console.log('Error:', newChat.details);
// 				return;
// 			}
// 		}
// 		catch (error) {
// 			console.log(error);
// 			return;
// 		}
// 		console.log('New chat created:', newChat);
// 		chatInfo = parsChatInfo(newChat);
// 	}
// 	else {
// 		console.log('Chat already exist => loading chat');
// 		chatData = parsChatInfo(apiAnswer.results[0]);
// 	}
// 	await selectChatMenu();
// 	await openChat(chatInfo);
// 	console.log('Chat started', lastClick);
// }


// async function chatClientInit() {
// 	await indexInit(false);
// }

// var lastClick = undefined;
// if (typeof loading === 'undefined')
// 	var loading = false;
// if (typeof nextMessagesRequest === 'undefined')
// 	var nextMessagesRequest = undefined;
// if (typeof nextChatsRequest === 'undefined')
// 	var nextChatsRequest = undefined;

// chatClientInit();
// selectChatMenu();

// document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
// 	e.preventDefault();
// 	console.log("dewpokdowek", e.key === 'Enter');
// 	if (e.key === 'Enter') return;
// 	selectChatMenu(e.target.value);
// });

// document.getElementById('searchChatForm').addEventListener('submit', (e) => {
// 	e.preventDefault();
// 	if (e.target.searchUser.value === '') return;
// 	startChat(e.target.searchUser.value);
// });

// document.getElementById('chatsList').addEventListener('scroll', async event => {
// 	const chatsListBox = document.getElementById('chatsList');
// 	const scrollHeight = chatsListBox.scrollHeight;
// 	const clientHeight = chatsListBox.clientHeight;
// 	const scrollTop = chatsListBox.scrollTop;
// 	const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
// 	if (scrollPercentage >= 85 && !loading) {
// 		loading = true;
// 		await getMoreChats();
// 		loading = false;
// 	}
// 	console.log('scrolling in chatsList');
// }, true);
