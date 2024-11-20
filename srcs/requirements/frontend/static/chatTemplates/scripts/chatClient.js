let socket;

function connect() {
	socket = io("wss://localhost:8000/chat");
	console.log("Connecting to the server...");
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
	});

	socket.on("error", (error) => {
		console.log("Error: ", error);
	});
}

async function chatClientInit() {
	await indexInit(false);
}

chatClientInit();
connect();
console.log("I've been there");