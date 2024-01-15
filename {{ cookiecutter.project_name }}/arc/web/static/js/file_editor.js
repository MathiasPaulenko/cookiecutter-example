/*
    This file contains all the code for edit features
*/
//prepare the editor
require('ace/ext/language_tools');
let editor = ace.edit("editor")
editor.setTheme("ace/theme/monokai")
editor.session.setMode("ace/mode/"+type_file)
editor.resize()
let completions = []
let simple_steps = []
let steps_with_descriptions = []

// set codeEditor
 function activateEditor(){
    //set options editor and set autocompletion
    if (type_file === "gherkin"){
        completions = [
            {value: 'Feature:', score: 1, meta: 'Initial Word to start a gherkin file'},
            {value: 'Scenario:', score: 2, meta: 'Initial Word to start simple scenario'},
            {value: 'Scenario Outline:\n\n\tExamples:\n\t\t| header |\n\t\t| value  |', score: 7, meta: 'Scenario Outline autocreate'},
            {value: 'Given', score: 3, meta: 'Step word to initiate a step definition, Given is used as a initial Word to Scenarios'},
            {value: 'When', score: 4, meta: 'Step initial word'},
            {value: 'Then', score: 5, meta: 'Step initial word'},
            {value: 'And', score: 6, meta: 'Step initial word'},
            {value: 'Examples:\n\t| header |\n\t| value  |', score: 7, meta: 'Examples for Outline Scenarios'},
          ]
        //set steps for completions and search steps
        let starts_score = 1
        for(const file in steps){
            for (const step in steps[file]){
                let step_completion_info = {value: steps[file][step]['step-definition'], score: starts_score, meta: "Step Definition"}
                completions.push(step_completion_info)
                simple_steps.push(steps[file][step]['step-definition'])
                let step_info = {"Definition":String(steps[file][step]['step-definition']),"Description":String(steps[file][step]['description'])}
                steps_with_descriptions.push(step_info)
            }
        }
        //set options editor and set autocompletion
        editor.setOptions({
          enableBasicAutocompletion: [{
            getCompletions: (editor, session, pos, prefix, callback) => {
              // note, won't fire if caret is at a word that does not have these letters
              callback(null, completions);
            },
          }],
          // to make popup appear automatically, without explicit _ctrl+space_
          enableLiveAutocompletion: true,
          autoScrollEditorIntoView: true,
          copyWithEmptySelection: true,
          enableSnippets: true,
          maxLines: Infinity,
          minLines: 50,
        });
    }
    else{
        editor.setOptions({
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          autoScrollEditorIntoView: true,
          copyWithEmptySelection: true,
          enableSnippets: true,
          maxLines: Infinity,
          minLines: 50,
        });
    }

    for(const index in file_lines){
      let line = file_lines[index]
      line = line.replace("\n","")
      file_lines[index] = line
   }
   let gherkin_code = ace.createEditSession(file_lines)
   editor.setSession(gherkin_code)
   editor.session.setMode("ace/mode/"+type_file);
   editor.session.setUseSoftTabs(true);
   editor.session.setTabSize(2);
   editor.session.setUseWrapMode(true);
   editor.setShowPrintMargin(false);
   document.getElementById('editor').style.fontSize='14px';
 }
 // call method to set the code from the feature
 if (file_lines !== undefined){
    activateEditor();
 }

// show alert animation
 function showAlert(id_alert) {
  let id = null;
  const elem = document.getElementById(id_alert);
  let pos = -300;
  clearInterval(id_alert);
  id = setInterval(showAlert, 5);
  function showAlert() {
    if (pos === 20) {
      clearInterval(id);
      setTimeout(function() {
        id = setInterval(backAlert, 5);
      }, 3000);
    } else {
      pos += 5;
      elem.style.right = pos + "px";
    }
  }
  function backAlert() {
    if (pos === -300) {
      clearInterval(id);
    } else {
      pos -= 5;
      elem.style.right = pos + "px";
    }
  }
}

// event to save the file when the form with id "save_form" is submitted
$(document).on('submit','#save_form',function(e){
  e.preventDefault();
  $.ajax({
    type:'POST',
    url:'/save_file',
    data:{
      csrf_token:$("#csrf_token").val(),
      file_content:$("#file_content").val(),
      path:$("#path").val()
    },
    success:function()
    {
      showAlert("animated_alert_success");
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      showAlert("animated_alert_error");
    }
  })
});

//set parameters to save the feature and sends the save form
function sendForm(){
    let form_save = document.getElementById("save_form")
    let input_content = document.getElementById("file_content")
    let input_path = document.getElementById("path")
    let btn_submit = document.getElementById("submit_form_button")
    let lines = editor.getSession().getDocument().getAllLines();
    let txt = '';
    for(const element of lines) {
        if (txt !== '') {
            txt += '\\n';
        }
        txt += element;
    }
    input_content.value = txt
    input_path.value = file_path_js
    btn_submit.click();
}

//  ******************* edit features methods ****************

//Shows the search step panel
function showSearchBar() {
  let id = null;
  const elem = document.getElementById("search-steps");
  const btn = document.getElementById("button_search_step");
  btn.style.display = "none";
  let pos = -600;
  clearInterval(id);
  id = setInterval(showAlert, 5);
  function showAlert() {
    if (pos === 30) {
      clearInterval(id);
    } else {
      pos += 10;
      elem.style.right = pos + "px";
    }
  }
 }

//hide the search step panel
 function hideSearchBar() {
  let id = null;
  const elem = document.getElementById("search-steps");
  const btn = document.getElementById("button_search_step");
  let pos = 30;
  clearInterval(id);
  id = setInterval(showAlert, 5);
  btn.style.display = "block";
  function showAlert() {
    if (pos === -600) {
      clearInterval(id);
    } else {
      pos -= 10;
      elem.style.right = pos + "px";
    }
  }
 }

 // Inserts a step in to the editor
 function insert_step(){
     let coord = editor.selection.getCursor();
    let desc_input = document.getElementById("search_step_description_input")
    let step_input = document.getElementById("search_step_input")
    let btn_insert = document.getElementById("btn_insert_step")
    editor.session.insert({row: coord.row, column:coord.column}, step_input.value+"\n")
    step_input.value = ""
    desc_input.value = ""
    btn_insert.disabled = true
    editor.gotoLine((coord.row)+2)
    editor.focus();
 }

 // Code to show the steps and descriptions in the search step panel
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  let currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      let a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() === val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += `<input type="hidden" value="${arr[i]}">`;
          b.innerHTML += `<input type="hidden" value="${i}">`;
          /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              let desc_input = document.getElementById("search_step_description_input")
              let btn_insert = document.getElementById("btn_insert_step")
              desc_input.value = steps_with_descriptions[this.getElementsByTagName("input")[1].value]['Description']
              btn_insert.disabled = false
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode === 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode === 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode === 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (const element of x) {
        element.classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
      let x = document.getElementsByClassName("autocomplete-items");
    for (const element of x) {
        if (elmnt !== element && elmnt !== inp) {
            element.parentNode.removeChild(element);
    }
  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}
// set autocomplete event to the input of search step panel.

if(type_file === "gherkin"){
    autocomplete(document.getElementById("search_step_input"), simple_steps);
}
