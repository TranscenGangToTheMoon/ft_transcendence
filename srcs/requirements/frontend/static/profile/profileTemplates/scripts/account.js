if (typeof selectedValue === 'undefined'){
    var selectedValue;
}

document.getElementById('pDeleteAccount').addEventListener('click', event => {
    event.preventDefault();
    const deleteAccountModal = new bootstrap.Modal(document.getElementById('pDeleteAccountModal'));
    deleteAccountModal.show();
    window.deleteModal = deleteAccountModal;
})

document.getElementById('pChangePassword').addEventListener('click', event => {
    event.preventDefault();
    const changePasswordModal = new bootstrap.Modal(document.getElementById('pChangePasswordModal'));
    changePasswordModal.show();
    window.changePasswordModal = changePasswordModal;
})

async function deleteAccount(password) {
    sse.close();
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/`, 'DELETE', undefined, undefined, {
        'password' : password
    })
        .then(async data => {
            if (data?.password){
                document.getElementById('pContextError').innerText = data.password;
                initSSE();
            }
            else if (data?.detail){
                initSSE();
                document.getElementById('pContextError').innerText = data.detail;
            }
            else if (!data){
                await navigateTo('/');
                await logOut();
                deleteModal.hide();
                closeChatView();
                setTimeout(()=> {
                    displayMainAlert('Account deleted', 'Your account has been successfully deleted. You have been redirected to homepage.', 'info', 5000);
                }, 300);
            }
        })
        .catch(error => {
            console.log('error', error)
        })
}

async function changePassword(new_password, old_password){
    const newPasswordField = document.getElementById('pPasswordInput');
    const oldPasswordField = document.getElementById('pConfirmPassword');
    const newPasswordFeedback = document.getElementById('pChangePasswordError');
    const oldPasswordFeedback = document.getElementById('pChangeContextError');

    newPasswordField.classList.remove('is-invalid');
    oldPasswordField.classList.remove('is-invalid');
    newPasswordFeedback.innerText = '';
    oldPasswordFeedback.innerText = '';
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'password' : new_password, 'old_password' : old_password});
        if (!data.id){
            console.log(data);
            if (data.password){
                newPasswordField.classList.add('is-invalid');
                newPasswordFeedback.innerText = data.password[0];
            }
            if (data.old_password){
                oldPasswordField.classList.add('is-invalid');
                oldPasswordFeedback.innerText = data.old_password[0];
            }
            // if (data.detail){
            //     oldPasswordField.classList.add('is-invalid');    
            //     newPasswordField.classList.add('is-invalid');
            //     oldPasswordFeedback.innerText = data.detail;
            // }
        }
        else{
            changePasswordModal.hide();
            document.getElementById('pChangePasswordError').innerText = "";
            document.getElementById('pChangeContextError').innerText = "";
            document.getElementById('pPasswordInput').value = "";
            displayMainAlert("password updated", "successfully updated your password.", 'info', 3000);
        }
    }
    catch (error){
        console.log('error on password change', error);
    }
}

document.getElementById('deleteAccountConfirm').addEventListener('submit', event => {
    event.preventDefault();
    deleteAccount(document.getElementById('pConfirmDeletion').value);
})

document.getElementById('changePasswordConfirm').addEventListener('submit', event => {
    event.preventDefault();
    changePassword(document.getElementById('pPasswordInput').value, document.getElementById('pConfirmPassword').value);
})

async function changeUsername(newUsername)
{
    if (!newUsername)
        return; 
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'username' : newUsername});
        if (!data.id) {
            document.getElementById('pChangeNicknameError').innerText = data.username ?? data.detail;
            return false;
        }
        else {
            document.getElementById('pChangeNicknameError').innerText = "";

            await fetchUserInfos(true);
            await indexInit(false);
            displayMainAlert("Nickname updated", `Successfully updated your nickname to '${newUsername}'`, 'info', 5000)
            handleRoute();
            return true;
        }
    }
    catch (error){
        console.log('error on username change', error);
        return false;
    }
}

document.getElementById('bUsername').addEventListener('mouseover', () => {
    const usernameElement = document.getElementById('bUsername');
    if (usernameElement) {
        usernameElement.classList.remove('border-opacity-10');
        usernameElement.classList.add('border-opacity-100');
    }
});
document.getElementById('bUsername').addEventListener('mouseout', () => {
    const usernameElement = document.getElementById('bUsername');
    if (usernameElement) {
        usernameElement.classList.remove('border-opacity-100');
        usernameElement.classList.add('border-opacity-10');
    }
});

document.getElementById('bUsername').addEventListener('click', () => {
    let usernameElement = document.getElementById('bUsername');
    const currentUsername = usernameElement.innerText;
    const inputField = document.createElement('input');
    inputField.id = 'pNicknameInput';
    inputField.className = 'm-0 p-0 align-items-center align-self-center text-truncate';
    inputField.type = 'text';
    inputField.value = currentUsername;
    inputField.style.fontSize = 'calc(1.375rem + 1.5vw)';
    usernameElement.innerHTML = '';
    usernameElement.appendChild(inputField);
    inputField.focus();

    inputField.addEventListener('blur', async function() {
        usernameElement.innerText = userInformations.username;
        document.getElementById('pChangeNicknameError').innerText = "";
    });
    
    inputField.addEventListener('keydown', async function(event) {
        if (event.key === 'Enter') {
            if (inputField.value !== userInformations.username)
                await changeUsername(inputField.value);
            else {
                usernameElement.innerText = userInformations.username;
                document.getElementById('pChangeNicknameError').innerText = "";
            }
        }
        if (event.key === 'Escape') {
            usernameElement.innerText = userInformations.username;
            document.getElementById('pChangeNicknameError').innerText = "";
        }
    });
})

document.getElementById('pDownloadData').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/users/me/download-data/', {
            method: 'GET',
            headers: {
                Authorization: 'Bearer ' + getAccessToken(),
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`Error while downloading: ${response.statusText}`);
        }
        const blob = await response.blob();
        
        const fileURL = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = fileURL;

        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1].replace(/["']/g, '')
            : 'your_data.json';
            
        link.download = filename;
        link.click();
        URL.revokeObjectURL(fileURL);
    } catch (error) {
        console.error('error:', error);
    }
});

function setChatAcceptationOptions(){
	const options = document.getElementById('options').querySelectorAll('.option');
	selectedValue = userInformations.accept_chat_from;

	options.forEach(option => {
  		if (option.dataset.value == selectedValue) {
    		option.classList.add('customSelected');
  		}
  
  		option.addEventListener('click', async () => {
            try {
                await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, 'PATCH', undefined, undefined, {
                    'accept_chat_from': option.dataset.value,
                })
                options.forEach(opt => opt.classList.remove('customSelected'));
                option.classList.add('customSelected');
                selectedValue = option.dataset.value;
            }
            catch(error){
                console.log(error);
            }
 		});
	});
}
function addBannerEventListener() {
    document.getElementById('pProfilePicture').addEventListener('mouseover', () => {
        const pProfilePictureEdit = document.getElementById('pProfilePictureEdit');
        pProfilePictureEdit.style.display = 'block';
    });
    document.getElementById('pProfilePicture').addEventListener('mouseout', () => {
        const pProfilePictureEdit = document.getElementById('pProfilePictureEdit');
        pProfilePictureEdit.style.display = 'none';
    });
    console.log('I\'m here', document.getElementById('pProfilePictureEdit'));
    document.getElementById('pProfilePicture').addEventListener('click', async ()=> {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/profile-pictures/`)
            const profilePicContainer = document.getElementById('profilePicContainer');
            profilePicContainer.innerHTML = '';
            for (i in data){
                let profilePic = data[i];
                const profilePicDiv = document.createElement('div');
                profilePicDiv.classList.add('profile-pic-div');
                profilePicDiv.setAttribute('data-bs-toggle', 'popover');
                profilePicDiv.setAttribute('data-bs-trigger', 'hover');
                profilePicDiv.setAttribute('data-bs-placement', 'top');
                profilePicDiv.setAttribute('data-bs-content', `${profilePic.name} (${profilePic.unlock_reason.slice(0, -1)})`);
                profilePicDiv.innerHTML = `
                <img src=${profilePic.medium} style='cursor: ${profilePic.unlock ? "pointer" : "not-allowed;filter: grayscale(90%);"}'
                class="${profilePic.is_equiped ? 'border border-warning border-2 m-1' : 'm-1'}">
                `
                if (profilePic.unlock && !profilePic.is_equiped){
                    profilePicDiv.addEventListener('click', async ()=> {
                        try {
                            await apiRequest(getAccessToken(), `${baseAPIUrl}/users/profile-picture/${profilePic.id}/`, 'PUT');
                            handleRoute();
                        }
                        catch(error){
                            console.log(error);
                        }
                    })
                }
                profilePicContainer.appendChild(profilePicDiv);
            }
            const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
            popovers.forEach((popover) => {
                new bootstrap.Popover(popover);
            });
        }
        catch(error){
            console.log(error)
        }
        const changeProfilePicModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('pChangeProfilePictureModal'));
        changeProfilePicModal.show();
    });
}
function fillBanner(){
    const usernameDiv = document.getElementById('bUsername');
    usernameDiv.innerText = userInformations.username;
    const profilePicDiv = document.getElementById('pProfilePicture');
    profilePicDiv.innerHTML = `
    <img class="rounded-1" src="${userInformations.profile_picture?.large}" onerror="src='/assets/imageNotFound.png'" style="cursor:pointer;max-width:100px;max-height:100px">
    <img id="pProfilePictureEdit" class="position-absolute top-0 start-0" src='/assets/icon/edit.png' cursor="pointer" style="cursor:pointer;display:none;max-width:40px;max-height:40px" onerror="src='/assets/imageNotFound.png'">
    `
    addBannerEventListener();
}

async function accountInit(){
    if (userInformations.is_guest){
        document.getElementById('pDeleteAccount').classList.add('disabled');
    }
    await fetchUserInfos(true);
    fillBanner();
    setChatAcceptationOptions();
    loadCSS('/profileTemplates/css/profile.css', false);

    loadContent('/blockedUsers/blockedUsers.html', 'blockedModalContainer');
    initSwitch();
} 

accountInit();

document.getElementById('switchAcceptFriendRequests').addEventListener('change', async function (event){
    event.preventDefault();
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, 'PATCH', undefined, undefined, {
            'accept_friend_request': this.checked,
        })
    }
    catch(error){
        console.log(error);
        this.checked=false;
    }
})

function initSwitch(){
    const FRswitch = document.getElementById('switchAcceptFriendRequests');
    if (FRswitch)
        FRswitch.checked = userInformations.accept_friend_request;
    if (userInformations.is_guest)
        document.getElementById('pFriendship').classList.add('d-none');
    else
        document.getElementById('pFriendship').classList.remove('d-none');
}

document.getElementById('seeBlockedUsers').addEventListener('click', async () => {
    await initBlockedUsers();
});
