$(document).ready(function(){

    $('#quote').children('.btn').on('click', quote());

});

function quote() {
    var form = document.getElementById("quote");

    form.onsubmit = function() {
        if(!form.symbol.value)
        {
            alert("Missing symbol!");
            return false;
        }
        return true;
    };
}