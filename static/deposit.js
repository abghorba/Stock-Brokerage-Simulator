$(document).ready(function(){

    $('#deposit').children('.btn').on('click', deposit());

});

function deposit() {
    var form = document.getElementById("deposit");

    form.onsubmit = function() {
        var cc_number = form.credit_number.value;
        var money = form.new_money.value;

        if(!cc_number) {
            alert("Missing credit card number!");
            return false;
        }
        if(!money) {
            alert("Enter money to be deposited!");
            return false;
        }
        return true;
    };
}