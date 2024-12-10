async function unblockUser(userId, divId) {
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/${userId}/`, 'DELETE');
    }
    catch(error) {
        console.log(error);
    }
    document.getElementById(divId).remove();
    nextBlocked = decrementNextBlock(nextBlocked);
    const displayedBlocked = getDisplayedBlockedUsers()
    if (displayedBlocked < 15)
        await getMoreBlocked();
    if (displayedBlocked === 0)
        setBlockedTitle("you haven't block anyone");
}

(async function blockedUserInit(){
    const unblockButtons = document.querySelectorAll('.unblock');
    for (let unblockButton of unblockButtons){
        if (!unblockButton.listened){
            unblockButton.listened = true;
            unblockButton.addEventListener('click', async function (event) {
                const blockId = this.parentElement.parentElement.id;
                await   unblockUser(blockId.substring(7),blockId)
            })
        }
    }
})()
