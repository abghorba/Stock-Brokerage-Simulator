$(document).ready(function(){

    $('#deposit').children('.btn').on('click', deposit());

});

function deposit() {
    var form = document.getElementById("deposit");
    form.onsubmit = function() {
        if(!form.credit_number.value)
        {
            alert("Missing credit card number!");
            return false;
        }
        if(!form.new_money.value)
        {
            alert("Enter money to be deposited!");
            return false;
        }
        return true;
    }
}