$(document).ready(function(){

    $('#buy').children('.btn').on('click', buy());

});

function buy() {
    var form = document.getElementById("buy");

    form.onsubmit = function() {
        var symbol = form.symbol.value;
        var shares = form.shares.value;

        if (!symbol) {
            alert("Missing symbol!");
            return false;
        }
        else if (!shares) {
            alert("Enter shares!");
            return false;
        }
        else if(shares <= 0) {
            alert("Shares must be a positive integer!");
            return false;
        }
        return true;
    };
}