/*===== FOCUS =====*/
const inputs = document.querySelectorAll(".form__input")

/*=== Add focus ===*/
function addfocus(){
    let parent = this.parentNode.parentNode
    parent.classList.add("focus")
}

/*=== Remove focus ===*/
function remfocus(){
    let parent = this.parentNode.parentNode
    if(this.value == ""){
        parent.classList.remove("focus")
    }
}

/*=== To call function===*/
inputs.forEach(input=>{
    input.addEventListener("focus",addfocus)
    input.addEventListener("blur",remfocus)
});

function sendLogin() {
    const EMAIL_OR_USERNAME = document.getElementById('username-or-email').value;
    const PASSWORD = document.getElementById('password').value;

    fetch('/login', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            username: EMAIL_OR_USERNAME,
            password: btoa(PASSWORD)
        })
    }).then(function (res) {
        if (res.status == 200) { 
            if (res.redirected) {
                window.location.href = res.url;
            }
        } else {
            const STATUS_P = document.getElementById('status-p');

            STATUS_P.style.visibility = 'visible';
            STATUS_P.innerHTML = "Your credentials are incorrect."
        }
    }).catch(function (err) {
        
    });
}
        

function checkFields() {
    const EMAIL_OR_USERNAME = document.getElementById('username-or-email').value;
    const PASSWORD = document.getElementById('password').value;

    const STATUS_P = document.getElementById('status-p');

    if (STATUS_P.style.visibility == 'visible') {
        STATUS_P.style.visibility = 'hidden';
    }

    if (EMAIL_OR_USERNAME.trim() != "" && PASSWORD.trim() != "") {
        document.getElementById('login-button').disabled = false;
        document.getElementById('login-button').style.opacity = 100;
        document.getElementById('login-button').style.cursor = 'pointer';
    } else {
        document.getElementById('login-button').disabled = true;
        document.getElementById('login-button').style.opacity = 30;
        document.getElementById('login-button').style.cursor = 'not-allowed';
    }
}