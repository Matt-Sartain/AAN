function event_reorder_function(event){
	var v_widget_page = $(".widget_page").val();
	var v_update_data = new Array();
	for (x=1;x<=5;x++){
		var v_row_data = new Array();
		$("#holder"+x).children(".widget").each(function(z,widget){
			v_row_data[z] = $(widget).children(".widget_id").val();
		});
		v_update_data[x] = v_row_data.join("|");
	}
	$.ajax({
		type: "POST",
		url: "/api/ajax_sort_order/"+v_update_data+"/"+v_widget_page+"/",
		dataType: "json",
		async: 'false'
	});
}

function change_chart_styles(v_this){
	var v_widget_id = v_this.parent().parent().parent().parent().children(".widget_id").val();
	var v_widget_style = v_this.text();
	$.ajax({
		type: "POST",
		url: "/api/ajax_new_chart/"+v_widget_id+"/"+v_widget_style+"/",
		dataType: "json",
		async: false,
		success: function(data){
			current_widget = v_this.parent().parent().parent().parent();
			current_widget.children(".widget_header").text(data.header);
			current_widget.children(".widget_content").html(data.html);
			v_this.parent().parent().parent().parent().children('.widget_id').val(data.widget_id);
			v_this.parent().parent().parent().parent().children('.hidden_flash_content').val('<div style="width:100%;">'+data.html+'</div>');
			
			v_this.parent().parent().parent().parent().children('.widget_settings_content').children().children('.wid').val(data.widget_id);
			
		}
	});
}
function ActivateTheLazers(){
	$("#holder1,#holder3,#holder4,#holder5").sortable({
		handle:'.widget_headerCtn',
		connectWith: '.widget_holder', 
		placeholder: 'ui-state-highlight',
		update: function store_order(event){
			event_reorder_function(event);		
		}
	});
	$("#holder2").sortable({
		handle:'.widget_headerCtn',
		placeholder: 'ui-state-highlight',
		update: function store_order(event){
			event_reorder_function(event);		
		}
	});
	
	$("#id_start_date").each(function(){
		$(this).val($(this).parent().parent().parent().parent().siblings(".hidden_start_date").val());
	});
	$("#id_end_date").each(function(){
		$(this).val($(this).parent().parent().parent().parent().siblings(".hidden_end_date").val());
	})

	$(".chart_style_lines").live("click", function(event){
		event.preventDefault();
		change_chart_styles($(this));
		$(this).parent().parent().siblings('.widget_content').show();
		$(this).parent().parent().siblings('.widget_settings_content').hide();
		$(this).parent().parent().parent().prev().prev().children(".widget_table").dataTable({'bFilter':false,
                                                                     	                      'bJQueryUI': true,
                                                                                              'bLengthChange':false,
                                                                                              'bPaginate': true,
                                                                                              'iDisplayLength':25});
		/*
		decHtmlTable = $(this).parent().parent().parent().parent().html();
		decHtmlTable = decHtmlTable.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>');
        $(this).parent().parent().parent().parent().html(decHtmlTable);
	    alert($(this).parent().parent().parent().parent().parent().html());
        */
	});
	$(".widget_settings").live("click", function(event){
		event.preventDefault();
		$(this).parent().parent().parent().siblings('.widget_content').hide();
		$(this).parent().parent().parent().siblings('.widget_settings_content').show();
	});
	$(".lightbox_it").live("click", function(event){
		event.preventDefault();
		var v_this = $(this);
		$($(this).parent().parent().parent().siblings(".hidden_flash_content").val()).dialog({
			bgiframe: true,
			height: 400,
			width: '95%',
			modal: true,
			draggable: false,
			resizable: false
		});
		$(this).parent().parent().parent().siblings('.widget_content').show();
		$(this).parent().parent().parent().siblings('.widget_settings_content').hide();
	});
	$(".widget_collapse").live("click", function(event){
		event.preventDefault();
		var $actObj = $(this).parent().next();
		$actObj.hide();
		$actObj.siblings(".widget_settings_content").hide();
		$actObj.siblings(".widget_footer").hide();
		$(this).removeClass('widget_collapse');
		$(this).addClass('widget_collapsed');
	});
	$(".widget_collapsed").live("click", function(event){
		event.preventDefault();
		var $actObj = $(this).parent().next();
		$actObj.show();
		$actObj.siblings(".widget_footer").show();
		$(this).removeClass('widget_collapsed');
		$(this).addClass('widget_collapse');
	});
	$(".widget_close").live("click", function(event){
		event.preventDefault();
		var v_this = $(this);
		var v_widget_id = $(this).parent().parent().children(".widget_id").val();
		$.ajax({
			type: "POST",
			url: "/api/ajax_remove_widget/"+v_widget_id+"/",
			async: false,
			success: function(data){
				$(v_this).parent().parent().remove();
				event_reorder_function(event);
			}
		});
	});	
	var data_html = '';
	$("#widget_add").click(function(event){
		event.preventDefault();
		$("#widget_toolbar").dialog({bgiframe: true,	height: 400, width: 600, modal: true,draggable: false,resizable: false});
		$("#widget_toolbar").bind('dialogclose', function(event, ui) {
			$("#widget_toolbar").dialog("destroy");
		});	
		
    });
    $('.widget_selector').live("click", function(event){

		var v_widget_id = $(this).children(".widget_selector_id").val();
		var v_widget_page = $(".widget_page").val();
		
		$.ajax({
			type: "POST",
			url: "/api/ajax_add_widget/"+v_widget_id+"/"+v_widget_page+"/",
			dataType: "json",
			async: true,
			success: function(data){
				$("#holder1").prepend("<li class='widget'>"+$('.toolbar_widget:last').html()+"</li>");
				$("#holder1").children("li:first").children(".widget_content").html(data_html);
				$("#holder1").children("li:first").children(".widget_id").val(data.widget_id);
				$("#holder1").children("li:first").children(".widget_settings_content").children().children(".widget_form_holder").html(data.form);
				$("#holder1").children("li:first").children(".widget_settings_content").children().children('.wid').val(data.widget_id);
				$("#holder1").children("li:first").children('.hidden_flash_content').val('<div style="width:100%;">'+data_html+'</div>');
				event_reorder_function(event);
				$("#widget_toolbar").dialog("close");
				$('.widget').children().show();
				$('.hidden_flash_content').hide();
				$('.widget_settings_content').hide();
			}
		});
	});
	$('.widget_selector').hover(function(){
		var v_widget_id = $(this).children(".widget_selector_id").val();
		$(".toolbar_widget:last").children(".widget_id").val(v_widget_id);
		$(".toolbar_widget:last").children(".widget_page").val( $(".widget_page").val());
		$(".toolbar_widget:last").children(".widget_header").val($(this).text());
		$.ajax({
			type: "POST",
			url: "/api/ajax_new_chart/"+v_widget_id+"/lines/?preview=1",
			dataType: "json",
			async: true,
			success: function(data){
				$('.toolbar_widget:last').children().children(".widget_header").text(data.header);
				$('.toolbar_widget:last').children(".widget_content").html(data.html);
				data_html = data.html;
			}
		});
	});
	$(".show_buttons").live("click",function(event){
		event.preventDefault();
		$(this).prev().hide("slow");
	});
	
	$(".show_buttons").live("mouseover",function(){
		$(this).prev().show("slow");
		
	});
	/*$(".widget").live("mouseout", function(event){
		$(this).children(".widget_buttons").hide("slow");
	});*/
	$('.widget_table tbody tr:even').css('background-color', 'white');
	$('.date-picker').datepicker({showOn: 'both', buttonImage: '/images/calendar.gif', buttonImageOnly: true, dateFormat: 'mm/dd/yy'});
}

$.extend({URLEncode:function(c){var o='';var x=0;c=c.toString();var r=/(^[a-zA-Z0-9_.]*)/;
  while(x<c.length){var m=r.exec(c.substr(x));
    if(m!=null && m.length>1 && m[1]!=''){o+=m[1];x+=m[1].length;
    }else{if(c[x]==' ')o+='+';else{var d=c.charCodeAt(x);var h=d.toString(16);
    o+='%'+(h.length<2?'0':'')+h.toUpperCase();}x++;}}return o;},
URLDecode:function(s){var o=s;var binVal,t;var r=/(%[^%]{2})/;
  while((m=r.exec(o))!=null && m.length>1 && m[1]!=''){b=parseInt(m[1].substr(1),16);
  t=String.fromCharCode(b);o=o.replace(m[1],t);}return o;}
});


