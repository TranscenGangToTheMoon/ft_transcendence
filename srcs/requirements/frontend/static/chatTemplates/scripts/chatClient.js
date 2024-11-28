const chatBox = document.getElementById('chats-box');
let socket;
let chatId = 1;


function connect() {
	socket = io("wss://localhost:4443", {
		path: "/ws/chat/"
	});
	console.log("Connecting to the server...");
	document.getElementById('chat-start-form').style.display = 'none';
	document.getElementById('chat-view').style.display = 'block';
	setupSocketListeners();
}

function disconnect() {
	socket.disconnect();
	console.log("Closing the connection to the server...");
	document.getElementById('chat-start-form').style.display = 'block';
	document.getElementById('chat-view').style.display = 'none';
}

function authentificate() {
	let authForm = document.getElementById('auth-form');
	authForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const chatID = e.target.chatID.value;
		console.log('chatID: ', chatID);
		socket.emit('auth', { 'token':getAccessToken(), 'chatID': chatID });
		console.log('Authentification in progress...');
		authForm.reset();
	});
}


function startchat() {
	let chatStartForm = document.getElementById('chat-start-form');
	chatStartForm.addEventListener('submit', (e) => {
		e.preventDefault();
		connect();
	});
}

function endchat() {
	let chatEndForm = document.getElementById('chat-end-form');
	chatEndForm.addEventListener('submit', (e) => {
		e.preventDefault();
		disconnect();
	});
}

function setupSocketListeners()
{
	socket.on("connect", () => {
		console.log("Connected to the server");
	});

	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
		//chatBox.innerHTML = "";
	});

	socket.on("message", (data) => {
		console.log("Message received: ", data);
		chatBox.insertAdjacentHTML('beforeend', `<div><p>: ${data.message}</p></div>`);
	});

	socket.on("error", (data) => {
		console.log("Error received: ", data);
		disconnect();
	});

	socket.on("debug", (data) => {
		console.log("Debug received: ", data);
	});

	let chatForm = document.getElementById('chat-form');
	chatForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const message = e.target.message.value;
		socket.emit('message', { 'message': message });
		console.log('Message sent: ', message);
		chatForm.reset();
	});
	authentificate();
	endchat();
}

async function chatClientInit() {
	await indexInit(false);
}

chatClientInit();
startchat();