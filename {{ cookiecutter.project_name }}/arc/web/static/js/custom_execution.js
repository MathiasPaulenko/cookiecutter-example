$(document).ready(() => {
    let deleteModal = document.getElementById('deleteCustomExecution');
    $(deleteModal).on('show.bs.modal', function (event) {
        let element = $(deleteModal);
        // Button that triggered the modal
        let button = $(event.relatedTarget);
        // Extract info from data-bs-* attributes
        let executionName = button.attr('data-custom-execution-name');
        let executionId = button.attr('data-custom-execution-id');
        // Update the modal's content.
        let modalTitle = element.find('.modal-title');
        let modalBodyConfirmation = element.find('.modal-body-confirmation');
        let modalForm = element.find('#deleteSettingForm');

        modalTitle.text(`Delete setting with name '${executionName}'`)
        modalBodyConfirmation.text(`Please, confirm you want to delete the custom execution configuration with name '${executionName}'`)
        modalForm.attr('action', `/custom_execution/delete/${executionId}/`)
    });

    // Save button
    $("#saveExecution").click(() => {
        fillTags()
        $("#save_execution").attr('checked', true)
        $("#custom_execution_form").submit()
    });

    $("#runButton").click(()=>{
        fillTags()
        $("#custom_execution_form").submit()
    })

    // Load button
    $(".select_custom_execution").click((e) => {
        let customExecutionId = $(e.currentTarget).attr('data-custom-execution-id')
        get_execution_data_by_id(customExecutionId);
    });

});


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

async function get_execution_data_by_id(execution_id) {
    // Send the get request to get a json with the date labels, passed and failed executions.
    await fetch(`/api/custom_execution/${execution_id}/`)
        .then(response => response.json())
        .then((data) => {
            update_custom_execution_form_data(data)
        });
}

function update_custom_execution_form_data(data) {
    selectedTags = data.tags.split(', ');
    let tags_field = $("#tags_added");
    tags_field.html("");
    $("#tags").val("");
    for (let tag of selectedTags){
        let tag_text = `<span data-tag='${tag}' id='${tag}_tag' class="d-inline-block text-primary p-1">${tag}<button onclick="removeTag('${tag}_tag')" class="btn btn-sm border-0 btn-outline-danger pb-2 mx-1">x</button></span>`;
        tags_field.html(tags_field.html() + tag_text);
    }
    $("#id").val(data.id);
    $("#name").val(data.name);
    $("#conf_properties").val(data.conf_properties);
    if (data.headless === true){
        $("#headless").attr('checked', 'checked');
    }else{
        $("#headless").removeAttr('checked');
    }
    $("#environment").val(data.environment);
    $("#tags").val(data.tags);
    $("#extra_arguments").val(data.extra_arguments);
}