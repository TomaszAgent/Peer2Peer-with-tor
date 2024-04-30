$(document).ready(function() {
    $("#paramButton").click(function() {
        let address = $("#address").val();
        let msg = $("#msg").val();

        const params = {
            address: address,
            msg: msg
        };

        $.ajax({
            url: '/send',
            type: 'GET',
            data: params,
            success: function(response) {
            
                console.log(response);
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });
});
