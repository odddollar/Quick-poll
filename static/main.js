function set_select_default() {
    // on page load set select to 2
    var select = document.getElementById("options");
    select.value = "2";
}

function change_input_fields() {
    // get number of options from dropdown
    var value = document.getElementById("options").value;

    // get parent container of options div and remove child nodes
    var container = document.getElementById("option-list")
    while (container.hasChildNodes()) {
        container.removeChild(container.lastChild);
    }

    // add necessary number of options
    for (var i = 1; i <= value; i++) {
        // create label element and set text
        var label = document.createElement("label");
        label.innerHTML = `Option ${i}\n`;

        // create input element and append to label
        var input = document.createElement("input");
        input.type = "text";
        input.name = `option${i}`;
        input.required = true;
        label.appendChild(input);

        // append label to container div
        container.appendChild(label);
        container.appendChild(document.createElement("br"))
    }
}
