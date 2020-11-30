$(document).ready(function () {
    var table = $("#appointments").DataTable({
        ajax: "/api/get",
        columns: [
            { data: "sort" },
            { data: "start" },
            { data: "end" },
            { data: "name" },
            { data: "course" },
            { data: "comments" },
            { data: "esl" },
            {
                data: "id",
                render: (data) => `<a href="/appointment/${data}">View</a>`,
            },
            {
                data: "added",
                render: (data, type, row) =>
                    `<button id="${row.id}" class="btn btn-${
                        data ? "secondary" : "primary"
                    } addEvent ${data ? "disabled" : ""}">${
                        data ? "Added" : "Add"
                    }</button>`,
            },
        ],
        order: [[1, "asc"]],
        responsive: true,
        columnDefs: [
            { targets: 0, visible: false, searchable: false },
            { targets: [1, 2], orderData: 0 },
            { targets: [5, 7, 8], orderable: false },
            { responsivePriority: 1, targets: [1, 3, 4] },
            { responsivePriority: 2, targets: [2, 5] },
        ],
    });

    $(".dataTables_filter input")
        .off()
        .on("keyup focusout", function () {
            if (
                this.value === null ||
                this.value === undefined ||
                this.value === false ||
                this.value === ""
            ) {
                table.ajax.url("/api/get").load();
            } else if (this.value.length > 2) {
                table.ajax.url(`/search?text=${this.value}`).load();
            }
        });

    $("#appointments").on("click", ".addEvent", function (e) {
        e.data = {
            method: "GET",
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
        setTimeout(() => newWindow.close(), 1000);
        currentWindow.focus();
    });

    $(".addAllEvents").on(
        "click",
        { method: "GET", url: "/add/0", text: "Adding..." },
        onClick
    );
    $(".getAppointments").on(
        "click",
        {
            method: "GET",
            url: "/getappointments",
            text: "Retrieving...",
        },
        onClick
    );

    function onClick(event) {
        const { method, url, text } = event.data;
        button = $(event.target);
        button.data("previousState", button.html());
        button.html(loadButton(text));

        $.ajax({
            type: method,
            url,
            success: function (data) {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    button.html(button.data("previousState"));
                    if ($(button).hasClass("addEvent")) {
                        table.ajax.url("/api/get").load();
                    } else {
                        location.reload();
                    }
                }
            },
            error: function (jqXHR, status, error) {
                errorFunc(jqXHR, status, error, button);
            },
        });
    }

    function checkProgress() {
        let row = $("#progressRow");
        row.collapse("show");
        $.ajax({
            type: "GET",
            url: "/progress",
            success: function (data) {
                let progress = data.progress;
                console.log(progress);
                let bar = $(".progress-bar");
                if (progress >= 0 && progress <= 100) {
                    bar.attr("aria-valuenow", progress).css(
                        "width",
                        progress + "%"
                    );
                    bar.text(progress + "%");
                    setTimeout(checkProgress, 100);
                } else {
                    row.collapse("hide");
                    clearTimeout(checkProgress);
                }
            },
            error: function () {
                row.collapse("hide");
                clearTimeout(checkProgress);
            },
        });
    }

    function loadButton(text = "") {
        text = `<span class='spinner-border spinner-border-sm' role='status'></span> ${text}`;
        return text;
    }

    function errorFunc(jqXHR, status, error, button) {
        console.log(jqXHR);
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
