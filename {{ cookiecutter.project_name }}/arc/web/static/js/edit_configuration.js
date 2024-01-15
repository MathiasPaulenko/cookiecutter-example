$(document).ready(()=>{
    let customSections = {}
    let removeSections = {}
    let sections = $('form.settings_form').find('a[data-bs-toggle="collapse"]');

    /*
        This function add the click event to the add_section_button.
        Append a new section given a name and also add the events
        to add a new option to this section and remove the section
    */
    const addSection = (custom_new_section, add_section_button)=> {
        const newSection = $('#add_new_section');
        const addSectionButton = $(`#${add_section_button}`);
        const sectionInput = $(`#${custom_new_section}`);

        const sectionTemplate = `
            <div data-section="{section}">
                <h4>
                    <a data-bs-toggle="collapse" href="#{section}" role="button" aria-expanded="true"
                    aria-controls="{section}">{section}</a>
                    <i data-remove-section="{section}" class="bi bi-x-square float-end remove-disabled-section"></i>
                </h4>
                <hr>
                <div class="collapse show" id="{section}">
                    <div class="mb-3">
                        <div class="row mb-3">
                            <label class="col-sm-2 col-form-label" for="{section}_custom_new_option">New option name</label>
                            <div class="col-sm-8">
                                <div class="mb-3 form-group">
                                    <input placeholder="Option name for section '{section}'" class="form-control" id="{section}_custom_new_option" name="{section}_custom_new_option" type="text" value="">
                                </div>
                            </div>
                            <div class="col-sm-2">
                                <button type="button" class="btn btn-secondary input_button">Add input</button>
                                <button type="button" class="btn btn-secondary checkbox_button">Add checkbox</button>
                            </div>
                        </div>
                    </div>
                </div>
                <hr>               
            </div>
        `;
        addSectionButton.click(()=>{
            let _section= sectionInput.val();
            if (!(_section in customSections) && sectionInput.val().trim() !== ''){
                customSections[_section] = [];
                newSection.before(sectionTemplate.replaceAll("{section}", _section));
                sectionInput.val('');
                addOption(_section);
                removeDisabledSection(_section);
            }
        })
    }

    const inputTemplate = `
            <div class="row mb-3">
                <div class="col-sm-2">
                    <i class="bi bi-x-square remove-option-disabled" data-remove-section="{section}" 
                    data-remove-option="{input_name}"></i>
                    <label class="col-form-label" for="{section}_{input_name}">{input_name}</label>
                </div>
                <div class="col-sm-10">              
                    <div class="mb-3 form-group">
                        <input placeholder="Value for '{input_name}" class="form-control custom_value" data-section="{section}" data-name="{input_name}"
                         id="{section}_{input_name}" name="{section}_{input_name}" type="text" value="">
                    </div>
                </div>
            </div>
        `;
        const checkboxTemplate = `
            <div class="row mb-3">
                <div class="col-sm-2">
                    <i class="bi bi-x-square remove-option-disabled" data-remove-section="{section}"
                     data-remove-option="{input_name}"></i>
                    <label class="col-form-label" for="{section}_{input_name}">{input_name}</label>
                </div>
                <div class="col-sm-10">
                    <div class="mb-3 form-group form-check form-switch">
                        <input class="form-check-input custom_value"
                         data-section="{section}" data-name="{input_name}"
                         id="{section}_{input_name}"
                         name="{section}_{input_name}" type="checkbox">
                    </div>
                </div>
            </div>
        `;

    // This function add the event to the input_button and checkbox_button to add a new option.
    const addOption = (section_name) => {
        let _section = $(`#${section_name}`);

        // Add input type text
        $(_section).find('.input_button').click((element)=>{
            let _input_name = $(`#${section_name}_custom_new_option`).val();

            if (!(customSections[section_name].includes(_input_name)) && _input_name.trim() !== ''){
                customSections[section_name].push(_input_name);

                // Select the form and append the new input
                let _form = $(element.target).parent().parent().parent();
                $(_form).before(
                    inputTemplate.replaceAll('{section}', section_name)
                        .replaceAll('{input_name}', _input_name)
                );
                $(`#${section_name}_custom_new_option`).val('');
                // Add the remove event to the new option.
                removeDisabledOption(section_name);
            }
        });

        // Add input type checkbox
        $(_section).find('.checkbox_button').click((element)=>{
            let _input_name = $(`#${section_name}_custom_new_option`).val();

            if (!(customSections[section_name].includes(_input_name)) && _input_name.trim() !== ''){
                customSections[section_name].push(_input_name);

                // Select the form and append the new input
                let _form = $(element.target).parent().parent().parent();
                $(_form).before(
                    checkboxTemplate.replaceAll('{section}', section_name)
                        .replaceAll('{input_name}', _input_name)
                );
                $(`#${section_name}_custom_new_option`).val('');
                // Add the remove event to the new option.
                removeDisabledOption(section_name);
            }

        });
    }

    // This function is used to mark a section for removal.
    const removeSection = (section_name) => {
        $(`i.remove-section[data-remove-section="${section_name}"]`).click((element)=>{
            $(`a[aria-controls="${section_name}"]`)
                .toggleClass('text-decoration-line-through')
                .toggleClass('to-remove-section');
        });
    }

    // This function is used to mark an option for removal.
    const removeOption = (section_name) => {
        $(`i.remove-option[data-remove-section="${section_name}"]`).click((element)=> {
            $(element.currentTarget).toggleClass('to-remove-option');
            $(element.currentTarget).parent().find('label')
                .toggleClass('text-decoration-line-through');
        });
    }

    // This function is only used for NEW options.
    const removeDisabledOption = (section_name) => {
        $(`i.remove-option-disabled[data-remove-section="${section_name}"]`).click((element) => {
            let _option_to_delete = $(element.currentTarget).attr('data-remove-option');
            customSections[section_name].splice(customSections[section_name].indexOf(_option_to_delete), 1);
            $(element.currentTarget).parent().parent().remove();
        });
    }

    // This function is only used for NEW sections
    const removeDisabledSection = (section_name) => {
        $(`i.remove-disabled-section[data-remove-section="${section_name}"]`).click((element) => {
            delete customSections[section_name]
            $(element.currentTarget).parent().parent().remove();
        });
    }

    // forEach every initial section and add the click events to add options, remove sections and options.
    $(sections).each((element)=>{
        let _element = sections[element];
        let _section = $(_element).attr('aria-controls');
        customSections[_section] = [];
        addOption(_section);
        removeSection(_section);
        removeOption(_section);
    })

    // Initialize the click event for the add_section_button.
    addSection('custom_new_section', 'add_section_button');

    // When submit form.
    $(".settings_form").on('submit', (event)=>{
        event.preventDefault();

        // Get all the data for new custom options and sections
        let custom_sections_options_values = {};
        let all_custom_inputs = $('input.custom_value');
        $(all_custom_inputs).each((input) => {
            let _input = $(all_custom_inputs[input]);
            let _section = $(_input).attr('data-section');
            let _name = $(_input).attr('data-name');
            if (!(_section in custom_sections_options_values)){
                custom_sections_options_values[_section] = {}
            }
            let _value = $(_input).val();
            if ($(_input).attr('type') === 'checkbox'){
                if ($(_input).prop('checked')){
                    _value = "true"
                }else{
                    _value = "false"
                }
            }
            custom_sections_options_values[_section][_name] = _value;
        });

        // Get the data for possible remove of sections

        let to_remove_sections = $('.to-remove-section');
        $(to_remove_sections).each((link)=>{
            let section_name = $(to_remove_sections[link]).attr('aria-controls');
            removeSections[section_name] = [];
        });

        // Get the data for possible remove of options

        let to_remove_options = $('.to-remove-option');
        $(to_remove_options).each((element)=>{
            let section_name = $(to_remove_options[element]).attr('data-remove-section');
            let option_name = $(to_remove_options[element]).attr('data-remove-option');
            if (!(section_name in removeSections)){
                removeSections[section_name] = [];
            }
            removeSections[section_name].push(option_name);
        });

        // Set the data in the hidden inputs

        $("#custom_sections_inputs").val(JSON.stringify(custom_sections_options_values));
        $("#remove_sections_inputs").val(JSON.stringify(removeSections));

        event.currentTarget.submit();
    });

})