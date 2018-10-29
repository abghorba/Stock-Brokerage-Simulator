$(document).ready(function(){

    $('#reset').children('.btn').on('click', password_reset());

});

function password_reset() {
    var form = document.getElementById("reset");

    form.onsubmit = function() {
        if (!form.username.value)
        {
            alert("Missing username!");
            return false;
        }
        else if (!form.keyword.value)
        {
            alert("Enter new password!");
            return false;
        }
        else if (!form.new_password.value)
        {
            alert("Enter new password!");
            return false;
        }
        else if (form.new_password.value != form.confirm_new.value)
        {
            alert("Passwords don't match!");
            return false;
        }
        return true;
    };
}