$(document).ready(function(){

    $('#sell').children('.btn').on('click', sell());

});

function sell() {
    var form = document.getElementById("sell");

    form.onsubmit = function() {
        var symbol = form.symbol.value;
        var shares = form.shares.value;

        if(!symbol) {
            alert("Select symbol!");
            return false;
        }
        if(!shares) {
            alert("Enter shares!");
            return false;
        }
        return true;
    };
}