document.getElementById('settingsButton').addEventListener('click', event => {
    event.preventDefault();
    const settingsModal = new bootstrap.Modal(document.getElementById('lobbySettingsModal'));
    settingsModal.show();
})

async function lobbyInit() {
    await indexInit(false);
}

lobbyInit();