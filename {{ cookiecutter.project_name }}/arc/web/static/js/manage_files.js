
function submitEditForm(path){
    let input_path = document.getElementById("path_to_edit")
    let input_back_page = document.getElementById("page_to_back")
    let form_edit = document.getElementById("edit_form")
    input_path.value = path
    input_back_page.value = "/view_data"
    form_edit.submit();
}

function showFolder(folder_id){
    let folder = document.getElementById("content_"+folder_id)
    let elements = content_page.childNodes
    for(const element in elements){
        if(elements[element].nodeName === "DIV"){
            elements[element].style.display = "none";
        }
    }
    folder.style.display = "flex";
}
createFolders()
function createFolders(){
    addFolders(environments, root_name, [root_name], root_name)
    showFolder(root_name)
}


function addFolders(data, id, routes, title){
    let div_folder = document.createElement("div")
    div_folder.className = "folder-content row"
    div_folder.id = `content_${id}`
    div_folder.style.display = "none"

    let title_text = document.createElement("span")
    title_text.innerText = title
    title_text.className = "fs-5"

    let hr = document.createElement("hr")
    let div_navigation = document.createElement("div")
    let div_links = document.createElement("div")
    for(const current_folder in routes){
        let link = document.createElement("a")
        link.innerText = routes[current_folder]
        link.href = "#"
        link.className = "link-primary"
        link.setAttribute("onclick", `showFolder('${routes[current_folder]}')`)
        let separator = document.createElement("span")
        separator.innerText = " / "
        div_links.appendChild(link)
        div_links.appendChild(separator)
    }
    div_navigation.appendChild(div_links)
    div_navigation.appendChild(hr)
    div_navigation.appendChild(title_text)
    div_folder.appendChild(div_navigation)

    let table = document.createElement("table")
    table.id = "content-table"
    table.className = "table table-hover"
    div_folder.appendChild(table)
    let tr = document.createElement("tr")
    let th_name = document.createElement("th")
    let th_type = document.createElement("th")
    let th_action = document.createElement("th")
    th_name.scope = "col"
    th_type.scope = "col"
    th_action.scope = "col"
    th_name.innerText = "Name"
    th_type.innerText = "Type"
    th_action.innerText = "Actions"
    let table_heads = document.createElement("thead")
    tr.appendChild(th_name)
    tr.appendChild(th_type)
    tr.appendChild(th_action)
    table_heads.appendChild(tr)
    table.appendChild(table_heads)

    let table_content = document.createElement("tbody")
    table.appendChild(table_content)

    for(const file in data){
        if(data[file]["extension"] === "folder"){
            let folder_name = file
            routes.push(file)
            addFolders(data[file]["content"], file, routes, file)
            routes.pop()
            table_content.appendChild(create_folder_row(folder_name, "Folder"))
        }else if(data[file]["extension"] === "json"){
            table_content.appendChild(create_row_file("bi-filetype-json", file, "JSON File", data[file]["path"]))
        }else if(data[file]["extension"] === "yaml"){
            table_content.appendChild(create_row_file("bi-filetype-yml", file, "YAML File", data[file]["path"]))
        }else if(data[file]["extension"] === "csv"){
            table_content.appendChild(create_row_file("bi-filetype-csv", file, "CSV File", data[file]["path"]))
        }else if(data[file]["extension"] === "feature"){
            table_content.appendChild(create_row_file("bi-file-earmark", file, "FEATURE File", data[file]["path"]))
        }else{
            table_content.appendChild(create_row_file_not_supported("bi-file-earmark", file, data[file]["extension"].toUpperCase()+" File", data[file]["path"]))
        }
    }
    content_page.appendChild(div_folder)
}

function create_row_file(icon, filename, type, path){
    let row = document.createElement("tr")
    let cell_filename = document.createElement("td")
    let cell_type = document.createElement("td")
    let cell_action = document.createElement("td")
    cell_filename.innerHTML = `<i class="bi ${icon} text-primary" style="font-size: 1.5rem;"></i>&nbsp;&nbsp;&nbsp;
                               <span class="text-secondary fs-6">${filename}</span>`
    cell_type.innerText = type
    cell_action.innerHTML = `<button class="btn btn-outline-primary" onclick='submitEditForm("${path}")')>
                             <i class="bi bi-pencil-square"></i></button>`
    row.appendChild(cell_filename)
    row.appendChild(cell_type)
    row.appendChild(cell_action)
    return row
}

function create_row_file_not_supported(icon, filename, type, path){
    let row = document.createElement("tr")
    let cell_filename = document.createElement("td")
    let cell_type = document.createElement("td")
    let cell_action = document.createElement("td")
    cell_filename.innerHTML = `<i class="bi ${icon} text-primary" style="font-size: 1.5rem;"></i>&nbsp;&nbsp;&nbsp;
                               <span class="text-secondary fs-6">${filename}</span>`
    cell_type.innerText = type
    cell_action.innerHTML = `<span class="text-secondary">Not supported File</span>`
    row.appendChild(cell_filename)
    row.appendChild(cell_type)
    row.appendChild(cell_action)
    return row
}

function create_folder_row(folder_name, type){
    let row = document.createElement("tr")
    row.setAttribute("onclick", `showFolder('${folder_name}')`)
    let cell_filename = document.createElement("td")
    let cell_type = document.createElement("td")
    let cell_action = document.createElement("td")
    cell_filename.innerHTML = `<i class="bi bi-folder text-primary" style="font-size: 1.5rem;"></i>&nbsp;&nbsp;&nbsp;
                               <span class="text-secondary fs-6">${folder_name}</span>`
    cell_type.innerText = type
    row.appendChild(cell_filename)
    row.appendChild(cell_type)
    row.appendChild(cell_action)
    return row
}
