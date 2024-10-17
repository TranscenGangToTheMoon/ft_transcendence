const baseAPIUrl = "http://localhost:8000/api"
const baseAPIUrlusers = "http://localhost:8005/api/users"

window.baseAPIUrl = baseAPIUrl;
window.baseAPIUrlusers = baseAPIUrlusers;

function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){ 
    let options = {
        method: method,
        headers: {
            "content-type": contentType
        }
    }
    if (token)
        options.headers["Authorization"] = `${authType} ${token}`;
    if (body)
        options.body = JSON.stringify(body);
    console.log(endpoint, options)
    return fetch(endpoint, options)
        .then(response => {
            return response.json();
        })
        .catch(error =>{
            throw error;
        })
}

async function getDataFromApi(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){
    try {
        let data = await apiRequest(token, endpoint, method, authType, contentType, body);
        return data;
    }
    catch (error) {
        console.log(error);
        throw error;
    }
}

function removeTokens(temp=false) {
    if (temp)
    {
        localStorage.removeItem('temp_token');
        localStorage.removeItem('temp_refresh');
    }
    else{
        localStorage.removeItem('token');
        localStorage.removeItem('refresh');
    }
}

function untemporizeTokens() {
    localStorage.setItem('token', localStorage.getItem('temp_token'));
    localStorage.setItem('refresh', localStorage.getItem('temp_refresh'));
    removeTokens(true);
}

window.apiRequest = apiRequest;
window.getDataFromApi = getDataFromApi;
window.removeTokens = removeTokens;
window.untemporizeTokens = untemporizeTokens;


function loadScript(scriptSrc) {
    const script = document.createElement('script');
    script.src = scriptSrc;
    script.onload = () => {
        console.log(`Script ${scriptSrc} loaded.`);
    };
    script.onerror = () => {
        console.error(`Error while loading script ${scriptSrc}.`);
    };
    document.body.appendChild(script);
}

async function loadContent(url) {
    const contentDiv = document.getElementById('content');

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Page non trouvée');
        }
        const html = await response.text();
        contentDiv.innerHTML = html;

        const script = contentDiv.querySelector('[script]');
        if (script)
            loadScript(script.getAttribute('script'));
    } catch (error) {
        contentDiv.innerHTML = '<h1>Erreur 404 : Page non trouvée</h1>';
    }
}

function navigateTo(url, doNavigate=true){
    history.pushState(null, null, url);
    if (doNavigate)
        handleRoute();
}

window.navigateTo = navigateTo;

function handleRoute() {
    const path = window.location.pathname;

    const routes = {
        '/login': '/authentication.html',
        '/': '/homePage.html'
    };

    const page = routes[path] || '/404.html';
    loadContent(page);
}

document.addEventListener('click', event => {
    if (event.target.matches('[data-link]')) {
        event.preventDefault();
        navigateTo(event.target.href);
    }
});

// window.addEventListener('popstate', handleRoute);

handleRoute();
