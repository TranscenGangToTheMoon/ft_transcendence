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
    if (doNavigate  )
        handleRoute();
}

window.navigateTo = navigateTo;

function handleRoute() {
    const path = window.location.pathname;

    const routes = {
        '/': '/homePage.html',
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
