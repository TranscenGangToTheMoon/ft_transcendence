// async function submitLogin(e) {
// 	e.preventDefault();
// 	await fetch("/submitEndpoint", {
// 		method: "POST",
// 		body: JSON.stringify({
// 			username: document.querySelector("#name").value,
// 			password: document.querySelector("#password").value,
// 		}),
// 	});
// }

const form = document.querySelector("#myform");
console.log(form);
form.addEventListener("submit", (e) => {
	e.preventDefault();
	fetch("/submitEndpoint", {
		method: "POST",
		body: JSON.stringify({
			username: document.querySelector("#name").value,
			password: document.querySelector("#password").value,
		}),
	});
});
