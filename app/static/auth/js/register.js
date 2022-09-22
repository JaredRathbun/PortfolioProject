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
})

function checkFields() {
    const STATUS_P = document.getElementById('status-p');

    if (STATUS_P.style.visibility == 'visible') {
        STATUS_P.style.visibility = 'hidden';
    }

    const EMAIL = document.getElementById('email').value;
    const USERNAME = document.getElementById('username').value;
    const PASSWORD_1 = document.getElementById('password').value;
    const PASSWORD_2 = document.getElementById('re-password').value;

    if (EMAIL.trim() != "" && USERNAME.trim() != "" && PASSWORD_1.trim() != "" 
        && PASSWORD_2.trim() != "") {
        document.getElementById('register-button').disabled = false;
        document.getElementById('register-button').style.opacity = 100;
        document.getElementById('register-button').style.cursor = 'pointer';
    } else {
        document.getElementById('register-button').disabled = true;
        document.getElementById('register-button').style.opacity = 30;
        document.getElementById('register-button').style.cursor = 'not-allowed';
    }
}

function sendRegister() {
    const EMAIL = document.getElementById('email').value;
    const USERNAME = document.getElementById('username').value;
    const PASSWORD_1 = document.getElementById('password').value;
    const PASSWORD_2 = document.getElementById('re-password').value;

    const STATUS_P = document.getElementById('status-p')

    if (PASSWORD_1 !== PASSWORD_2) {
        STATUS_P.style.visibility = 'visible';
        STATUS_P.innerHTML = 'Your passwords do not match.';
    } else if (!document.getElementById('email').value.toLowerCase().match(
        /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/
        )) {
            STATUS_P.style.visibility = 'visible';
            STATUS_P.innerHTML = 'Please enter a valid email address.';
    } else {
        fetch('/register', {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({
                email: EMAIL,
                username: USERNAME,
                password: btoa(PASSWORD_1)
            })
        }).then(function (res) {
            if (res.status == 200) {
                if (res.redirected) {
                    window.location.href = res.url;
                }
            } else {
                STATUS_P.style.visibility = 'visible';
                STATUS_P.innerHTML = 'Sorry, an account with that username/email already exists.';
            }
        }).catch(function (err) {
            
        });
    }
}

function checkEmail() {
    const valid = document.getElementById('email').value.toLowerCase().match(
        /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/
    );
    
    const email_logo = document.getElementById('email-logo');
    console.log(email_logo.classList);
    if (valid) {
        email_logo.classList.remove('bx-envelope');
        email_logo.classList.add('envelope-check');
    } else {
        email_logo.classList.remove('envelope-check');
        email_logo.classList.add('bx-envelope');
    }
}