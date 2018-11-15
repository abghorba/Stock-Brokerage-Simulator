$(document).ready(function(){

    $('#registration').children('.btn').on('click', register());

});

function register() {
    var form = document.getElementById("registration");

    form.onsubmit = function() {
        var username = form.username.value
        var password = form.password.value;
        var password_confirm = form.confirmation.value;
        var keyword = form.keyword.value

        // https://stackoverflow.com/questions/12090077/javascript-regular-expression-password-validation-having-special-characters
        var regEx = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

        if (!username) {
            alert("Missing username!");
            return false;
        }
        else if (!password) {
            alert("Missing password!");
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
        else if (!form.keyword.value) {
            alert("Missing keyword!");
            return false;
        }
        return true;
    };
}