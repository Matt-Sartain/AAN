
$("#addWidget").live("click", function(event){
	event.preventDefault();
	$("#widget_toolbar").dialog({bgiframe: true,	
	                             height: 400, 
	                             width: 600, 
	                             modal: true,
	                             draggable: false,
	                             resizable: false,
				                 open: function(event, ui) { 
				                   $("#ui-dialog-title-widget_toolbar").text("Add Widget");
				                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
				                   $(".ui-dialog-titlebar-close span").remove();
				                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
				                   $(".ui-dialog-titlebar-close").text("Close");
			                   } });
	$("#widget_toolbar").bind('dialogclose', function(event, ui) {
		$("#widget_toolbar").dialog("destroy");
	});	
});

//WIDGET SETTINGS
$(".widgetSettingsBtn").live("click", function(event){
		event.preventDefault();
		$(this).parent().parent().parent().siblings('.widget_content').hide();
		$(this).parent().parent().parent().siblings('.widget_settings_content').show();
	});

//ADDING A NEW WIDGET	
$('.widget_selector').live("click", function(event){
    event.preventDefault();
    var widget_id = $(this).siblings(".widget_selector_id").val();
	var widget_page = $(".widget_page").val();
	
	data_html = '';	
	$.ajax({
		type: "POST",
		url: "/api/ajax_add_widget/"+widget_id+"/"+widget_page+"/",
		dataType: "json",
		async: true,
		success: function(data){
		    location.reload();
		    /*
		    $("#mainWidgetCtn").prepend("<li class='dynamicWidgetCtn'>"+$('#widget_template').html()+"</li>");
		    $("#mainWidgetCtn").children("li:first").children(".dynamicWidgetHdrCtn").children(".dynamicWidgetHdr").html(data.header);
		    $("#mainWidgetCtn").children("li:first").children(".dynamicWidget").html(data.html);
			$("#mainWidgetCtn").children("li:first").children(".currentWidgetID").val(data.widget_id);
			$("#mainWidgetCtn").children("li:first").children(".dynamicWidgetSettings").children(".widgetSettingsForm").children(".widget_form_holder").html(data.form);
			$("#mainWidgetCtn").children("li:first").children(".dynamicWidgetSettings").children(".widgetSettingsForm").children('.wid').val(data.widget_id);
			$("#mainWidgetCtn").children("li:first").children(".hidden_flash_content").val('<div style="width:100%;">'+data.html+'</div>');
			$("#mainWidgetCtn").children("li:first").children(".dynamicWidget").children('.widget_table').dataTable({'bFilter':false,'bJQueryUI': true,'bLengthChange':false,'iDisplayLength':25,'bAutoWidth':false});
			$("#widget_toolbar").dialog("close");
			*/
			
			/*
			$('.dynamicWidgetHdrCtn').show();
			$('.dynamicWidgetFtr').show();
			
			$('.hidden_flash_content').hide();
			$('.widget_settings_content').hide();
			*/	
			
	    }
	});  

});


$(".widgetSettingsBtn").live("click", function(event){
	event.preventDefault();
	$(this).parent().parent().siblings('.dynamicWidget').hide();
	$(this).parent().parent().siblings('.dynamicWidgetSettings').show();
});
$(".showWidgetOptions").live("click",function(event){
    event.preventDefault();
	$(this).prev().toggle("slow");
});

//CHANGING CHART STYLE

$(".chartStyle").live("click", function(event){
		event.preventDefault();
		change_chart_styles($(this));
	});
	
	
function change_chart_styles(v_this){
	var widget_id = v_this.parent().parent().parent().children(".currentWidgetID").val();
	var widget_style = v_this.attr("id");
	
	$.ajax({
		type: "POST",
		url: "/api/ajax_new_chart/"+widget_id+"/"+widget_style+"/",
		dataType: "json",
		async: false,
		success: function(data){
			current_widget = v_this.parent().parent().parent();
			current_widget.children(".dynamicWidget").html(data.html);
			current_widget.children('.hidden_flash_content').val('<div style="width:100%;">'+data.html+'</div>');
			
			//current_widget.children(".dynamicWidgetHdrCtn").children(".dynamicWidgetHdr").children(".widget_header").text(data.header);
			//v_this.parent().parent().parent().parent().children('.widget_id').val(data.widget_id);
			//v_this.parent().parent().parent().parent().children('.widget_settings_content').children().children('.wid').val(data.widget_id);
			
		}
	});
	
	
}
$(".zoomDynamicWidget").live("click", function(event){
		event.preventDefault();

		$($(this).parent().parent().siblings(".hidden_flash_content").val()).dialog({
			bgiframe: true,
			height: 400,
			width: '95%',
			modal: true,
			draggable: false,
			resizable: false,open: function(event, ui) { 
				                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
			                   } 
		});

		$(this).parent().parent().siblings('.dynamicWidget').show();
		$(this).parent().parent().siblings('.dynamicWidgetSettings').hide();
	});

