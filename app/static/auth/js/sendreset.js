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

function checkEmail() {
    const STATUS_P = document.getElementById('status-p');

    if (STATUS_P.style.visibility == 'visible') {
        STATUS_P.style.visibility = 'hidden';
    }

    const regex = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/;
    
    const email_field = document.getElementById('email-field').value.toLowerCase();
    const button = document.getElementById('email-button');
    
    if (regex.test(email_field)) {
        button.style.opacity = 100;
        button.disabled = false;
        button.style.cursor = 'pointer';
    } else {
        button.style.opacity = 30;
        button.disabled = true;
        button.style.cursor = 'not-allowed';
    }
}

function sendEmail() {
    const STATUS_P = document.getElementById('status-p');
    const EMAIL = document.getElementById('email-field').value;

    fetch('/sendreset', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            email: EMAIL
        })
    }).then((res) => {
        if (res.status == 200) {
            STATUS_P.innerHTML = 'An email has been sent if it matches our records.';
            STATUS_P.style.visibility = 'visible';
            STATUS_P.style.color = 'blue';

            if (res.redirected) {
                let timeout = setTimeout(() => {
                    location.href = res.url;
                    window.clearTimeout(timeout);
                }, 4000); 
            }
        } else {
            STATUS_P.innerHTML = 'Sorry, we were unable to send an email. Please try again.';
            STATUS_P.style.visibility = 'visible'
            STATUS_P.style.color = 'red';
        }
    })
}