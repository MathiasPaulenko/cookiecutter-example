let tags;
let selectedTags = []
let message_errors_span = $("#message_errors_group_name");
let message_errors = $("#message_errors");


function set_tags(_tags) {
    tags = _tags;
}

$(document).ready(()=>{
    $("#btnAddTag").click(()=>addTag());
    autocomplete(document.getElementById("tag_input"));
})

function autocomplete(inp) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    let currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < tags.length; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (tags[i].substr(0, val.length).toUpperCase() === val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + tags[i].substr(0, val.length) + "</strong>";
                b.innerHTML += tags[i].substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + tags[i] + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function (e) {
        let autoCompleteList = document.getElementById(this.id + "autocomplete-list");
        if (autoCompleteList){
            autoCompleteList = autoCompleteList.getElementsByTagName("div");
        }
        if (e.keyCode === 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(autoCompleteList);
        } else if (e.keyCode === 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(autoCompleteList);
        } else if (e.keyCode === 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (autoCompleteList) {
                  autoCompleteList[currentFocus].click();
                }
            }
        }
    });

    function addActive(autoCompleteList) {
        /*a function to classify an item as "active":*/
        if (!autoCompleteList) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(autoCompleteList);
        if (currentFocus >= autoCompleteList.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (autoCompleteList.length - 1);
        /*add class "autocomplete-active":*/
        autoCompleteList[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(autoCompleteList) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (const element of autoCompleteList) {
            element.classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        let autoCompleteList = document.getElementsByClassName("autocomplete-items");
        for (const element of autoCompleteList) {
            if (elmnt !== element && elmnt !== inp) {
                element.parentNode.removeChild(element);
            }
        }
    }
}

function addTag() {
    /*
    This function create a tag element and add to tags field with the info in the input text "Tag to run"
    */
    let input = $("#tag_input");
    let tags_field = $("#tags_added");
    if (input.val() !== "") {
        let tag = "" + input.val();
        if (!tags.includes(tag)) {
            //if the tag to add doesn't exist
            message_errors.text(`@${tag} does not exist in the database`);
        } else {
            //add tag element if exist in database
            message_errors.text("");
            if (!selectedTags.includes(tag)) {
                selectedTags.push(tag);
                let tags_text = `<span data-tag='${tag}' id='${tag}_tag' class="d-inline-block text-primary p-1">${tag}<button onclick="removeTag('${tag}_tag')" class="btn btn-sm border-0 btn-outline-danger pb-2 mx-1">x</button></span>`;
                tags_field.html(tags_field.html() + tags_text);
                input.val("");
            } else {
                //if the tag to add is already added inform and clean the input
                message_errors.text(`@${tag} already added to the queue`);
                input.val("");
            }
        }
    } else {
        //if the tag to add is empty
        message_errors.text(`add some @tag first`);
    }
}

function removeTag(id) {
    /*
    This function is used to remove a tag webElement in the tags field defined by the argument
    take 1 argument the id of the webElement
    */
    let element = $(`#${id}`);
    let tag = element.attr('data-tag');
    let tag_index = selectedTags.indexOf(tag)
    if (tag_index > -1){
        selectedTags.splice(tag_index, 1);
    }
    $(element).remove();
}