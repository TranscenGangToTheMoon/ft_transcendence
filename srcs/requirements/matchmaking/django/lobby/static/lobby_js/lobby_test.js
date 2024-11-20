let url = `ws://${window.location.host}/lobby/`
let socket = new WebSocket(url);

socket.onopen = function() {
	console.log('WebSocket connection established.');
	const message = {
		'message': 'Hello, world!'
	};
	socket.send(JSON.stringify(message));
};
socket.onmessage = function(event) {
	const message = JSON.parse(event.data);
	console.log('Received message:', message);
};

let button = document.getElementById('button');

button.onclick = function() {
	socket.send(JSON.stringify({'message': 'start'}));
}
