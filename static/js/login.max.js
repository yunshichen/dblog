
$(function() {
    $("#login_btn").click(function(){

        global_do_ajax_submit_form('login_form', {}, function(data){

            if(data.error){
                global_show_message_in_span('error_span', false, data.error);
            }else{
                window.location.href = "/admin";
            }
        });

    });

//    $(document).keyup(function(event){
//      if(event.keyCode ==13){
//        $("#login_btn").trigger("click");
//      }
//    });

});