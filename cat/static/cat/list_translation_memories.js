$(document).ready(function() {
    var source_language = $("select#id_source_language")
    var target_language = $("select#id_target_language")
    var translation_memory = $("select#id_translation_memory")

    source_language.change(function() {
        list_translation_memories()
    })

    target_language.change(function() {
        list_translation_memories()
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