
function changePage(id){
    if (!window.location.href.includes(id))
        history.pushState({}, '', id);

    const url = window.location.pathname;
    console.log(`url: ${url}`);
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.body.innerHTML = data;
        });
}

function triggerPopup(id) {
    if (!window.location.href.includes(id))
        history.pushState({}, '', id);

    const url = window.location.pathname;
    console.log(`url: ${url}`);
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementById(id).innerHTML = data;
        });
}

window.addEventListener('popstate', () => {
    const url = window.location.pathname;
    fetch(url)
        .then(response => response.text())
        .then(data => document.body.innerHTML = data)
})