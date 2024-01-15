/*
This file contains specific functions for the Custom Run Interface (Groups Run)
*/


$(document).ready(()=>{
    $("#runButton").click(()=>run_by_tag());
})

function run_by_tag() {
    /*
    This function prepares the form to Run tags added in the tags field and take the configuration selected
    */
    fillTags()
    $("#run_form").submit()
}

function fillTags(){
    $("#tags").val("")
    let tags_text = ""
    for (const tag of selectedTags) {
        if (tag === selectedTags.at(-1)) {
            tags_text += `${tag}`
        } else {
            tags_text += `${tag}, `
        }
    }
    $("#tags").val(tags_text);
}
