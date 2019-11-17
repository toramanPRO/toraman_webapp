$(document).ready(function() {
    var source_language = $("input#id_source_language")
    var target_language = $("input#id_target_language")
    var translation_memory = $("select#id_translation_memory")

    source_language.change(function() {
        if (source_language.val().length == 2 && target_language.val().length == 2) {
            list_translation_memories()
        }
    })

    target_language.change(function() {
        if (source_language.val().length == 2 && target_language.val().length == 2) {
            list_translation_memories()
        }
    })

    function list_translation_memories() {
        $.get(
            "translation-memory-query",
            {
                "source_language": source_language.val(),
                "target_language": target_language.val(),
            },
            function(data) {
                translation_memory.html((data))
            }
        ).fail(function() {
            translation_memory.html("<option value=\"---\">N/A</option>")
        })
    }
});