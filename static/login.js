$(document).ready(function(){

    $('#login').children('.btn').on('click', login());

});

function login() {
    var form = document.getElementById("login");

    form.onsubmit = function() {
        var username = form.username.value;
        var password = form.password.value;

        if (!username) {
            alert("Missing username!");
            return false;
        }
        else if (!password) {
            alert("Missing password!");
            return false;
        }
        return true;
    };
}
