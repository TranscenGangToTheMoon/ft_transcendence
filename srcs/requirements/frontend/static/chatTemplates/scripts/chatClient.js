async function connect(token, chatData) {
	if (window.socket) {
        closeChat(); // Ensure any existing socket is properly closed
    }
	let socket = await io("wss://localhost:4443", {
		path: "/ws/chat/",
		transport: ['websocket'],
		auth: {
			"token": 'Bearer ' + token,
			"chatId": chatData.chatId
		}
	});
	console.log(socket);
	window.socket = socket;
	console.log("Connecting to the server...");

	setupSocketListeners(chatData);
}

function closeChat()
{
	try {
		console.log("Closing the connection to the server...");
		socket.off();
		socket.disconnect();
		socket = null;
	}
	catch (error) {
		console.log(error);
	}
	document.getElementById('chatView').style.display = 'none';
	document.getElementById('messages').innerHTML = "";
}


function send(chatData) {
    const chatForm = document.getElementById('sendMessageForm');
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = e.target.message.value;
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
			connect(await refreshToken(), chatData.chatId);
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
		
	});
	
	socket.on("message", (data) => {
		console.log("Message received: ", data);
		chatBox.insertAdjacentHTML('beforeend', `<div><p><strong>${data.author}:</strong> ${data.content}</p></div>`);
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
		chatData.lastMessage = chat.last_message.content;
	}
	return chatData;
}

async function loadOldMessages(chatData){
	const chatBox = document.getElementById('messages');
	try {
		console.log('loading old messages');
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatData.chatId}/messages`, 'GET');
		if (data.count === 0) {
			console.log('no messages to load');
		}
		else {
			data.results.forEach(element => {
				if (element.author === chatData.targetId) {
					chatBox.insertAdjacentHTML('afterbegin', `<div><strong>${chatData.target}:</strong> ${element.content}</div>`);
				} else {
					chatBox.insertAdjacentHTML('afterbegin', `<div><strong>You:</strong> ${element.content}</div>`);
				}
			});
		}
	}
	catch (error) {
		console.log(error);
	}
}

// await loadContent('chatTemplates/chatUserCard.html', 'chatList', true);


var lastClick;

async function selectChatMenu(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	console.log('filter', filter);
	try {
		const apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (apiAnswer.count > 0) {
			apiAnswer.results.forEach(async element => {
				let chatData = parsChatRequest(element);
				let chatUserCard = document.createElement('div');
				chatUserCard.id = 'chatListElement' + chatData.target;
				chatUserCard.classList.add('chatUserCard');
				chatsList.appendChild(chatUserCard);
				await loadContent('/chatTemplates/chatUserCard.html', chatUserCard.id);
				console.log(chatUserCard);
				chatUserCard.querySelector('.chatUserCardTitleUsername').innerText = chatData.target;
				chatUserCard.querySelector('.chatUserCardTitleStatus').innerText = 'prout';
				chatUserCard.querySelector('.chatUserCardLastMessage').innerText = chatData.lastMessage;
				// try {
				// 	response = await fetch('chatTemplates/chatUserCard.html');
				// 	if (!response.ok) {
				// 		throw new Error('Network response was not ok');
				// 	}+
				// 	const html = response.text();
				// 	html.setAttribute('id', 'chatListElement' + chatData.user);
				// 	html.querySelector('.chatUserCardTitleUsername').innerText = chatData.user;
				// 	html.querySelector('.chatUserCardTitleStatus').innerText = 'prout';
				// 	html.querySelector('.chatUserCardLastMessage').innerText = chatData.lastMessage;
				// 	html.querySelector('.chatUserCardButtonDeleteChat').addEventListener('click',async e => {
				// 		e.preventDefault();
				// 		console.log('delete chat');
				// 		//https://ft_transcendence.fr/api/chat/<int:chat_id>/
				// 		try {
				// 			const response = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatData.chatId}/`, 'DELETE');
				// 			Document.getElementById('chatListElement' + chatData.user).remove();
				// 		}catch(error){
				// 			console.log(error);
				// 		}
				// 	});
				// 	html.addEventListener('click', e => {
				// 		if (lastClick === e.target.closest('#chatListElement' + chatData.user)) return;
				// 			lastClick = e.target.closest('#chatListElement' + chatData.user);
				// 			console.log(chatData.user, 'selected');
				// 			connect(getAccessToken(), chatData);
				// 			loadOldMessages(chatData);
				// 	});
				// 	chatsList.appendChild(html);
				// }
				// catch (error) {
				// 	notFound = document.createElement('div');
				// 	notFound.innerHTML = '<div>Error 404 : Page not found : </div>'
				// 	chatsList.appendChild(notFound);
				// }
				// let chat = document.createElement('div');
				// chat.setAttribute('id', 'chatListElement');
				// chat.innerHTML = `<p id="chatListElementTarget">${chatData.target}:</p><p id="chatListElementMessagePreview">${chatData.lastMessage}</p>`;
				// chat.addEventListener('click', e => {
				// 	if (lastClick === e.target.closest('#chatListElement')) return;
				// 	lastClick = e.target.closest('#chatListElement');
				// 	console.log(chatData.user, 'selected');
				// 	connect(getAccessToken(), chatData);
				// 	loadOldMessages(chatData);
				// });
				// chatsList.appendChild(chat);
			});
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
		if (apiAnswer.count === 0)
		{
			const newchat = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'POST', undefined, undefined, {'username': username, 'type':"private_message"});
			console.log(newchat.code);
			let chatData = parsChatRequest(newchat);
			connect(getAccessToken(), chatData);
		}
		else {
			console.log('chat already exists');
			let chatData = parsChatRequest(apiAnswer.results[0]);
			connect(getAccessToken(), chatData);
			loadOldMessages(chatData);
		}
	}
	catch(error) {
		console.log(error);
	}
}


async function chatClientInit() {
	await indexInit(false);
}
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
