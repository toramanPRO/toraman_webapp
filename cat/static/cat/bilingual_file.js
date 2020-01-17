$(document).ready(function() {
    var csrf_token = $("[name=csrfmiddlewaretoken]").val();
    var file = $(document).attr('title');

    $("td.source tag").click(function() {
        var target_segment = $(this).closest("tr").find("td.target");
        $(this).clone().appendTo(target_segment);
    })

    $("td.target").keydown(function(e) {
        if (e.ctrlKey) {
            if (e.key == "Enter") {
                e.preventDefault()

                submit_segment("Translated", $(this))
            } else if (e.key == "Insert") {
                e.preventDefault()
                var source_html = $(this).closest("tr").find("td.source").html()
                $(this).html(source_html);
            } else if (e.key == "A"
                    || e.key == "a"
                    || e.key == "Backspace"
                    || e.key == "Delete"
                    || e.key == "C"
                    || e.key == "c"
                    || e.key == "X"
                    || e.key == "x"
                    || e.key == "V"
                    || e.key == "v"
                    || e.key == "Z"
                    || e.key == "z"
                    || e.key == "ArrowLeft"
                    || e.key == "ArrowRight") {
            } else {
                e.preventDefault()
            }

        } else if (e.key == "Enter") {
            e.preventDefault()
        } else {
            $(this).closest("tr").addClass("draft")
            $(this).closest("tr").removeClass("translated")
        }
    })

    $("td.target").focusin(function() {
        lookup_segment($(this))
    })

    $("td.target").focusout(function() {
        if ($(this).closest("tr").hasClass("draft")) {
            submit_segment("Draft", $(this))
        }
    })

    function lookup_segment(target_cell) {
        var source_segment = target_cell.closest("tr").find("td.source").html()

        $.get(
            $(location).attr("href"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "procedure": "lookup",
                "source_segment": source_segment,
            },
            function(html) {
                $("table#tm-hits").html(html);
            }
        )
    }

    function submit_segment(segment_status, target_cell) {
        var source_segment = target_cell.closest("tr").find("td.source").html()
        var target_segment = target_cell.html().replace(/&nbsp;/g, ' ')
        var paragraph_no = target_cell.closest("tr").find("td.details p.paragraph-no").text()
        var segment_no = target_cell.closest("tr").find("td.details p.segment-no").text()

        var segment_no_list = []
        var exact_segment

        if (segment_status == "Translated") {
            target_cell.closest("tr").addClass("translated")
            target_cell.closest("tr").removeClass("draft")
        }

        $.post(
            $(location).attr("href"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "source_segment": source_segment,
                "target_segment": target_segment,
                "segment_status": segment_status,
                "paragraph_no": paragraph_no,
                "segment_no": segment_no,
            },
            function(data) {
                console.log("Segment #" + segment_no + " submitted successfully.")
                if (segment_status == "Translated" && data != "") {
                    segment_no_list = data.split(', ')
                    for (i = 0; i < segment_no_list.length; i++) {
                        exact_segment = $("tr.segment#" + segment_no_list[i])
                        exact_segment.find("td.target").html(target_segment)
                        exact_segment.addClass("translated")
                    }
                }
                if (segment_status == "Translated") {
                    target_cell.closest("tr").nextAll().not(".translated").first().find("td.target").focus()
                }
            }
        ).fail(function() {
            console.log("Segment #" + segment_no + " submission failed.")

            if (segment_status == "Translated") {
                target_cell.closest("tr").removeClass("translated")
            }
            target_cell.closest("tr").addClass("draft")
        })
    }
});
