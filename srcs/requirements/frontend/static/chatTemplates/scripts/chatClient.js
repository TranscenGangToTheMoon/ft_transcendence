async function connect(token, chatData) {
	if (window.socket) {
        closeChat(); // Ensure any existing socket is properly closed
    }
	let socket = await io("wss://localhost:4443", {
		path: "/ws/chat/",
		extraHeaders: {
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
            socket.emit('message', {'chatId': chatData.chatId, 'content': message});
            console.log('Message sent: ', message);
            chatForm.reset();
        });
    }
}


function setupSocketListeners(chatData)
{
	document.getElementById('endChat').addEventListener('click', () => {
		closeChat();
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
	
	socket.on("error", (data) => {
		console.log("Error received: ", data);
	});
	
	socket.on("debug", (data) => {
		console.log("Debug received: ", data);
	});

	send(chatData);
}

async function loadOldMessages(chatData){
	const chatBox = document.getElementById('messages');
	try {
		console.log('loading old messages');
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatData.chatId}/messages`, 'GET');
		data.results.forEach(element => {
			if (element.author === chatData.targetId) {
				chatBox.insertAdjacentHTML('afterbegin', `<div><strong>${chatData.target}:</strong> ${element.content}</div>`);
			} else {
				chatBox.insertAdjacentHTML('afterbegin', `<div><strong>You:</strong> ${element.content}</div>`);
			}
		});
	}
	catch (error) {
		console.log(error);
	}
}

async function selectChatMenu(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	console.log('filter', filter);
	try {
		const data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		if (data.count > 0) {
			data.results.forEach(element => {
				let data = {
					'chatId': element.id,
					'target': element.participants[0].username,
					'targetId': element.participants[0].id,
					'lastMessage': element.last_message,
				};
				if (data.lastMessage === null) {
					data.lastMessage = '< Say hi! >';
				}
				let chat = document.createElement('div');
				chat.setAttribute('id', 'chatListElement');
				chat.innerHTML = `<p id="chatListElementTarget">${data.target}:</p><p id="chatListElementMessagePreview">${data.lastMessage}</p>`;
				chat.addEventListener('click', () => {
					console.log(data.user, 'selected');
					connect(getAccessToken(), data);
					loadOldMessages(data);
				});
				chatsList.appendChild(chat);
			});
		}
	}
	catch(error) {
		console.log(error);
	}
}

async function startChat(username) {

}

async function chatClientInit() {
	await indexInit(false);
}
chatClientInit();

selectChatMenu();

document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	selectChatMenu(e.target.value);
});
document.getElementById('searchChatForm').addEventListener('submit', (e) => {
	e.preventDefault();
	//selectChatMenu(e.target.value);
	closeChat();
});
