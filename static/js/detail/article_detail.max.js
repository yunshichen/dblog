$(document).ready(function() {

    // 检查 标题, 分类 等信息是否设置
    check_init_article_info();

    // 点击左下方打开模态对话框
	$('#article_info_container').click(function(){
        $('#article_modal_container').modal('show');
	});

    // 绑定模态对话框保存按钮的事件
	$('#save_modal_button').click(check_when_save_modal);

    // 初始化ck editor
    init_ck_editor();

    // 点击右下方预览文章的按钮
    $('#preview_btn').click(do_preview_article);

    // 点击右下方保存文章的按钮
    $('#save_record_btn').click(do_save_article);

    // 退出编辑
    $('#close_record_btn').click(do_close_article_window);
});

function do_close_article_window(){
    if(confirm('请确保文章信息已经保存. 确实要关闭文章编辑窗口吗?')){
        window.close();
    }
}


function check_init_article_info(){
    var aid = $('#aid').val();
    if (aid == ''){
        // 新建
        global_show_message_in_span('article_info_title', false, '未填写标题');
        global_show_message_in_span('article_info_cat', false, '未选择分类');
        global_show_message_in_span('article_info_short_desc', false, '未填写简介');
    } else{
        update_article_info_when_has_value();
    }
}

function do_preview_article(){

    var aid = $('#aid').val();
    if (aid == ''){
        global_show_message_in_span('article_info_title', false, '无法预览,请先保存文章');
        return;
    }

    var url = '/admin/article/preview?aid=' + aid;
    window.open(url);
}

function update_article_info_when_has_value(){

    var title = $.trim($('#title').val());
    var cat_label = $("#cat_id").find("option:selected").text();

    global_show_message_in_span('article_info_title', true, title);
    global_show_message_in_span('article_info_cat', true, cat_label);
    global_show_message_in_span('article_info_short_desc', true, '简介已填写');
}

function init_ck_editor(){

    //alert('init_ck_editor');

    CKEDITOR.replace('article_content');

    CKEDITOR.config.mathJaxLib = '//cdn.mathjax.org/mathjax/2.6-latest/MathJax.js?config=TeX-AMS_HTML';
    CKEDITOR.config.extraPlugins = 'uploadimage';
    CKEDITOR.config.imageUploadUrl = '/admin/ajax/ckeditor/upload_image';
//    CKEDITOR.config.height = '600px';
//    CKEDITOR.config.width = '800px';
    CKEDITOR.config.height = '85vh';

	// file browser 方式上传的配置
	CKEDITOR.config.image_previewText = '';
	CKEDITOR.config.filebrowserUploadUrl= '/admin/ajax/ckeditor/upload_image';


    CKEDITOR.on('instanceReady', function(e) {
        // 设置背景色
        var editor_bg_color = '#FCFCFC';
        // First time
        e.editor.document.getBody().setStyle('background-color', editor_bg_color);
        // in case the user switches to source and back
        e.editor.on('contentDom', function() {
            e.editor.document.getBody().setStyle('background-color', editor_bg_color);
        });

        // 获取内容
        var aid = $('#aid').val();
        if(aid == ''){
            return;
        }

        var url = '/admin/ajax/article/get_content';

        // 这里不能用 $.diego.fn.do_ajax 方法, 因为它会把结果转成json
    	$.ajax({
    		url : url,
    		type : 'get',
    		data : {'aid': aid},
    		success : function(server_data, textStatus, jqXHR) {

                //alert(server_data);
                CKEDITOR.instances.article_content.setData(server_data);
    		},
    		error : function() {
    		    // fixme FUTURE
    		    //alert('获取文章内容失败');
    		}
    	});

    });

}

function do_save_article(){

    var error_msg = check_article_info();
    if( error_msg != ''){
        global_show_message_in_span('show_save_article_info', false, error_msg);
        return;
    }

    var content = CKEDITOR.instances.article_content.getData();   //CKEDITOR.instances.控件ID.getData();
    if(content == ''){
        global_show_message_in_span('show_save_article_info', false, '请输入文章内容');
        return;
    }

    var title = $.trim($('#title').val());
    var cat_id = $('#cat_id').val();
    var column_id = $('#column_id').val();
    var short_desc = $.trim($('#short_desc').val());
    var status = $('#status').val();
    var aid = $('#aid').val();

    var url = '/admin/ajax/article/save';
    var params = {
        'aid': aid,
        'title': title,
        'cat_id': cat_id,
        'column_id': column_id,
        'short_desc': short_desc,
        'status': status,
        'content': content
    }

    global_do_ajax(url, params, function (response_data){

        if( global_check_session_expire(response_data)){
            return;
        }
        if(response_data.error){
            global_show_message_in_span('show_save_article_info', false, response_data.error);
            return;
        }

        // 重要. 如果不设置, 那按一次按钮就创建一条记录
        $('#aid').val(response_data.data);
        global_show_message_in_span('show_save_article_info', true,
            '已保存于: ' + global_format_now_to_hhmm() );
    });
}


function check_when_save_modal(){

    var error_msg = check_article_info();
    if( error_msg != ''){
        global_show_message_in_span('show_save_modal_info', false, error_msg);
        return;
    }

    // 一切正常
    $('#show_save_modal_info').html('');
    $('#article_modal_container').modal('hide');
    update_article_info_when_has_value();
}

function check_article_info(){

    var title = $.trim($('#title').val());
    var cat_id = $('#cat_id').val();
    var short_desc = $.trim($('#short_desc').val());

    if(title == ''){
        return '请填写标题';
    }

    if(short_desc == ''){
        return '请填写简介';
    }

    if(cat_id == ''){
        return '请选择分类';
    }

    return '';
}
