$(document).ready(function () {
    $(".addEvent").on("click", { method: "POST", text: "Adding..." }, function (
        e
    ) {
        e.data.url = "/add/" + this.id;
        onClick(e, $(this));
    });

    $(".addAllEvents").on(
        "click",
        { method: "GET", url: "/add/0", text: "Adding..." },
        onClick
    );
    $(".getAppointments").on(
        "click",
        { method: "GET", url: "/getappointments", text: "Retrieving..." },
        function (e) {
            checkProgress();
            onClick(e, $(this));
        }
    );

    function onClick(event, button = $(this)) {
        console.log(button);
        button.data("previousState", button.html());
        button.html(loadButton(event.data.text));

        $.ajax({
            type: event.data.method,
            url: event.data.url,
            success: function () {
                window.location.replace("/");
            },
            error: function (jqXHR, status, error) {
                errorFunc(jqXHR, status, error, button);
            },
        });
    }

    function checkProgress() {
        let bar = $("#progressRow");
        bar.collapse("show");
        $.ajax({
            type: "GET",
            url: "/progress",
            success: function (data) {
                let progress = data.progress;
                let bar = $(".progress-bar");
                if (progress >= 0 && progress <= 100) {
                    bar.attr("aria-valuenow", progress).css(
                        "width",
                        progress + "%"
                    );
                    bar.text(progress + "%");
                    setTimeout(checkProgress, 1000);
                } else {
                    bar.collapse("hide");
                    clearTimeout(checkProgress);
                }
            },
            error: function () {
                bar.collapse("hide");
                clearTimeout(checkProgress);
            },
        });
    }

    function loadButton(text = "") {
        text = `<span class='spinner-border spinner-border-sm' role='status'></span> ${text}`;
        return text;
    }

    function errorFunc(jqXHR, status, error, button) {
        button.html(button.data("previousState"));
        let alert = $("#topAlert");
        let div = alert.closest(".container-fluid");
        alert.addClass("alert-danger").html(jqXHR.responseText);
        div.collapse("show");
        div.on("shown.bs.collapse", function () {
            setTimeout(() => div.collapse("hide"), 3000);
        });
    }
});
