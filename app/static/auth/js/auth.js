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

function checkOTP() {
    const OTP_CODE = document.getElementById('otp-code').value;

    if (OTP_CODE.length === 6) {
        document.getElementById('auth-button').disabled = false;
        document.getElementById('auth-button').style.opacity = 100;
        document.getElementById('auth-button').style.cursor = 'pointer';
    } else {
        document.getElementById('auth-button').disabled = true;
        document.getElementById('auth-button').style.opacity = 30;
        document.getElementById('auth-button').style.cursor = 'not-allowed';
    }
}

function sendOTP() {
    const OTP_CODE = document.getElementById('otp-code').value;

    fetch('/auth', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            otp: OTP_CODE
        })
    }).then((res) => {
        if (res.status == 200) {
            if (res.redirected) {
                window.location.href = res.url;
            }
        } else {
            const STATUS_P = document.getElementById('status-p');

            STATUS_P.style.visibility = 'visible';
            STATUS_P.innerHTML = "Sorry, looks like that OTP is not valid.";
        }
    })
}