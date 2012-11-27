$(document).ready(function(){
    $(".apply_button, .ButtReApply, .apply_all").live('click',function(event) {
        event.preventDefault();
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
        var v_this = $(this);
        var v_post_url_start = $(this).attr("href");
        var id_list = [];
        var v_post_url = v_post_url_start;
        if ($(this).hasClass('.apply_all')){
            $(".checkbox").each(function(){
                if ($(this).attr("checked") == true){
                    id_list.push($(this).val());    
                }
            });
            if (id_list.length > 0){
                v_post_url += "?advertiser_id="+id_list;
            }    
        }
        $.ajax({
    		type: "POST",
    		url: v_post_url,
    		success: function(msg){
    		    if(msg == 'Applied'){
    		        $(v_this).removeClass('apply_button');
    		        $(v_this).removeClass('AdvertiserApproved');
    		        $(v_this).removeClass('report_btns');
    		        $(v_this).removeClass('botRight');
    		        $(v_this).addClass('application_completed');
    		        $(v_this).html(msg);
    		    }else{
    		        dialogbox = $("<div>"+msg+"</div>");
    			    dialogbox.dialog({bgiframe: true,height: 500, width: 600, modal: true,draggable: true,resizable: true});
            		dialogbox.bind('dialogclose', function(event, ui) {
            			dialogbox.dialog("destroy");
            		});	
    		    }
    		}
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
    });
});