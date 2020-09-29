$(document).ready(function () {
    $(".addEvent").click(function () {
        let button = $(this);
        button.html(loadButton());
        $.ajax({
            type: "POST",
            url: "/add/" + this.id,
            success: function () {
                button.removeClass("btn-primary");
                button.addClass("btn-secondary");
                button.prop("disabled", true);
                button.html("Added");
            },
            error: function (e) {
                console.log(e);
            },
        });
    });

    $(".addAllEvents").click({ url: "/add/0", text: "Adding..." }, onClick);
    $(".getAppointments").click(
        { url: "/getappointments", text: "Retrieving..." },
        onClick
    );

    function onClick(event) {
        let button = $(this);
        button.html(loadButton(event.data.text));
        $.ajax({
            type: "GET",
            url: event.data.url,
            success: function () {
                window.location.replace("/");
            },
            error: function (e) {
                console.log(e);
            },
        });
    }

    function loadButton(text = "") {
        text = `<span class='spinner-border spinner-border-sm' role='status'></span> ${text}`;
        return text;
    }
});
