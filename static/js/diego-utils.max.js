// 点击头部菜单的时候触发
function global_click_header(index){
    var header_prefix = 'global_header_';
    headers = $("li[id^='global_header_']");
    $.each(headers, function( index, item ) {
      //alert( index + ": " + item );
      // 去掉li的active 样式
      $(item).removeClass('active')
    });

    $('#global_header_'+index).addClass('active')

    // 发起请求, 改变左侧菜单
    window.location.href = '/index?select_header_index=' + index;
}

// 点击左侧菜单的时候触发
function global_click_left(parent_index, child_index, child_link){
    //alert('parent_index: ' + parent_index + ', child_index: ' + child_index);
    var current_header = $("li[id^='global_header_'][class='active'");

    var header_index = current_header.attr('id').replace('global_header_', '');
    //alert('current_header.index: ' + header_index);

    var url = child_link +  '?select_header_index=' + header_index;
    url += '&select_parent_index=' + parent_index;
    url += '&select_child_index=' + child_index;
    window.location.href = url;
}

// 用于ajax 方法, 检查是否session 超时
function global_check_session_expire(server_data){

	if(typeof server_data === 'object'){
		// no need to do anything
    } else {
    	server_data = $.parseJSON(server_data);
    }
	if(server_data.session_expire == 'Y'){

		// 显示隐藏的模态对话框
		$('#show_login_error_in_modal').html('');
        $('#global_modal_login_div').modal('show');
		return true;
	}
	return false;
}

// 提交全局隐藏的登录form
function global_do_submit_modal_login_form(){

    var o_button = $(this);
    o_button.button('loading');

    global_do_ajax_submit_form('global_modal_login_form', {}, function(data){

        o_button.button('reset');

        if(data.error){
            global_show_message_in_span('show_login_error_in_modal', false, data.error);
            return;
        }

        $('#global_modal_login_div').modal('hide');
        //TODO use gitter to notify
    });
}


function global_show_message_in_span (id_or_element, succ, msg){

    var font = '<font color="red">';
    if(succ){
        font = '<font color="green">';
    }

    msg = font + msg + '</font>';
    if(id_or_element instanceof jQuery){
        $(id_or_element).html(msg);
    }
    else{
        $('#'+id_or_element).html(msg);

    }
}

function global_format_now_to_hhmm () {
    var datetime = new Date();
    //var month = datetime.getMonth() + 1 < 10 ? "0" + (datetime.getMonth() + 1) : datetime.getMonth() + 1;
    //var date = datetime.getDate() < 10 ? "0" + datetime.getDate() : datetime.getDate();
    var hour = datetime.getHours()< 10 ? "0" + datetime.getHours() : datetime.getHours();
    var minute = datetime.getMinutes()< 10 ? "0" + datetime.getMinutes() : datetime.getMinutes();
    var second = datetime.getSeconds()< 10 ? "0" + datetime.getSeconds() : datetime.getSeconds();
    return hour+":"+minute+":"+second;
}

	function gen_green_or_red_font (value, msg_pair){

		var color = 'green';
		if(value != 'Y'){
			value = 'N';	// 防止有时候value 是 空的情况
			color = 'red';
		}

		return "<font color='" + color + "'>" + msg_pair[value] + "</font>";

	}

    function on_file_upload_change (){
    	// 必须有全局对象

        var upload_url = g_image_uploader.upload_url;
		var upload_parameter = g_image_uploader.upload_parameter;
        var current_uploader = g_image_uploader.current_uploader;
		var show_m = current_uploader.show_upload_message;

		// 初始化上传框
        if (!window.FormData) {
            show_m("浏览器不支持 FormData 对象，请用 chrome 或 firefox浏览器来上传文件", false);
            return;
        }
        
        var firstFile = this.files[0];

        if( ! firstFile){
            return;
        }	        

        data = new FormData();
        data.append(upload_parameter, firstFile);
        	
        // ---- 发送图片数据到远程服务器
        show_m(current_uploader, '正在上传......', true);
        
        var fileObj = this.files;
        $.ajax({
            url: upload_url,
            type: "POST",
            data: data,
            processData: false,
            contentType: false,
            success: function(server_data) {
            	current_uploader.upload_handler(current_uploader, server_data);
            	//rebinding_file_change(g_image_uploader.file_obj, false);
            	
            },
            error : function() {
            	current_uploader.error_handler(current_uploader, server_data);
            	//rebinding_file_change(g_image_uploader.file_obj, false);
            },
        });
        
    }
    
    // ---------------------------------------
    function show_progress (s_title, s_text){

    	var title = '正在操作';
    	var text = '正在操作中,请稍候...';

    	if(s_title){
    		title = s_title;
    	}
    	if(s_text){
    		text = s_text;
    	}

//    	$.messager.progress({
//    		title : title,
//    		text : text,
//    		left : 400,
//    		top : document.body.scrollTop + document.documentElement.scrollTop
//    				+ 150,
//    	});
    }
    
    // ---------------------------------------

function global_do_ajax (url, data, fn) {

    if(!fn){
        fn = function(data, textStatus, jqXHR){};
    }

    var async = true;
    if (data.async && (data.async == false)) {
        async = false;
    }

    var method = "post";
    if(data.method == 'get'){
        method = "get";
    }

    $.ajax({
        url : url,
        type : method,
        data : data,
        success : function(server_data, textStatus, jqXHR) {
//    			$.messager.progress('close');
            if(typeof server_data != 'object'){
                server_data = $.parseJSON(server_data);
            }
            fn(server_data, textStatus, jqXHR);
        },
        error : function() {
//    			$.messager.progress('close');
        },
        async : async
    });
}
    
    // ---------------------------

 // 将form中的值转换为键值对。
function global_get_form_json  (frm) {
    var o = {};
    var a = $(frm).serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [ o[this.name] ];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });

    return o;
 }
    
// --------------------------
function global_do_ajax_submit_form (formid, data, fn) {

    frm = $("#" + formid);
    var dataPara = global_get_form_json(frm);

    var async = true;
    var url = frm.attr("action");
    if (data) {
        if (data.async) {
            async = false;
        }

        for (key in data) {
            if (key == 'async' || key == 'url') {
                continue;
            }
            dataPara[key] = data[key];
        }
        url = url || data.url;
    }

//    	show_progress();

    $.ajax({
        url : url,
        type : method = frm.attr("method"),
        data : dataPara,
        success : function(data, textStatus, jqXHR) {
//    			$.messager.progress('close');
            fn(data, textStatus, jqXHR);
        },
        error : function() {
//    			$.messager.progress('close');
        },
        async : async
    });
}
    
    // --------------------------
function global_toast_info_bottom_right (succ, msg){

    $.extend($.gritter.options, {
        position: 'bottom-right',// possibilities: bottom-left, bottom-right, top-left, top-right
    });

    var title = '操作错误';
    var icon_name = 'im-angry';
    var class_name = 'error-notice';

    if(succ){
        title = '操作成功';
        var icon_name = 'im-grin';
        var class_name = 'gritter-success';

    }

    $.gritter.add({
        // (string | mandatory) the heading of the notification
        title: title,
        // (string | mandatory) the text inside the notification
        text: msg,
        // (int | optional) the time you want it to be alive for before fading out
        time: '',
        // (string) specify font-face icon  class for close message
        close_icon: 'en-cross',
        // (string) specify font-face icon class for big icon in left. if are specify image this will not show up.
        icon: icon_name,
        // (string | optional) the class name you want to apply to that specific message
        class_name: class_name
    });

}
