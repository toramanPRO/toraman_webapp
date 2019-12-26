$(document).ready(function() {
    let selected_tab = "project-overview"
    let selected_button = "overview"

    $("button#overview").click(function(){
        navigate_to("project-overview", "overview")
    })
    $("button#pm-settings").click(function(){
        navigate_to("project-pm-settings", "pm-settings")
    })
    $("button#report").click(function(){
        navigate_to("project-report", "report")
    })
    function navigate_to(tab_id, button_id) {
        $("div#" + selected_tab).css("display", "none");
        selected_tab = tab_id
        $("div#" + selected_tab).css("display", "block");

        $("button#" + selected_button).toggleClass("selected")
        selected_button = button_id
        $("button#" + selected_button).toggleClass("selected")
    }
})