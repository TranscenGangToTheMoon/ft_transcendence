const chatBox = document.getElementById('chats-box');
let socket;


function connect() {
	socket = io("wss://localhost:4443", {
		path: "/ws/chat/"
	});
	setupSocketListeners();
}

function setupSocketListeners()
{
	socket.on("connect", () => {
		console.log("Connected to the server");
	});

	socket.on("disconnect", () => {
		console.log("Disconnected from the server");
	});

	socket.on("message", (data) => {
		console.log("Message received: ", data);
		chatBox.insertAdjacentHTML('beforeend', `<div><p>: ${data.message}</p></div>`);
	});

	let chatForm = document.getElementById('chat-form');
	chatForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const message = e.target.message.value;
		socket.emit('message', { 'message': message });
		console.log('Message sent: ', message);
		chatForm.reset();
	});

}

async function chatClientInit() {
	await indexInit(false);
}

chatClientInit();
connect();
console.log("I've been there");