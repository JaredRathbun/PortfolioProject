$(document).ready(function() {
    $("#show_hide_password button").on('click', function(event) {
        console.log('in function');
        event.preventDefault();
        if($('#show_hide_password input').attr("type") == "text"){
            $('#show_hide_password input').attr('type', 'password');
            $('#show_hide_password i').addClass( "fa-eye-slash" );
            $('#show_hide_password i').removeClass( "fa-eye" );
        }else if($('#show_hide_password input').attr("type") == "password"){
            $('#show_hide_password input').attr('type', 'text');
            $('#show_hide_password i').removeClass( "fa-eye-slash" );
            $('#show_hide_password i').addClass( "fa-eye" );
        }
    });
});

function showAPIToken(apiToken) {
    const API_TOKEN = apiToken;

    // const html = `
    //     <div style="width: 500px">
    //         <div class="form-group">
    //             <div class="input-group" id="">
    //                 <input class="form-control" type="password" placeholder=${API_TOKEN}>
    //             </div>
    //         </div>
    //     </div>
    // `;

    Swal.fire({
        title: '<h4>View API Token</h4>',
        text: API_TOKEN,
        confirmButtonText: 'Okay'
    });
}

