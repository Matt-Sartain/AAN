$(".applyToAdvertiser").live("click", function(event){
    event.preventDefault();

	var dWidth = 700;
	var dHeight = 545;	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");		
	$apply = $(this)
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
		    if(data == "Applied") { 
		        $apply.replaceWith('<font color="#090">Applied</font>')
		        return false;		        
            }
			$("#ajaxLightbox").html(data);			
			$("#ajaxLightbox").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 
			                   $("#ui-dialog-title-ajaxLightbox").text(dialogHdr); 
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
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

        }    
	});     
});
$(".applyToSelected").live("click", function(event){
    event.preventDefault();

	var dWidth = 700;
	var dHeight = 545;	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");		
	$apply = $(this)
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
		    if(data == "Applied") { 
		        $("input:checkbox").each(function(event) {
		            if (this.checked) { 
		                var o = $(this).parent().parent();
		                o.find(".applyToAdvertiser").replaceWith('<font color="#090">Applied</font>');}
		        });
		        return false;		        
            }
			$("#ajaxLightbox").html(data);			
			$("#ajaxLightbox").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 
			                   $("#ui-dialog-title-ajaxLightbox").text(dialogHdr); 
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
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

        }    
	});     
});
$("#show_terms").live("click",function(event){
    var org_id = $(this).siblings().children(".accept_terms").val();
    event.preventDefault();
    $.ajax({
		type: "POST",
		url: '/publisher/advertisers/terms/'+org_id+'/',
		success: function(msg){
		    dialogbox = $("<div>"+msg+"</div>")
		    dialogbox.dialog({bgiframe: true,height: 500, width: 600, modal: true,draggable: true,resizable: true});
    		dialogbox.bind('dialogclose', function(event, ui) {
    			dialogbox.dialog("destroy");
    		});	
    		$("#lb_print").live("click",function(event){
                event.preventDefault();
                window.open($(this).attr("href"));
            });
            $(".lb_cancel").bind("click",function(event){
                event.preventDefault();
                var org_id = $(this).siblings("#org_id").val();
        	    $("#accept_terms_"+org_id).attr("checked",false);
        	    dialogbox.dialog("destroy");
        	});
        	$(".lb_accept").bind("click",function(event){
        	    event.preventDefault();
        	    var org_id = $(this).siblings("#org_id").val();
        	    $("#accept_terms_"+org_id).attr("checked",true);
        	    dialogbox.dialog("destroy");
        	});
		}
	});
});
$("#lb_continue").live('click',function(event){
    $(".accept_terms").each(function(){
         event.preventDefault();
         if ($(this).attr('checked') == true){
    	    var v_post_url = $("#lb_continue").attr("href");
            var id_list = [];
            id_list.push($(this).val());
            if (id_list.length > 0){
                v_post_url += "&advertiser_id="+id_list;
            }
            window.location = v_post_url;
        }
    });
});