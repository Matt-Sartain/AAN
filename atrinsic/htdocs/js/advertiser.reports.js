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
	// If report type "Sales and Activity Report By Publisher"(1) or "Revenue Report by Publisher"(3)
    if(selReportType == 1 || selReportType == 3){ 
        $('.widget_table tbody tr').each( function() {
            var nTds = $('td', this);
            var pubId = $(nTds[0]).text(); // Publisher Id is the 1st Column
            var pubName = $(nTds[1]).text(); // Publisher name is 2nd Column, which is where we want our link.
                        
            // Check if the link has already been created.
            if (pubName.substring(0,2) != "<a") {
                $(nTds[1]).html('<a href="" id="/advertiser/publishers/view/'+pubId+'/" class="AjaxLightBox" name="'+pubName+' - Profile">'+pubName+'</a>')        
            }
                
        });
    }
    
    var selGroupBy = $("input[@name='group_by']:checked").val()
	// If report type "Sales and Activity Report"(0) or "Revenue Report"(2)
    if(selReportType == 0 || selReportType == 2){ 
        $('.widget_table tbody tr').each( function() {
            var nTds = $('td', this);
            var colDate = $(nTds[0]).text(); // Date column
            
            // Now we must format according to group by selection. 0 = Day, 1 = Week, 2 = Month, 3 = Quarter
            if(selGroupBy == 2) // Month
            {
                Date.format = 'mmm yyyy';
                var dtm = new Date($(nTds[0]).text());
                $(nTds[0]).text(dtm.asString());
            }
                
    
        });
    }
}

function displayDialog(obj){	
    
    $("input:submit").click(function(event){
		event.preventDefault();    		
        value = $('.run_reports_by:checked').val()
        var bolAddtoForm = false
        if (value == '1') {
            $('#Vertical').remove();
            $('#Publishers').remove();
            $appendThis = $('#Group')
            bolAddtoForm = true
        } else if (value == '2') {
            $('#Group').remove();
            $('#Publishers').remove();
            $appendThis = $('#Vertical')
            bolAddtoForm = true
        } else if (value == '3') {
            $('#Group').remove();
            $('#Vertical').remove();
            $appendThis = $('#Publishers')
            bolAddtoForm = true
        } else {
            $('#Group').remove();
            $('#Vertical').remove();
            $('#Publishers').remove();
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
			if ($.trim(chosen_type) == "Group" || $.trim(chosen_type) == "Vertical" || $.trim(chosen_type) == "Publishers"){    			    
			    if ($.trim(chosen_type) == "Group"){
			        var dWidth = 300
			        var dHeight = 200
			    }else if ($.trim(chosen_type) == "Vertical"){
			        var dWidth = 300
			        var dHeight = 400
			    }else{
			        var dWidth = 300
			        var dHeight = 400    				        
			    }
			    $('#'+$.trim(chosen_type)).dialog({
			                            width:dWidth, 
			                            height:dHeight,
			                            modal:true,		                             
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