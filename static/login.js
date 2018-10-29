$(document).ready(function(){

    $('#login').children('.btn').on('click', login());

});


function login() {
    var form = document.getElementById("login");

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
        return true;
    };
}
