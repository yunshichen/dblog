$(document).ready(function() {

	$('#go_add_new_article').click(create_new_article);

	$('#cat_select').change(research_data_list);

	$('#make_static_blog').click(make_static_blog);

    init_data_table();
});

function make_static_blog(){

    var url = '/admin/ajax/make_static';
    var params = {};

    global_do_ajax(url, params, function (server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        global_toast_info_bottom_right(true, '静态化成功');
    });
}


function create_new_article(){

    var url = '/admin/article/detail';
    window.open(url);

}

// 选择分类的时候, 查询相关文章
function research_data_list(){
    var cat_id = $('#cat_select').val();
    //alert('value is: ' + value);
    g_page.set_params({
        cat_id: cat_id
    });

	g_page.search_with_current_page_no(1);
}


function init_data_table(){

    g_page = new DPager({
        'container_id': 'page_div'
        , 'url': '/admin/ajax/article/page'
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

			html += "<td>" + dto.title + "</td>";
			html += "<td>" + dto.cat_label + "</td>";
			if(dto.status == 'Y'){
			    html += "<td><font color='green'>公开</font></td>";
			}
			else{
			    html += "<td><font color='#7C2900'>草稿</font></td>";
			}
			html += "<td>" + dto.create_time + "</td>";

            sep_html = '&nbsp;&nbsp;&nbsp;&nbsp;';
			html += "<td>";
			html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_preview_article(\"" + dto.id + "\");'>预览</a>";
			html += sep_html;
			html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_edit_record(\"" + dto.id + "\");'>编辑</a>";
			html += sep_html;
			html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_set_status(\"" + dto.id + "\");'>设置公开</a>";
			html += sep_html;
			html += "<a style='cursor:pointer;' href='javascript:void(0);' onclick='do_delete_record(\"" + dto.id + "\");'>删除</a>";
			html += "</td>";
		}

		$('#table_body').html(html);
	}

	g_page.search_with_current_page_no(1);

}

function do_edit_record(aid){

    var url = '/admin/article/detail?aid=' + aid;
    window.open(url);

}

function do_preview_article(aid){

    var url = '/admin/article/preview?aid=' + aid;
    window.open(url);

}

function do_delete_record(aid){

    var url = '/admin/ajax/article/delete';
    var data = {'aid': aid};

    _article_do_ajax(url, data, '博客已删除');

}

function do_set_status(aid){

    var url = '/admin/ajax/article/toggle_status';
    var data = {'aid': aid};

    _article_do_ajax(url, data, '设置成功');

}

function _article_do_ajax(url, data, msg){

    global_do_ajax(url, data, function(server_data){

        if( global_check_session_expire(server_data)){
            return;
        }

        if(server_data.error){
            global_toast_info_bottom_right(false, server_data.error);
            return;
        }

        global_toast_info_bottom_right(true, msg);

        g_page.search_with_current_page_no(1);

    });
}