$(document).ready(function(){

    $('#reset').children('.btn').on('click', password_reset());

});

function password_reset() {
    var form = document.getElementById("reset");

    form.onsubmit = function() {
        var username = form.username.value
        var keyword = form.keyword.value
        var password = form.new_password.value;
        var password_confirm = form.confirm_new.value;
        
        // https://stackoverflow.com/questions/12090077/javascript-regular-expression-password-validation-having-special-characters
        var regEx = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

        if (!username) {
            alert("Missing username!");
            return false;
        }
        else if (!keyword) {
            alert("Enter new password!");
            return false;
        }
        else if (!password) {
            alert("Enter new password!");
            return false;
        }
        else if (password.search(regEx) < 0) {
            alert("Password must be at least 8 characters long, and have at least one lowercase, uppercase, and special character!");
            return false;
        }
        else if (password != password_confirm) {
            alert("Passwords don't match!");
            return false;
        }
        return true;
    };
}