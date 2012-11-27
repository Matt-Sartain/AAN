function hideAssignedTo() { 
        $('#id_assigned_to_program_term').parent().parent().hide();
        $('#id_assigned_to_group').parent().parent().hide();
        $('#id_assigned_to_individual').parent().parent().hide();
        $('#id_assigned_to_minimum_rating').parent().parent().hide();
        $('#id_assigned_to_promotion_method').parent().parent().hide();
        $('#id_assigned_to_publisher_vertical').parent().parent().hide();
}

function initDatePickers(){
    $("#id_start_date, #id_end_date").datepicker({showOn: "both", clickInput:true, dateFormat: "mm/dd/yy", buttonImage: "/images/blankdatepicker.png",buttonImageOnly: true}); 
}

function initAssignedTo(){
    hideAssignedTo()
    initDatePickers()
    if ($('#id_assigned_to').val() == '2') {
        $('#id_assigned_to_program_term').parent().parent().show();
    } else if ($('#id_assigned_to').val() == '3') {
        $('#id_assigned_to_group').parent().parent().show();
    } else if ($('#id_assigned_to').val() == '4') {
        $('#id_assigned_to_individual').parent().parent().show();
    } else if ($('#id_assigned_to').val() == '5') {
        $('#id_assigned_to_minimum_rating').parent().parent().show();
    } else if ($('#id_assigned_to').val() == '6') {
        $('#id_assigned_to_promotion_method').parent().parent().show();
    } else if ($('#id_assigned_to').val() == '7') {
        $('#id_assigned_to_publisher_vertical').parent().parent().show();
    }
    $('#id_assigned_to').change(function() {
    	hideAssignedTo();
        if ($(this).val() == '2') {
            $('#id_assigned_to_program_term').parent().parent().show();
        } else if ($(this).val() == '3') {
            $('#id_assigned_to_group').parent().parent().show();
        } else if ($(this).val() == '4') {
            $('#id_assigned_to_individual').parent().parent().show();
        } else if ($(this).val() == '5') {
            $('#id_assigned_to_minimum_rating').parent().parent().show();
        } else if ($(this).val() == '6') {
            $('#id_assigned_to_promotion_method').parent().parent().show();
        } else if ($(this).val() == '7') {
            $('#id_assigned_to_publisher_vertical').parent().parent().show();
        }
    });
}   

function initEditLinks(){
    initAjaxFormPostFromLightbox();
    initAssignedTo();
    initDatePickers();
}

$(".addLinksBtn").live("click", function(event){
    event.preventDefault();
    function ajaxLoading(){        
		$(".ajaxLoading").height($(".ajaxLoading").parents(".contentCtn").height());
		$(".ajaxLoading").width($(".ajaxLoading").parents(".contentCtn").width());
		$(".ajaxLoading").show();
    }
    function hideAjaxLoading(){
        $(".ajaxLoading").hide();
    }
    
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");
	ajaxLoading();		
    $("#ajaxLightbox").dialog("destroy");
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
		    hideAjaxLoading();
			$("#ajaxLightbox").html(data);			
			$("#ajaxLightbox").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 
			                   $("#ui-dialog-title-ajaxLightbox").text(dialogHdr); 
			                   $("#ui-dialog-title-ajaxLightbox").addClass("modifyDialogTitle");
			                   $(".ui-dialog-titlebar-close span").remove();
			                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
			                   $(".ui-dialog-titlebar-close").text("Close");
		                   } 
		               });
            $("#ajaxLightbox").bind("dialogclose", function(event, ui) {
                $("#ajaxLightbox").html("");
                $("#ajaxLightbox").dialog("destroy");
            });
			               
		},
        error:function (xhr, ajaxOptions, thrownError){
            alert("Status Code: " + xhr.status + ". Further error details should go here.");                                
		    hideAjaxLoading();

        }    
	}); 
});