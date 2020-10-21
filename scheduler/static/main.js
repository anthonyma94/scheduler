$(document).ready(function () {
    $(document).on("click", ".addEvent", function (e) {
        e.data = {
            method: "POST",
            text: "Adding...",
            url: "/add/" + this.id,
        };
        onClick(e);
    });

    $("#dropInButton").click(function (e) {
        e.preventDefault();
        let currentWindow = window.self;
        $(this).html("Host ID: 112233");
        let newWindow = window.open(
            "about:blank",
            this.target,
            "width=10,height=10"
        );
        currentWindow.focus();
        newWindow.location.href = this.href;
        setTimeout(() => newWindow.close(), 300);
        currentWindow.focus();
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
            onClick(e);
        }
    );

    function popUnder(node) {
        $(node).html("Host ID: 112233");
        var newWindow = window.open(
            "about:blank",
            node.target,
            "width=500,height=500"
        );
        newWindow.blur();
        window.focus();
        newWindow.location.href = node.href;
        return false;
    }

    function onClick(event) {
        button = $(event.target);
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
