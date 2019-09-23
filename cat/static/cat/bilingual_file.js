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
            } else if (e.key == "A" || e.key == "a" || e.key == "Backscape" || e.key == "Delete") {
            } else {
                e.preventDefault()
            }

        } else if (e.key == "Enter") {
            e.preventDefault()
        } else {
            console.log(e.key)
        }
    })

    $("td.target").focusout(function() {
        submit_segment("Draft", $(this))
    })

    function submit_segment(segment_status, target_cell) {
        var target_segment = target_cell.html()
        var paragraph_no = target_cell.closest("tr").find("td.details p.paragraph_no").text()
        var segment_no = target_cell.closest("tr").find("td.details p.segment_no").text()
        $.post(
            $(location). attr("href"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "target_segment": target_segment,
                "segment_status": segment_status,
                "paragraph_no": paragraph_no,
                "segment_no": segment_no,
            },
            function() {
                console.log("Segment #" + segment_no + " submitted successfully.")
            }
        ).fail(function() {
            console.log("Segment #" + segment_no + " submission failed.")
        })
    }
});