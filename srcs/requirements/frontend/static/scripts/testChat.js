// document.getElementById('sendMessage').addEventListener('click', event => {
//     event.preventDefault();
//     const message = document.getElementById('message').value;
//     if (!message)
//         document.getElementById('container').innerText = "";
//     else
//         document.getElementById('container').innerText = `Message: ${message}`;
// })

document.getElementById('getMessages').addEventListener('click', async event => {
    event.preventDefault();
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'GET');
        console.log(data);
    }
    catch (error){
        console.log(error);
    }
})

document.getElementById('getContentById').addEventListener('click', async event => {
    event.preventDefault();
    const chatId = document.getElementById('chatId').value;
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatId}/messages`, 'GET');
        console.log(data);
    }
    catch (error) {
        console.log(error);
    }
})

document.getElementById('sendMessage').addEventListener('click', async event => {
    event.preventDefault();
    const chatId = document.getElementById('mChatId').value;
    const messageContent = document.getElementById('messageContent').value;
    if (!chatId || !messageContent)
        return console.log('fields must not be blank');
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatId}/messages/`, 'POST', undefined, undefined, {
            'content' : messageContent,
        });
        console.log(data);
    }
    catch (error) {
        console.log('error', error);
    }
})

async function loadExistingChats() {
    const messagesDiv = document.getElementById('existingChats');
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'GET');
        if (data.count !== 0){
            data.results.forEach(async chat => {
                let messages = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chat.id}/messages/`, 'GET');
                if (messages.count !== 0) {
                    messages.results.forEach(message => {
                        messagesDiv.innerText += `${message.content} (${message.sent_at})\n`;
                    })
                }
            });
        }
    }
    catch (error) {
        console.log(error);
    }
}

async function testChatInit() {
    await indexInit(false);
    loadExistingChats();
}

testChatInit();