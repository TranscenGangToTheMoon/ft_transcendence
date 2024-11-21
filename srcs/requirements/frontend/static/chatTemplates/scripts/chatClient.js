let socket;

function connect() {
	socket = io("ws://localhost:8010");
	// socket = io("wss://localhost:8010");
	// socket = io("wss://localhost:4443/wss/chat");
	console.log("======");
	console.log(socket);
	console.log("Connecting to the server...");
	setupSocketListeners();
	console.log("Prout...");
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

	socket.on("ping", (data) => {
		console.log("Ping received: ", data);
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