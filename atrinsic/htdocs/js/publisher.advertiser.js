function initSearchFormManipulation() {  
    // Move the Date_to field to same line as Date_from and add "and" between
    $("#id_date_to").parent().insertAfter($("#id_date_from").parent())
    $("#id_date_from").parent().append("and")
    // Remove Empty Line that remains.
    $("#id_vertical").parent().parent().prev().remove();
    $(".filterBtn").insertAfter($("#id_network_rating").parent())
    $("#id_date_to, #id_date_from").datepicker({showOn: "both", clickInput:true, dateFormat: "mm/dd/yy", buttonImage: "/images/blankdatepicker.png",buttonImageOnly: true});  
}
   	
function initRecruitAdvertisers(){    
    $(".applyToSelected").mouseover(function(){
        var link = "/publisher/advertisers/apply/?advertiser_id=";
        $("input[name='advertiser_id_h']").each(function(){
            link += this.value + "&advertiser_id=";
        });
        link = link.substring(0, link.lastIndexOf("&advertiser_id="), 0);
        $(".applyToSelected").attr('id', link);
    });  
    $("input:checkbox").click(function(event) {
        if(this.checked){
            $("#All_ad_ID").append('<input type="hidden" name="advertiser_id_h" value="'+this.value+'" id="o_'+this.value+'_h"/>');
        } else {
            var selector = '#'+this.id+'_h';            
            $(selector).remove();
        }
    });
    $(".dataTableSelectAll").click(function() {
        $("input:checkbox").each(function () {
            if(this.checked){
                var selector = '#'+this.id+'_h';            
                $(selector).remove();
            } else {
                $("#All_ad_ID").append('<input type="hidden" name="advertiser_id_h" value="'+this.value+'" id="o_'+this.value+'_h"/>');
            }            
        });
    });
    //$(".applyToSelected").click(function(event) {
    //    event.preventDefault();
    //    bolContinue = false
    //    $("input:checkbox").each( function() {
    //        if(this.checked){
    //            bolContinue = true
    //        }
    //    });
    //    if(bolContinue){
    //        $("#checkbox_form").attr("action", "/publisher/advertisers/apply/");
    //        $("#checkbox_form").submit();
    //    }
    //});
} 
function initMyAdvertisers(){
    
    $(".expireSelected").click(function(event) {
        event.preventDefault();
        $("#checkbox_form").attr("action", "/publisher/advertisers/expire/");
        $("#checkbox_form").submit();
    });
}

function initPendingOffers(){
    $(".acceptSelected").click( function(event) {
        event.preventDefault();
        $("#method").val("accept");
        $("#pendingOffers").submit();        
    });

    $(".declineSelected").click( function(event) {
        event.preventDefault();
        $("#method").val("decline");
        $("#pendingOffers").submit();        
    });
} 

function DataTableResults() {
    $(".dataTableSearchResults").dataTable({"bFilter":true,
 	                         "bJQueryUI": true,
                             "bLengthChange":true,
                             "bPaginate": true,
                             "iDisplayLength":50,        
                             "bAutoWidth": false,
                             "aoColumns" : [
                                { sWidth: "6%" },
                                { sWidth: "24%" },
                                { sWidth: "17%" },
                                { sWidth: "10%" },
                                { sWidth: "10%" },
                                { sWidth: "12%" },
                                { sWidth: "20%" }]
    });

    $(".dataTables_length").parent().removeClass("ui-widget-header")
    $(".dataTables_info").parent().removeClass("ui-widget-header")    
    
    $(".customDisabledPrevPage").css("background-image","url(/images/BL_prev.gif)")
    $(".customDisabledNextPage").css("background-image","url(/images/BL_next.gif)")
    $(".customNextPage").css("background-image","url(/images/BL_next_blue.gif)")
    $(".customPrevPage").css("background-image","url(/images/BL_prev_blue.gif)")
    
}




function initGetLinks(){
    $("#websiteForm .clearfix").remove();
	$(".getLink").click(function(event) {	
	    event.preventDefault();
	    var ajaxUrl = $(this).attr("id");	
	    $row = $(this).parents("tr")
    	$.ajax({    		
			type: "GET",
			url: ajaxUrl,
			dataType: "html",
			async: true,
			success: function(data){
			    // Remove form if displayed anywhere else.
			    $(".dWebsiteForm").remove();
			    var getWebsiteForm = $("#websiteForm").html()
			    getWebsiteForm = getWebsiteForm.replace("REPLACEACTION", ajaxUrl)
			    getWebsiteForm = getWebsiteForm.replace("REPLACEID", "viewLinkForm")
			    $("<tr class='dWebsiteForm'><td colspan=4>" + getWebsiteForm + "</td></tr>").insertAfter($row)
			    function showResponse(responseText, statusText)  { 
                    $("#AjaxContentFromDialog").html(responseText);	
    				$("#AjaxContentFromDialog").dialog({autoOpen:false,
    				               bgiframe:true, 
    				               height:500, 
    				               width:500, 
    				               modal:true, 
    				               draggable:false, 
    				               resizable:false,
    				               open: function(event, ui) {
        			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
        			                   $(".ui-dialog-titlebar-close span").remove();
        			                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
        			                   $(".ui-dialog-titlebar-close").text("Close");		
    			                   } 
    			               });
    			    $("#AjaxContentFromDialog").dialog("open");
                    $(".goBackBtn").click(function(event) {	
                        $("#AjaxContentFromDialog").dialog("destroy");
                    });
                    $("#AjaxContentFromDialog").bind("dialogclose", function(event, ui) {
                        $("#AjaxContentFromDialog").dialog("destroy");
                    });

                	//return true; 
                    
                }     
		        var opts = {
                    //target:        '#AjaxContentFromDialog',
                	success:       showResponse  // post-submit callback
                	//beforeSubmit:  showPreResponse, 
                	//error:         errorOut
                };
		        $('#viewLinkForm').bind('submit', function() {       
                	$(this).ajaxSubmit(opts);
                	return false; // <-- important!
                });	

			},
            error:function (xhr, ajaxOptions, thrownError){
                alert("Status Code: " + xhr.status + ". Further error details should go here.");                                
			    hideAjaxLoading();
            }    
		}); 		
	});	
}	


