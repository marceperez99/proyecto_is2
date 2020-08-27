
for (let counter = 0; counter < len; counter++) {

    let id;
    id = 'id_form-' + counter + '-modificar';
    let input = `input[id=${id}]`;
    $('#' + id).prop("checked",false)

    //Consigue los divs de asignacion
    let div_usuario = $('#div_id_form-' + counter + '-usuario' )
    let div_motivo = $('#div_id_form-' + counter + '-motivo' )
    let div_parent = div_motivo.parent()


    div_usuario.remove()
    div_motivo.remove()

    $(input).change(function () {
        if ($(this).is(':checked')) {
            div_parent.append(div_usuario)
            div_parent.append(div_motivo)
            $('#id_form-' + counter + '-usuario').attr('required',true)
            $('#id_form-' + counter + '-motivo').attr('required',true)

            // Checkbox is checked..
        } else {
             div_usuario.remove()
            div_motivo.remove()
            // console.log(input + 'unchecked')
            // Checkbox is not checked..
        }
    });
}