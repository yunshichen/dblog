/**

    bootstrap 风格的分页条,允许简单的定制.
    注意: boostrap 的分页条必须用 pager 样式, 用其他样式会导致对齐问题.

    关键参数:

    json_result : 表示 response data,包含:
    {
        page_no: 当前页,如第1页, 第7页
        page_count: 页数大小
        page_size: 每页显示多少记录, 如10条
        total_count: 总记录数
        data_list: 数组 data_list

    }

**/

function math_divide(exp1, exp2) {
    var n1 = Math.round(exp1); //四舍五入
    var n2 = Math.round(exp2); //四舍五入

    var rslt = n1 / n2; //除

    if (rslt >= 0) {
        rslt = Math.floor(rslt); //返回小于等于原rslt的最大整数。
    }
    else {
        rslt = Math.ceil(rslt); //返回大于等于原rslt的最小整数。
    }

    return rslt;
}

var DPager = function(config){
    this.container_id = config.container_id;

    this.url = config.url;
    this.async = (!config.async) ? false: config.async;
    this.current_page_no = 1;
    
    // session 过期的处理
    this.handle_session_expire = function(server_data){
        return false;
    }
    if(config.handle_session_expire){
        this.handle_session_expire = config.handle_session_expire;
    }
    
    //python version
    this.json_result = {
        page_size: 10
        ,page_no: 1
        ,page_count: 1
        ,total_count: 0
        ,data_list: []
    }

    this.params = config.params;

}

/**
    发起 ajax请求,并得到返回数据
**/
DPager.prototype.do_ajax_call = function(page_no){
    var o_this = this;
    o_this.current_page_no = page_no;

    var data = this.params || {};
    data.page_no = page_no;

    $.ajax({
        url: o_this.url
        ,method: 'POST'
        ,async: o_this.async
        ,data: data
        ,success: function(server_data){
        	
        	// 处理session过期
        	if(o_this.handle_session_expire(server_data)){
        		return;
        	}
            o_this.on_ajax_success(o_this, server_data)
        }
    });
}

DPager.prototype.get_json_result = function(){
    return this.json_result;
}

DPager.prototype.search_with_current_page_no = function(page_no){
    var o_this = this;
    o_this.on_before_search(o_this);
    o_this.do_ajax_call(page_no);
    o_this.on_after_search(o_this);
}

//callback
DPager.prototype.on_before_search = function(o_pager){
    //do nothing
}

DPager.prototype.on_ajax_success = function(o_this, server_data){
	
	var json_result = null;
	if(typeof server_data === 'object'){
    	json_result = server_data.data;
    } else {
    	json_result = $.parseJSON(server_data).data;
    }
	//var json_result = $.parseJSON(server_data).data.data;

    //fixme 加上检查方法. json_result 的结构必须和服务器端参数一致
    o_this.json_result = json_result;

    o_this.render(o_this.current_page_no);
}
DPager.prototype.on_after_search = function(o_pager){
    //do nothing
}

// 设置额外的查询参数
DPager.prototype.set_params = function(a_params){
    var params = this.params || {};
    for( var mykey in a_params){
        params[mykey] = a_params[mykey];
    }
    this.params = params;
}

DPager.prototype.render = function(current_page_no){
    var json_result = this.json_result;
    //python version
    var total_count = json_result.total_count;
    var page_size = json_result.page_size;
    var page_count = json_result.page_count;

    //java version
//    var total_count = json_result.totalCount;
//    var page_size = json_result.pageSize;
//    var page_count = json_result.pageCount;

    var o_con = $("#"+this.container_id);

    var shtml = "";

    //记录数仅一页的情况,不需要显示分页条
    if (page_count == 1){
        shtml = "<div class='page-con info'>共有 " + total_count + " 条记录</div>";
        o_con.html(shtml);
        return;
    }

    // 计算起点页码
    var marker_size = 10;   //分页页码, 现在是 10个. ( 1,2,3,4,5,6,7,8,9,10 )
    var start = 0;
    var end = 0;
    
    if(page_count <= marker_size){
    	start = 1;
    	end = page_count;
    }else{
    	if(current_page_no <= marker_size){
    		start = 1;
    		end = marker_size;
    	}else{
    		// 举个列子, 12页的起始页码是 11 ,  33页的起始页码是 31, 即 x * 10 + 1
    		start = math_divide(current_page_no, marker_size) * marker_size + 1;
    		if( page_count - current_page_no >= marker_size ){
    			end = start + marker_size -1 ;
    		}else{
    			end = page_count;
    		}
    	}
    }
    
    // 计算是否需要显示前一页, 后一页
    var has_prev = false;
    var has_next = false;
    
    if(start > marker_size){
    	has_prev = true;
    }
    if(end < page_count){
    	has_next = true;
    }

	shtml = "<div class='page-con info'>记录数: " + total_count + ", 每页显示: " + page_size + "条, 当前显示 ";

	from = (current_page_no - 1)  * page_size + 1;
	to = from + page_size - 1;
	to = to <= total_count ? to : total_count;

	shtml += from + " 至 " + to + " 条 </div>";
	shtml += "<div class='page-con bar'><nav><ul class='pager'>";

	if ( has_prev){
		shtml += "<li><a href='javascript:void(0);' data-goto='" + (current_page_no - 10) + "'>前10页</a></li>";
	}


	for ( start; start <= end; start++){
		if ( start == current_page_no ){
			shtml += "<li><span style='background-color: #DDD;'><a href='javascript:void(0);'>" + start + "</a></span></li>";
			continue;
		}
		shtml += "<li><a href='javascript:void(0);' data-goto='" + start + "'>" + start + "</a></li>";

	}

	//只有不是第一排和最后一排,才需要 >> 和最后一页的按钮.
	if (  has_next ){
		var next = end + 1;
		shtml += "<li><a href='javascript:void(0);' data-goto='" + next + "'>后10页</a></li>";
	}

	shtml += "</ul></nav></div>"
	o_con.html(shtml);

	var me = this;
	o_con.find('a[data-goto]').click(function(){
		var pageNum = $(this).data('goto');
		me.search_with_current_page_no(pageNum);
	});

}
