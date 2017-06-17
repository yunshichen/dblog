$(document).ready(function() {

    init_modal_form();

	$('#submit_modal_form').click(do_save_record);

	init_data_table();

});

function init_modal_form(){

	$('#open_data_modal_form').click(function(){
	    $('#data_modal_title').html('新增分类');
	    $('#aid').val('');
	    $('#label').val('');
	    $('#show_error_in_modal').html('');
        $('#data_modal_container').modal('show');
	});
}

function do_save_record(){

    var o_button = $(this);
    o_button.button('loading');
    global_do_ajax_submit_form("modal_form_save", '', function (server_data){
        o_button.button('reset');

        if( global_check_session_expire(server_data)){
            return;
        }
        if(server_data.error){
            global_show_message_in_span('show_error_in_modal', false, server_data.error);
            return;
        }

        $('#data_modal_container').modal('hide');
        g_page.search_with_current_page_no(1);

    });
}


function init_data_table(){

    var data_body = 'table_body';
    var page_bar = 'bottom_page_bar';


    g_page = new DPager({
        'container_id': page_bar
        , 'url': '/admin/ajax/cat/page'
        // , 'handle_session_expire': check_is_session_invalid	// check_is_session_invalid 来自于 share.max.js
    });

    g_page.on_after_search = function(g_page){

        var json_result = g_page.json_result;

        var data_list = json_result.data_list;
        var i=0;
        var html = "";
        for(i ; i < data_list.length; i++){
            var dto = data_list[i]

            if(i % 2 == 0){
                html += "<tr class='gradeX even'>";
            }else{
                html += "<tr class='gradeX odd'>";
            }

            html += "<td>" + dto.label + "</td>";

            sep_html = '&nbsp;&nbsp;&nbsp;&nbsp;';
            html += "<td>";
            html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_edit_record(\"" + dto.id + "\");'>编辑</a>";
            html += sep_html;
            html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_move_up_cat(\"" + dto.id + "\");'>上移</a>";
            html += sep_html;
            html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_move_down_cat(\"" + dto.id + "\");'>下移</a>";
            html += sep_html;
            html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_delete_cat(\"" + dto.id + "\");'>删除</a>";
            html += "</td>";
        }

        $('#' + data_body).html(html);
    }

    g_page.search_with_current_page_no(1);

}


function on_click_add_btn_cat(){

    var o_button = $(this);


    $('#title_cat').html('新增分类');     // 改变title 文字
    $('#save_id_cat').val('');          // 清空id
    $('#error_span_cat').html('');      // 清空错误区
    $('#label_cat').val('');            // 分类的值
}


function do_edit_record(aid){

    var url = '/admin/ajax/cat/get';
    var params = {'aid': aid};

    global_do_ajax(url, params, function(server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        var dto = server_data.data;

        $('#data_modal_title').html('修改分类');
        $('#aid').val(aid);
        $('#label').val(dto.label);
        $('#show_error_in_modal').html('');
        $('#data_modal_container').modal('show');

    });

}


function do_delete_cat(aid){

    var url = '/admin/ajax/cat/delete';

    var data = {
        'method': 'post',
        'aid': aid
    }

    global_do_ajax(url, data, function(server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        global_toast_info_bottom_right(true, '分类已删除');

        g_page.search_with_current_page_no(1);

    });

}


function do_move_down_cat(aid){

    var url = '/admin/ajax/cat/move_down';

    var data = {
        'method': 'post',
        'aid': aid
    }

    global_do_ajax(url, data, function(server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        global_toast_info_bottom_right(true, '下移成功');

        g_page.search_with_current_page_no(1);

    });

}


function do_move_up_cat(aid){

    var url = '/admin/ajax/cat/move_up';

    var data = {
        'method': 'post',
        'aid': aid
    }

    global_do_ajax(url, data, function(server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        global_toast_info_bottom_right(true, '上移成功');

        g_page.search_with_current_page_no(1);

    });

}