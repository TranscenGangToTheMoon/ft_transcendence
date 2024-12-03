function connect(chatId) {
	let socket = io("wss://localhost:4443", {
		path: "/ws/chat/",
		extraHeaders: {
			"token": getAccessToken(),
			"chatId": chatId
		}
	});
	window.socket = socket;
	console.log("Connecting to the server...");
	setupSocketListeners();
	return true;
}


function send() {
	let chatForm = document.getElementById('chat-form');
	chatForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const message = e.target.message.value;
		socket.emit('message', { 'message': message });
		console.log('Message sent: ', message);
		chatForm.reset();
	});
}


function setupSocketListeners()
{
	document.getElementById('endChat').addEventListener('click', () => {
		socket.disconnect();
	});
	document.getElementById('logOut').addEventListener('click', () => {
		socket.disconnect();
	});

	const chatBox = document.getElementById('chats-box');

	socket.off("connect");
    socket.off("disconnect");
    socket.off("message");
    socket.off("error");
	socket.off("debug");
	
	socket.on("connect", () => {
		console.log("Connected to the server");
		document.getElementById('startChat').style.display = 'none';
		document.getElementById('chat-view').style.display = 'block';
	});
	
	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
		console.log("Closing the connection to the server...");
		document.getElementById('startChat').style.display = 'block';
		document.getElementById('chat-view').style.display = 'none';
		chatBox.innerHTML = "";
		socket = null;
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

async function chatClientInit() {
	await indexInit(false);
}

chatClientInit();

document.getElementById('startChat').addEventListener('submit', (e) => {
	e.preventDefault();
	const chatId = e.target.chatId.value;
	connect(chatId)
	document.getElementById('startChat').reset();
})
