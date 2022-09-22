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
    input.addEventListener("focus", addfocus)
    input.addEventListener("blur", remfocus)
});

function checkPasswords() {
    const STATUS_P = document.getElementById('status-p');

    if (STATUS_P.style.visibility == 'visible') {
        STATUS_P.style.visibility = 'hidden';
    }

    var regex = /^\s*$/;

    const password_one = document.getElementById('password-one').value;
    const password_two = document.getElementById('password-two').value;
    const button = document.getElementById('reset-button');

    if (!regex.test(password_one) && !regex.test(password_two)) {
        button.style.opacity = 100;
        button.disabled = false;
        button.style.cursor = 'pointer';
    } else {
        button.style.opacity = 30;
        button.disabled = true;
        button.style.cursor = 'not-allowed';
    }
}

function sendReset() {
    const password_one = document.getElementById('password-one').value;
    const password_two = document.getElementById('password-two').value;
    const status_p = document.getElementById('status-p');

    if (password_one !== password_two) {
        status_p.style.visibility = 'visible';
        status_p.innerHTML = 'Your passwords do not match.';
        return;
    }

    const TOKEN = new URL(window.location.href).searchParams.get('token');

    fetch('/reset', {
        method: 'POST',
        body: JSON.stringify({
            token: TOKEN,
            password: btoa(password_one)
        }),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then((res) => {
        if (res.status == 200) {
            status_p.style.visibility = 'visible';
            status_p.style.color = 'Blue';
            status_p.innerHTML = 'Your password has been reset. This page will redirect. If you are not directed, click <a href=\'/login\'>here</a>.'

            if (res.redirected) {
                let timeout = setTimeout(() => {
                    location.href = res.url;
                    window.clearTimeout(timeout);
                }, 4000);
            }
        } else {
            status_p.style.visibility = 'visible';
            status_p.style.color = 'Red';
            status_p.innerHTML = 'Looks like that link is invalid or has expired. Click <a href=\'/sendreset\'>here</a> to get a new link.';
        }
    })
}