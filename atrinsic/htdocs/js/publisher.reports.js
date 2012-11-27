function initRunRptFormManipulation() {  
    // Move the Date_to field to same line as Date_from and add "and" between
    $("#id_end_date").parent().insertAfter($("#id_start_date").parent())
    // Remove Empty Line that remains.
    $("#id_start_date").parent().parent().next().next().remove();
    $(".filterBtn").insertAfter($("#id_report_type").parent())
    $("#id_end_date, #id_start_date").datepicker({showOn: "both", clickInput:true, dateFormat: "mm/dd/yy", buttonImage: "/images/blankdatepicker.png",buttonImageOnly: true});  
    $("legend").remove();
}
function DataTableResults() {
    $('.widget_table').dataTable({'bFilter':false,
	                       'bJQueryUI': true,
                       'bLengthChange':false,
                       'iDisplayLength':25,        
                       'bAutoWidth': false}); 
                       
	var selReportType = $('#id_report_type :selected').val()
	// If report type "Sales and Activity Report By Advertiser"(9) or "Revenue Report by Advertiser"(10)
    if(selReportType == 9 || selReportType == 10){ 
        $('.widget_table tbody tr').each( function() {
            var nTds = $('td', this);
            var advId = $(nTds[0]).text(); // Advertiser Id is the 1st Column
            var advName = $(nTds[1]).text(); // Advertiser name is 2nd Column, which is where we want our link.
            
            $(nTds[1]).html('<a href="" id="/publisher/advertisers/view/'+advId+'/" class="AjaxLightBox" name="'+advName+' - Profile">'+advName+'</a>')        
        });
    }
}



function displayDialog(obj){	
	if (obj.type == "select-one" ||obj.type == "select-multiple"){
		var var_content = "";
		for (var i = 0; i < obj.options.length; i++){
			if (obj.options[ i ].selected){
				if(var_content == ""){
					var_content = obj.options[ i ].text;
				}else{
					var_content += ", "+obj.options[ i ].text;	
				}
			}
		}
	}else{
		var_content = $(obj).val();
	}
    $("input:submit").click(function(event){
		event.preventDefault();    		
        value = $('.run_reports_by:checked').val()
        var bolAddtoForm = false
        if (value == '1') {
            $('#Vertical').remove();
            $appendThis = $('#Advertiser')
            bolAddtoForm = true
        } else if (value == '2') {
            $('#Advertiser').remove();
            $appendThis = $('#Vertical')
            bolAddtoForm = true
        } else {
            $('#Vertical').remove();
            $('#Advertiser').remove();
        }
        if(bolAddtoForm){
            
    		$appendThis.css('position','absolute')
    		$appendThis.css('left','-1000px')
    		$appendThis.css('top','-300px')
    		$appendThis.show();        		
    		$('#report_form').append($appendThis);
    	}
		$("#report_form").submit();
	});
	if (obj.type=='radio'){
		if(obj.checked){
			var chosen_type =$(obj).parent().text();
			if ($.trim(chosen_type) == "Advertiser" || $.trim(chosen_type) == "Vertical"){    			    

			    if ($.trim(chosen_type) == "Advertiser"){
			        var dWidth = 300
			        var dHeight = 100
			    }else{
			        var dWidth = 300
			        var dHeight = 400    				        
			    }
			    $('#'+$.trim(chosen_type)).dialog({
			                            width:dWidth, 
			                            height:dHeight,		                             
                                        open: function(event, ui) { 			                   
                                         $("#ui-dialog-title-" + $.trim(chosen_type)).text($.trim(chosen_type));
                                         $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
                                         $(".ui-dialog-titlebar-close span").remove();
                                         $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
                                         $(".ui-dialog-titlebar-close").text("Close");			                   
                                        } });
                $('#'+$.trim(chosen_type)).bind('dialogclose', function(event, ui) {
	                $('#'+$.trim(chosen_type)).dialog("destroy");
                });	
	                
			}
		}
	}
}

$(".run_reports_by").live("click",function(event) {
   displayDialog(this);
});

$(".dwnldDynamicWidget").click(function(event) {
    event.preventDefault();
	$('#download_types').dialog({width:325, 
	                             height:225,
	                             modal: true,
	                             draggable: false,
	                             resizable: false,		                             
    			                 open: function(event, ui) { 			                   
    			                     $("#ui-dialog-title-dashBoardSettingsDlg").text("Dashboard Settings");
    			                     $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
    			                     $(".ui-dialog-titlebar-close span").remove();
    			                     $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
    			                     $(".ui-dialog-titlebar-close").text("Close");			                   
    		                     }         		                     
     });
	$('#download_types').bind('dialogclose', function(event, ui) {
	    $("#target").val("");
		$('#download_types').dialog("destroy");
	});	
});
$(".downloadCSV").live("click",function(event) {
		event.preventDefault();
		$("#target").val("0");
		$('#download_types').dialog("destroy");
		$("#report_form").submit();
		$("#target").val("");
    });

$(".downloadXLS").live("click",function(event) {
	event.preventDefault();
	$("#target").val("2");
	$('#download_types').dialog("destroy");
	$("#report_form").submit();
	$("#target").val("");
});
$(".downloadTAB").live("click",function(event) {
	event.preventDefault();
	$("#target").val("1");
	$('#download_types').dialog("destroy");
	$("#report_form").submit();
	$("#target").val("");
});