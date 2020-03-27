let contador_atr=1;

$("#atributos_dinamicos #atr_").each(function(){
    let elemento = $(this);
    let nro_atributo = contador_atr;
    elemento.attr("id","atr_"+contador_atr);
    $(".row a",elemento).click(event=>{
        event.preventDefault();
        $("#atr_"+nro_atributo).remove();
    });
    $("input[name=nombre]",elemento).attr("name","atr_"+nro_atributo+"_nombre");
    $("input[name=requerido]",elemento).attr("name","atr_"+nro_atributo+"_requerido");
    $("input[name=max_longitud]",elemento).attr("name","atr_"+nro_atributo+"_max_longitud");
    $("input[name=max_digitos]",elemento).attr("name","atr_"+nro_atributo+"_max_digitos");
    $("input[name=max_tamaño]",elemento).attr("name","atr_"+nro_atributo+"_max_tamaño");
    $("input[name=max_decimales]",elemento).attr("name","atr_"+nro_atributo+"_max_decimales");
    $("input[name=tipo]",elemento).attr("name","atr_"+nro_atributo+"_tipo");
    $("#cont_atr").attr("value",nro_atributo);
    contador_atr++;
});
function agregar_atributo() {
    let nro_atrib = contador_atr;
    let nuevo_atributo = $("<div>" +atributos[ $("#seleccionar_atr").val() ] +"</div>");
    nuevo_atributo.prepend(
        //Se agrega el titulo de la seccion
        $("<div class='row'></div>")
            .append($("<h5 class='col-11'>"+$("#seleccionar_atr option:selected").text()+"</h5>"))
            .append(
                //Se agrega el boton de eliminar tipo de item
                $("<a href='#' class='text-color-danger col-1'><i class='fas fa-trash-alt'></i></a><hr>")
                    .click(event=>{
                        event.preventDefault();
                        $("#atr_"+nro_atrib).remove();
                    })
            ));
    nuevo_atributo.attr("id","atr_"+nro_atrib).attr("class","col-10 mx-auto border rounded p-3 my-3");
    $("#atributos_dinamicos").append(nuevo_atributo);
    //Se cambian los nombres de los inputs
    $("#atr_"+nro_atrib+" input[name=nombre]").attr("name","atr_"+nro_atrib+"_nombre");
    $("#atr_"+nro_atrib+" input[name=requerido").attr("name","atr_"+nro_atrib+"_requerido");
    $("#atr_"+nro_atrib+" input[name=max_longitud").attr("name","atr_"+nro_atrib+"_max_longitud");
    $("#atr_"+nro_atrib+" input[name=max_digitos").attr("name","atr_"+nro_atrib+"_max_digitos");
    $("#atr_"+nro_atrib+" input[name=max_tamaño").attr("name","atr_"+nro_atrib+"_max_tamaño");
    $("#atr_"+nro_atrib+" input[name=max_decimales").attr("name","atr_"+nro_atrib+"_max_decimales");
    $("#atr_"+nro_atrib+" input[name=tipo]").attr("name","atr_"+nro_atrib+"_tipo");
    console.log($("#atr_"+nro_atrib+" input[name=max_decimales"));
    $("#cont_atr").attr("value",nro_atrib);
    contador_atr++;
}

function eliminar_atributo(id_atributo){
    $("#atributos_dinamicos atr_"+id_atributo).remove();
}