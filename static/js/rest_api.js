$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#payment_id").val(res.id);
        $("#payment_user_id").val(res.user_id);
        $("#payment_order_id").val(res.order_id);
        // if (res.status === 1) {
        //     $("#payment_status").val("UNPAID");
        // } else if (res.status === 2) {
        //     $("#payment_status").val("PROCESSING");
        // } else {
        //     $("#payment_status").val("PAID");
        // }
        $("#payment_status").val(res.status);
        $("#method_id").val(res.method_id);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#payment_id").val("");
        $("#payment_user_id").val("");
        $("#payment_order_id").val("");
        $("#payment_status").val("1");
        $("#method_id").val("1");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a payment
    // ****************************************

    $("#create-btn").click(function () {

        var user_id = parseInt($("#payment_user_id").val());
        var order_id = parseInt($("#payment_order_id").val());
        var status = parseInt($("#payment_status").val());
        var method_id = parseInt($("#payment_method_id").val());

        var data = {
            "user_id": user_id,
            "order_id": order_id,
            "status": status,
            "method_id": method_id
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/payments",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a payment
    // ****************************************

    $("#update-btn").click(function () {

        var payment_id = parseInt($("#payment_id").val());
        var user_id = parseInt($("#payment_user_id").val());
        var order_id = parseInt($("#payment_order_id").val());
        var status = parseInt($("#payment_status").val());
        var method_id = parseInt($("#payment_method_id").val());

        var data = {
            "user_id": user_id,
            "order_id": order_id,
            "status": status,
            "method_id": method_id
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/payments/" + payment_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a payment
    // ****************************************

    $("#retrieve-btn").click(function () {

        var payment_id = $("#payment_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/payments/" + payment_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a payment
    // ****************************************

    $("#delete-btn").click(function () {

        var payment_id = $("#payment_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/payments/" + payment_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Payment with ID [" + res.id + "] has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#payment_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a payment
    // ****************************************

    $("#search-btn").click(function () {

        var user_id = $("#payment_user_id").val();
        var order_id = $("#payment_order_id").val();
        var status = $("#payment_status").val();
        var method_id = $("#payment_method_id").val();

        var queryString = ""

        if (user_id) {
            queryString += 'user_id=' + user_id
        }
        if (order_id) {
            if (queryString.length > 0) {
                queryString += '&order_id=' + order_id
            } else {
                queryString += 'order_id=' + order_id
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }
        if (method_id) {
            if (queryString.length > 0) {
                queryString += '&method_id=' + method_id
            } else {
                queryString += 'method_id=' + method_id
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/payments?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">User ID</th>'
            header += '<th style="width:40%">Order ID</th>'
            header += '<th style="width:10%">Status</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                payment = res[i];
                var row = "<tr><td>"+payment.id+"</td><td>"+payment.user_id+"</td><td>"+payment.order_id+"</td><td>"+payment.status+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
