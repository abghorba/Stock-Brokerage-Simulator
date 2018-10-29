$(document).ready(function(){

    $('#sell').children('.btn').on('click', sell());

});

function sell() {
    var form = document.getElementById("sell");

    form.onsubmit = function() {
        if(!form.symbol.value)
        {
            alert("Select symbol!");
            return false;
        }
        if(!form.shares.value)
        {
            alert("Enter shares!");
            return false;
        }
        return true;
    };
}