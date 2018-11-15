$(document).ready(function(){

    $('#quote').children('.btn').on('click', quote());

});

function quote() {
    var form = document.getElementById("quote");

    form.onsubmit = function() {
        var symbol = form.symbol.value; 

        if(!symbol) {
            alert("Missing symbol!");
            return false;
        }
        return true;
    };
}