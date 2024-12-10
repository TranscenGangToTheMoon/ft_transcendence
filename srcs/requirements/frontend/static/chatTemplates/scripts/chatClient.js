function connect(token, chatId) {
	if (window.socket) {
        closeChat(); // Ensure any existing socket is properly closed
    }
	let socket = io("wss://localhost:4443", {
		path: "/ws/chat/",
		extraHeaders: {
			"token": 'Bearer ' + token,
			"chatId": chatId
		}
	});
	window.socket = socket;
	console.log("Connecting to the server...");
	setupSocketListeners();
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


function send() {
    const chatForm = document.getElementById('sendMessageForm');
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = e.target.message.value;
            socket.emit('message', { 'message': message });
            console.log('Message sent: ', message);
            chatForm.reset();
        });
    }
}


function setupSocketListeners()
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
	});

	socket.on("connect_error", async (data) => {
		console.log("Connection error: ", data);
		if (data.error === 401){
			token = await refreshToken();
			console.log('retry');
			connect(token, chatId);
		}
	});
	
	socket.on("disconnect", () => {
		console.log("Disconnected from the server");

	});
	
	socket.on("message", (data) => {
		console.log("Message received: ", data);
		chatBox.insertAdjacentHTML('beforeend', `<div><p>: ${data.message}</p></div>`);
	});
	
	socket.on("error", (data) => {
		console.log("Error received: ", data);
		socket.disconnect();
	});
	
	socket.on("debug", (data) => {
		console.log("Debug received: ", data);
	});

	send();
}


async function selectChatMenu(filter='') {
	chatsList = document.getElementById('chatsList');
	chatsList.innerHTML = '';
	console.log('filter', filter);
	try {
		const data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		console.log(data);
		if (data.count > 0) {
			console.log('there is some chats');
			data.results.forEach(element => {
				console.log(element);
				let data = {
					'chatId': element.id,
					'user': element.participants[0].username,
					'lastMessage': element.last_message,
				};
				if (data.lastMessage === null) {
					data.lastMessage = '< Say hi! >';
				}
				console.log(data);
				let chat = document.createElement('div');
				chat.setAttribute('id', 'chatListElement');
				chat.innerHTML = `<p id="chatListElementTarget">${data.user}:</p><p id="chatListElementMessagePreview">${data.lastMessage}</p>`;
				chat.addEventListener('click', () => {
					console.log(data.user, 'selected');
					connect(getAccessToken(), data.chatId);
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

let chatListForm = document.getElementById('searchChatForm');

chatListForm.addEventListener('keyup', (e) => {
	e.preventDefault();
	selectChatMenu(e.target.value);
});
chatListForm.addEventListener('submit', (e) => {
	e.preventDefault();
	//selectChatMenu(e.target.value);
	closeChat();
});
