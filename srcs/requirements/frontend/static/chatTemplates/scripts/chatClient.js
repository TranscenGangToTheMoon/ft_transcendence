// function connect(token, chatId) {
// 	let socket = io("wss://localhost:4443", {
// 		path: "/ws/chat/",
// 		extraHeaders: {
// 			"token": 'Bearer ' + token,
// 			"chatId": chatId
// 		}
// 	});
// 	window.socket = socket;
// 	console.log(socket);
// 	console.log("Connecting to the server...");
// 	setupSocketListeners();
// 	return true;
// }

// function closeChat()
// {
// 	console.log("Closing the connection to the server...");
// 	socket.disconnect();
// 	socket = null;
// 	document.getElementById('startChat').style.display = 'block';
// 	document.getElementById('chat-view').style.display = 'none';
// 	chatBox.innerHTML = "";
// }


// function send() {
// 	let chatForm = document.getElementById('chat-form');
// 	chatForm.addEventListener('submit', (e) => {
// 		e.preventDefault();
// 		const message = e.target.message.value;
// 		socket.emit('message', { 'message': message });
// 		console.log('Message sent: ', message);
// 		chatForm.reset();
// 	});
// }


// function setupSocketListeners()
// {
// 	document.getElementById('endChat').addEventListener('click', () => {
// 		closeChat();
// 	});
// 	document.getElementById('logOut').addEventListener('click', () => {
// 		closeChat();
// 	});

// 	const chatBox = document.getElementById('chats-box');

// 	socket.off("connect");
// 	socket.off("connect_error");
//     socket.off("disconnect");
//     socket.off("message");
//     socket.off("error");
// 	socket.off("debug");
	
// 	socket.on("connect", () => {
// 		console.log("Connected to the server");
// 		console.log(socket);
// 		document.getElementById('startChat').style.display = 'none';
// 		document.getElementById('chat-view').style.display = 'block';
// 	});

// 	socket.on("connect_error", async (data) => {
// 		console.log("Connection error: ", data);
// 		// if (data.error === 401){
// 		// 	token = await refreshToken();
// 		// 	console.log('suite');
// 		// }
// 	});
	
// 	socket.on("disconnect", () => {
// 		console.log("Disconnected from the server");

// 	});
	
// 	socket.on("message", (data) => {
// 		console.log("Message received: ", data);
// 		chatBox.insertAdjacentHTML('beforeend', `<div><p>: ${data.message}</p></div>`);
// 	});
	
// 	socket.on("error", (data) => {
// 		console.log("Error received: ", data);
// 		socket.disconnect();
// 	});
	
// 	socket.on("debug", (data) => {
// 		console.log("Debug received: ", data);
// 	});

// 	send();
// }


// document.getElementById('selectChat').addEventListener('submit', (e) => {
	// 	e.preventDefault();
	// 	const chatId = e.target.chatId.value;
	// 	connect(chatId)
	// 	document.getElementById('startChat').reset();
	// })
	
	// async function apiRequest(token, endpoint, method="GET", authType="Bearer",
	//     contentType="application/json", body=undefined, currentlyRefreshing=false)
	
	// GET https://ft_transcendence.fr/api/chat/
	
	// {
		// 	"q": "string", // filtre la liste en ne gardant que les utilisateurs dont le nom contient 'q'
		//   }
		
async function chatClientInit() {
	await indexInit(false);
}

async function selectChatMenu(filter='') {
	chatList = document.getElementById('chatsList');
	chatList.innerHTML = '';
	console.log('filter', filter);
	try {
		// if (filter) {
		// 	const res = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, undefined, undefined, undefined, {'q' : filter});
		// }
		// else {
		// 	const res = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`);
		// }
		const res = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/?q=${filter}`);
		console.log(res);
	}
	catch(error) {
		console.log(error);
	}
}

chatClientInit();

document.getElementById('selectChat').addEventListener('click', async () => {
	document.getElementById('chatsListView').style.display = 'block';
	selectChatMenu();
	let chatListForm = document.getElementById('searchChatForm');
	chatListForm.addEventListener('keyup', (e) => {
		e.preventDefault();
		selectChatMenu(e.target.value);
	});
});
