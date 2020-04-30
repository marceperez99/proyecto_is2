 function ocultar_items_eliminados() {
     $(".item_Eliminado").hide();
     $("#btn_mostrar_eliminados").show();
     $("#btn_ocultar_eliminados").hide();
 }
  function mostrar_items_eliminados() {
     $(".item_Eliminado").show();
     $("#btn_mostrar_eliminados").hide();
     $("#btn_ocultar_eliminados").show();
 }


 document.addEventListener('DOMContentLoaded', function() {
    $(".item_Eliminado").hide();
    $("#btn_ocultar_eliminados").hide();
    }, false);
