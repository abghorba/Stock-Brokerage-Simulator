$(document).ready(function(){

    $('#buy').children('.btn').on('click', buy());

});

function buy() {
    var form = document.getElementById("buy");

    form.onsubmit = function() {
        if (!form.symbol.value)
        {
            alert("Missing symbol!");
            return false;
        }
        else if (!form.shares.value)
        {
            alert("Enter shares!");
            return false;
        }
        else if(form.shares.value <= 0)
        {
            alert("Shares must be a positive integer!");
            return false;
        }
        return true;
    };
}