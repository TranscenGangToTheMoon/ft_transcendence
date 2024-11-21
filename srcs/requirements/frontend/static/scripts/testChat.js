document.getElementById('simulateMessageSent').addEventListener('click', async event => {
    event.preventDefault();
    const chatId = document.getElementById('convId').value;
    const message = document.getElementById('message').value;
    if (!chatId || !message)
        return;
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatId}/messages/`, 'POST', undefined, undefined, {
            'content' : message,
        });
    }
    catch (error) {
        console.log(error);
    }
})

async function summonChat(chatId, chatParticipants) {
    const messagesDiv = document.getElementById('messages');
    const participantsDiv = document.getElementById('participants');
    messagesDiv.innerText = "";
    participantsDiv.innerText = "";
    chatParticipants.forEach(participant => {
        participantsDiv.innerText+= `${participant.username}\n`;
    })
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/${chatId}/messages/`, 'GET');
        if (data.count === 0)
            messagesDiv.innerText = "no message in this conversation";
        else {
            data.results.forEach(message => {
                messagesDiv.innerText += `${message.content} (${message.sent_at})\n`;
            })
        }
    }
    catch (error) {
        console.log('ah', error);
    }
}

async function loadExistingChats() {
    const messagesDiv = document.getElementById('existingChats');
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/chat/`, 'GET');
        if (data.count !== 0){
            data.results.forEach(async chat => {
                console.log(JSON.stringify(chat.participants))
                messagesDiv.innerHTML += `<button class="chatConversation btn btn-dark" onclick='summonChat(${chat.id}, ${JSON.stringify(chat.participants)})'>${chat.type} (id : ${chat.id})</button>\n`
                console.log(messagesDiv.innerHTML);
            });
        }
        else
            messagesDiv.innerText = 'no active chat for this user';
    }
    catch (error) {
        console.log(error);
    }
}

async function testChatInit() {
    await indexInit(false);
    await loadExistingChats();
}

testChatInit();