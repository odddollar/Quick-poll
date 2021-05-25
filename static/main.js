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
        // create field container div
        var field_container = document.createElement("div")
        field_container.className = "field";

        // create label element and set attributes
        var label = document.createElement("label");
        label.className = "label";
        label.htmlFor = `option${i}`;
        label.innerHTML = `Option ${i}\n`;
        field_container.appendChild(label);

        // create control div
        var control = document.createElement("div");
        control.className = "control";
        field_container.appendChild(control);

        // create input and append as child to control div
        var input = document.createElement("input");
        input.className = "home-input input is-primary";
        input.id = `option${i}`;
        input.type = "text";
        input.name = `option${i}`;
        if (i == 1 || i == 2) {
            input.placeholder = i == 1 ? "e.g. Good" : "e.g. Bad";
        }
        input.required = true;
        control.appendChild(input);

        // append field container div to container div
        container.appendChild(field_container);
    }
}
