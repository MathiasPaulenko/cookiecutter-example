let features_data;

function set_features_data(_features_data) {
    features_data = _features_data;
}

let details_modal = $('#show_details');

details_modal.on('show.bs.modal', (event) => {
    // Event to prepares gherkin information to show in the modal
    // Button that triggered the modal
    let button = event.relatedTarget;
    // Extract info from data-bs-* attributes (get feature details clicked)
    let feature = button.getAttribute('data-bs-feature-file');
    // Update the modal's content.
    let modalTitle = details_modal.find('.modal-title');
    let modalBodyInput = details_modal.find('.modal-body');
    modalBodyInput.html('<div id="modalFeatureDetail"></div>')
    let feature_data = features_data[`${feature}`];
    //Define title of the modal
    modalTitle.text(`Show details of ${feature}`);
    let current = window.location.origin
    fetch(`${current}/utils/feature`, {
        method: 'POST',
        body: feature_data["filepath"]
    }).then(response => response.json())
        .then(text => {
            ace.edit("modalFeatureDetail", {
                mode: "ace/mode/gherkin",
                theme: "ace/theme/vibrant_ink",
                value: text,
                readOnly: true
            });
        })
})