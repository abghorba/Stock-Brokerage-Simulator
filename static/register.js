$(document).ready(function(){

    $('#registration').children('.btn').on('click', register());

});

function register() {
    var form = document.getElementById("registration");

    form.onsubmit = function() {
        if (!form.username.value)
        {
            alert("Missing username!");
            return false;
        }
        else if (!form.password.value)
        {
            alert("Missing password!");
            return false;
        }
        else if (form.password.value != form.confirmation.value)
        {
            alert("Passwords don't match!");
            return false;
        }
        else if (!form.keyword.value)
        {
            alert("Missing keyword!");
            return false;
        }

        return true;
    };
}