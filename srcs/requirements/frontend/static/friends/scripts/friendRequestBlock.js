// document.querySelector('.declineFriendRequest').addEventListener('click', function(event) {
//     console.log('declined friend request ', this.parentElement.parentElement.id);
// })

// document.querySelector('.acceptFriendRequest').addEventListener('click', function(event) {
//     console.log('accepted friend request ', this.parentElement.parentElement.id);
// })

(function friendRequests(){
    const declineButtons = document.querySelectorAll('.declineFriendRequest');

    for (let declineButton of declineButtons){
        if (!declineButton.listened){
            declineButton.addEventListener('click', event => {
                console.log('declined friend request: ', declineButton.parentElement.parentElement.id);
            })
        }
        declineButton.listened = true;
    }

    const acceptButtons = document.querySelectorAll('.acceptFriendRequest');

    for (let acceptButton of acceptButtons){
        if (!acceptButton.listened){
            acceptButton.addEventListener('click', event => {
                console.log('accepted friend request: ', acceptButton.parentElement.parentElement.id);
            })
        }
        acceptButton.listened = true;
    }
})()



// console.log(document.querySelector('.declineFriendRequest'))
// console.log(document.querySelector('.acceptFriendRequest'))
// console.log(document.querySelectorAll('declineFriendRequest'));