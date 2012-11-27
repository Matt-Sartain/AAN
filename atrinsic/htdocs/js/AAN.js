/*************************** Live Button Events ****************************/
// Most of these Buttons are Primarily located on the Dashboard 
$("#helplink").click(function(e){
	e.preventDefault();
	window.open(this.href,"AAN_Help","location=1,status=1,scrollbars=1,width=800,height=552");
	return false;

});	
$('.deleteAjax').click(function() {			    						
	var type = $(this).attr("name");
	var del = confirm("Are you sure you want to delete this " + type + "?");
	if (!del){ return false; }	
	var callUrl = $(this).attr("id");			
	$.ajax({
		type: "GET",
		url: callUrl,
		dataType: "html",
		async: false,
		success: function(data){}
	}); 
});
// Widget header btns 
$(".closeWidget").live("click", function(event){
		event.preventDefault();
		var v_this = $(this);
		var v_widget_id = $(this).parent().parent().children(".currentWidgetID").val();
		$.ajax({
			type: "POST",
			url: "/api/ajax_remove_widget/"+v_widget_id+"/",
			async: false,
			success: function(data){
				$(v_this).parent().parent().remove();
				//event_reorder_function(event);
			}
		});
	});	
$(".collapseWidget").live("click", function(event){
	event.preventDefault();
	var $actObj = $(this).parent().next();
	$actObj.hide();
	$actObj.siblings(".dynamicWidgetFtr").hide();
	$(this).removeClass('collapseWidget');
	$(this).addClass('collapsedWidget');
});
$(".collapsedWidget").live("click", function(event){
	event.preventDefault();
	var $actObj = $(this).parent().next();
	$actObj.show();
	$actObj.siblings(".dynamicWidgetFtr").show();
	$(this).removeClass('collapsedWidget');
	$(this).addClass('collapseWidget');
});
$(".collapseStaticWidget").live("click", function(event){
	event.preventDefault();
	var $actObj = $(this).parent().next();
	$actObj.hide();
	$actObj.siblings(".dynamicWidgetFtr").hide();
	$(this).removeClass('collapseStaticWidget');
	$(this).addClass('collapsedStaticWidget');
});
$(".collapsedStaticWidget").live("click", function(event){
	event.preventDefault();
	var $actObj = $(this).parent().next();
	$actObj.show();
	$actObj.siblings(".dynamicWidgetFtr").show();
	$(this).removeClass('collapsedStaticWidget');
	$(this).addClass('collapseStaticWidget');
});
// Select All Button is available to many forms / tables
// *** We must Bind as a Live click ***
$(".dataTableSelectAll, .primaryDisplayTableSelectAll").live("click", function(event){
    event.preventDefault();
    $("input:checkbox").each( function() {
        this.checked = !this.checked;
    });
}); 
$(".dashboardSettings").live("click", function(event){
	event.preventDefault();
		// Dimensions
	dWidth = 600;
	dHeight = 200;
	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");		
	
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
			$("#dashBoardSettingsDlg").html(data);			
			$("#dashBoardSettingsDlg").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 			                   
			                   $("#ui-dialog-title-dashBoardSettingsDlg").text("Dashboard Settings");
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
			                   $(".ui-dialog-titlebar-close span").remove();
			                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
			                   $(".ui-dialog-titlebar-close").text("Close");			                   
		                   } 
		               });
            $("#dashBoardSettingsDlg").bind("dialogclose", function(event, ui) {
                $("#dashBoardSettingsDlg").dialog("destroy");
            });
			               
		},
        error:function (xhr, ajaxOptions, thrownError){
            alert("Status Code: " + xhr.status + ". Further error details should go here.");      

        }    
	}); 			   
});
/*************************** Payment Status Popup **********************************/
$(".PaymentStatusRpt").live("click", function(event){
	event.preventDefault();
		// Dimensions
	dWidth = 550;
	dHeight = 545;
	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");		
	
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
			$("#dashBoardSettingsDlg").html(data);			
			$("#dashBoardSettingsDlg").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 			                   
			                   $("#ui-dialog-title-dashBoardSettingsDlg").text("Payment Status");
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
			                   $(".ui-dialog-titlebar-close span").remove();
			                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
			                   $(".ui-dialog-titlebar-close").text("Close");			                   
		                   } 
		               });
            $("#dashBoardSettingsDlg").bind("dialogclose", function(event, ui) {
                $("#dashBoardSettingsDlg").dialog("destroy");
            });
			               
		},
        error:function (xhr, ajaxOptions, thrownError){
            alert("Status Code: " + xhr.status + ". Further error details should go here.");      

        }    
	}); 			   
});
$(".showMonthlyStats a").live("click", function(event){
    event.preventDefault(); 
    if($(this).parent().hasClass("expand")){
        $(this).parent().removeClass("expand")
        $(this).html("-")               
        $("<tr><td colspan=4 class='ajaxLoadingTd'></td></tr>").insertAfter($(this).parent().parent())            
        var callUrl = $(this).attr("href");		
        $rowClicked = $(this)
        $.ajax({
            type: "GET",
            url: callUrl,
            dataType: "html",
            async: false,
            success: function(data){   
                $rowClicked.parent().parent().next().remove()   
                $(data).insertAfter($rowClicked.parent().parent())
            }
        });
    }else{
        $(this).parent().addClass("expand")
        $(this).html("+")   
        $(this).parent().parent().next().remove()             
    }
});
$(".approveByPub").live("click", function(event){
    event.preventDefault();         	
    $currentRow = $(this).parents("tr").children(".showMonthlyStats").children("a")
    if($currentRow.text()=="-"){            
        $currentRow.trigger("click");            
    }       
    $approvedPub = $(this)
    var callUrl = $(this).attr("id");	 
    $.ajax({
        type: "GET",
        url: callUrl,
        dataType: "html",
        async: false,
        success: function(data){   
            $approvedPub.parent().html(data)
        }
    });
});	
$(".approveMonth").live("click", function(event){
    event.preventDefault(); 
    var callUrl = $(this).attr("id");		
    $approvedMonth = $(this)
    $.ajax({
        type: "GET",
        url: callUrl,
        dataType: "html",
        async: false,
        success: function(data){   
            $approvedMonth.parent().html(data)
        }
    });
});	
/*************************** Payment Status Popup **********************************/

/*************************** END Live Button Events ****************************/

/*************************** Initialize Notifications ****************************/
function init_notifications(){
    $('#NotificationsBtn').click(function(event){
        event.preventDefault();
        $('#NotificationsCtn').slideToggle("slow");
        
    });
    $('#closeNotificationsBtn').click(function(event){
        event.preventDefault();
        $('#NotificationsCtn').slideUp("slow");
        
    });
    $('.deleteNotificationsBtn').click(function(event){
        event.preventDefault();
        var v_this = $(this);
        var notificationType = v_this.parent().prev().children('#notification_type').text();

        $.ajax({
    		type: "POST",
    		url: '/api/remove_notification/'+notificationType+'/'+v_this.attr("alt")+'/',
    		dataType: "html",
    		async: false,
    		success: function(){
    		    x = v_this.parent().parent().children().length;
    		    if (x == 1){
    		        new_li ="<li>No new notifications</li>";
                    v_this.parent().html(new_li);
    		    }else{
    		        v_this.parent().parent().remove();
    		    }
    		}
    	}); 
    });    
}

/*************************** END Initialize Notifications ****************************/

function initDashSettingsFormManipulation(){   
    $("legend").remove()
    $(".dashboardSettingsUpdateBtn").insertAfter($("#id_dashboard_variable1").parent())    
}


function getDialogSize($this){
	var dWidth = 700;
	var dHeight = 545;	
	if($this.hasClass("dXXtraSm")) { dHeight = 250; dWidth = 400; } //
	if($this.hasClass("dXtraSm")) { dHeight = 250; dWidth = 600; } // 
	if($this.hasClass("dXtraSmallWide")) { dHeight = 250; dWidth = 850; } //
	if($this.hasClass("dNormal")) { dHeight = 600; dWidth = 600; } // 
	if($this.hasClass("dSmall")) { dHeight = 400; dWidth = 500; } // 
	if($this.hasClass("dSmallWide")) { dHeight = 400; dWidth = 850; } // 
	if($this.hasClass("dShorterMed")) { dHeight = 400; dWidth = 950; } // 
	if($this.hasClass("dMed")) { dHeight = 600; dWidth = 950; } // 
	return [dWidth, dHeight]
}
/*************************** Ajax Initialization Functions ***************************/
function initAjaxLightBox(){
    /*
        Additional classes that represent size for Lightbox:
        dXtraSm - width 600, height 250
        dSmall - width 500, height 400
    */
    function ajaxLoading(){        
		$(".ajaxLoading").height($(".ajaxLoading").parents(".contentCtn").height());
		$(".ajaxLoading").width($(".ajaxLoading").parents(".contentCtn").width());
		$(".ajaxLoading").show();
    }
    function hideAjaxLoading(){
        $(".ajaxLoading").hide();
    }
	$(".AjaxLightBox").live("click", function(event){
	    event.preventDefault();
		// Default Dimensions
		dialogSizes = getDialogSize($(this));
		dWidth = dialogSizes[0];  // 
		dHeight = dialogSizes[1]; 
		var ajaxUrl = $(this).attr("id");		
		var dialogHdr = $(this).attr("name");		
		ajaxLoading();
		
		var $curObj = $(this)
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
				                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
				                   //$("#ui-dialog-title-ajaxLightbox").addClass("modifyDialogTitle");
				                   $(".ui-dialog-titlebar-close span").remove();
				                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
				                   $(".ui-dialog-titlebar-close").text("Close");
			                   } 
			               });
                $("#ajaxLightbox").bind("dialogclose", function(event, ui) {
                    $("#ajaxLightbox").html("");
                    $("#ajaxLightbox").dialog("destroy");    
                    if($curObj.hasClass("ReloadOnClose")){location.reload();}
                });
				              
			},
            error:function (xhr, ajaxOptions, thrownError){
                alert("Status Code: " + xhr.status + ". Further error details should go here.");                                
			    hideAjaxLoading();

            }    
		}); 
	
	
	});
	
    function ajaxLoadingFromLightbox(){        
		$("#AjaxContent .ajaxLoading").height($(".ajaxLoading").parents("#ajaxLightbox").height());
		$("#AjaxContent .ajaxLoading").width($(".ajaxLoading").parents("#ajaxLightbox").width());
		$("#AjaxContent .ajaxLoading").show();
    }
    function hideAjaxLoadingFromLightbox(){
        $("#AjaxContent .ajaxLoading").hide();
    }    
	$(".AjaxLightBoxFromLightbox").live("click", function(event){
	    event.preventDefault();
		// Default Dimensions
		dialogSizes = getDialogSize($(this))
		dWidth = dialogSizes[0];  // 
		dHeight = dialogSizes[1]; 
		
		var ajaxUrl = $(this).attr("id");		
		var dialogHdr = $(this).attr("name");		
        ajaxLoadingFromLightbox();		
    	$.ajax({    		
			type: "GET",
			url: ajaxUrl,
			dataType: "html",
			async: true,
			success: function(data){
                hideAjaxLoadingFromLightbox();
				$("#AjaxLightBoxFromLightbox").html(data);			
				$("#AjaxLightBoxFromLightbox").dialog({bgiframe:true, 
				               height:dHeight, 
				               width:dWidth, 
				               modal:true, 
				               draggable:false, 
				               resizable:false,
				               open: function(event, ui) { 
				                   $("#ui-dialog-title-AjaxLightBoxFromLightbox").text(dialogHdr); 
				                   $("#ui-dialog-title-AjaxLightBoxFromLightbox").addClass("modifyDialogTitle");
				                   $(".ui-dialog-titlebar-close span").remove();
				                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
				                   $(".ui-dialog-titlebar-close").text("Close");
			                   } 
			               });
                $("#AjaxLightBoxFromLightbox").bind("dialogclose", function(event, ui) {
                    $("#AjaxLightBoxFromLightbox").html("");
                    $("#AjaxLightBoxFromLightbox").dialog("destroy");
                });
                
                $(".cancelBtn").click( function(event) {
                    $("#AjaxLightBoxFromLightbox").html("");
                    $("#AjaxLightBoxFromLightbox").dialog("destroy");
                });
				               
			},
            error:function (xhr, ajaxOptions, thrownError){
                hideAjaxLoadingFromLightbox();
                alert("Status Code: " + xhr.status + ". Further error details should go here.");                                


            }    
		}); 
	
	
	});
}	
function initAjaxFormPost(){  

    function ajaxLoading(){   
    	$("#AjaxContent .ajaxLoading").height($("#AjaxContent").parents("#ajaxLightbox").height());
    	$("#AjaxContent .ajaxLoading").width($("#AjaxContent").parents("#ajaxLightbox").width());
    	$("#AjaxContent .ajaxLoading").show();
    }
    function hideAjaxLoading(){
        $("#AjaxContent .ajaxLoading").hide();
    }
    var opts = {
        //target:        '#AjaxContent',
    	success:       showResponse,  // post-submit callback
    	error:         errorOut
    };
    var bolDoNotReload = false
    $('form').bind('submit', function() {
        if($(this).hasClass("DoNotReload")){
            bolDoNotReload = true
        }
        ajaxLoading();
    	$(this).ajaxSubmit(opts);
    	return false; // <-- important!
    });	

    function showResponse(responseText, statusText)  { 
        
		if(responseText.indexOf("errorlist") > 0){	
		    $("#AjaxContent").html(responseText);
		}else{			
            //hideAjaxLoading(); 
            if(!bolDoNotReload){
                $("#ajaxLightbox").dialog("destroy");
                location.reload();
            }else{
                var newProgramVars = eval( "(" + responseText + ")" ); //vars - programId, programName
                
            	$.ajax({    		
        			type: "GET",
        			url: '/advertiser/settings/programs/' + newProgramVars.programId + '/',
        			dataType: "html",
        			async: true,
        			success: function(data){
        			    $("#ajaxLightbox").html("")
        			    $("#ui-dialog-title-ajaxLightbox").text("Program: " + newProgramVars.programName);
        				$("#ajaxLightbox").html(data);		
                        $("#ajaxLightbox").bind("dialogclose", function(event, ui) {
                            location.reload(); 
                        });
    				},
                    error:function (xhr, ajaxOptions, thrownError){
                        alert("Status Code: " + xhr.status + ". Further error details should go here.");                                                
                    }    
        		}); 

            }
		}
        
    }     
    function errorOut(){ 
        alert("An unexpected error has occured. Please try again later.");
        hideAjaxLoading(); 
        $("#ajaxLightbox").dialog("destroy");
        
    }    
}
function initAjaxFormPostFromLightbox(){  

    function ajaxLoadingFromLightbox(){  
    	$("#AjaxContentFromDialog .ajaxLoading").height($("#AjaxContentFromDialog").parents("#AjaxLightBoxFromLightbox").height());
    	$("#AjaxContentFromDialog .ajaxLoading").width($("#AjaxContentFromDialog").parents("#AjaxLightBoxFromLightbox").width());
    	$("#AjaxContentFromDialog .ajaxLoading").show();
    }
    
    function hideAjaxLoadingFromLightbox(){
        $("#AjaxContentFromDialog .ajaxLoading").hide();
    }
    
    function showResponse(responseText, statusText)  { 
		if(responseText.indexOf("errorlist") > 0){
		    $("#AjaxContentFromDialog").html(responseText);
		}else{
            hideAjaxLoadingFromLightbox();
            $("#ajaxLightbox").html(responseText);
            $("#AjaxLightBoxFromLightbox").dialog("close");
            $("#AjaxLightBoxFromLightbox").dialog("destroy");
             
		}
        
    }     
    function errorOut(){ 
        alert("An unexpected error has occured. Please try again later.");
        hideAjaxLoadingFromLightbox(); 
        $("#AjaxLightBoxFromLightbox").dialog("destroy");
        
    }
    var opts = {
        //target:        '#AjaxContent',
    	success:       showResponse,  // post-submit callback
    	error:         errorOut
    };
    $('form').bind('submit', function() {
        ajaxLoadingFromLightbox();
    	$(this).ajaxSubmit(opts);
    	return false; // <-- important!
    });	
}
/*************************** END Ajax Initialization Functions ***************************/

/*********************************** HELP SECTION ***************************************/

$(".closeHelp").live("click", function(event){  
    event.preventDefault()
    $("#dashBoardSettingsDlg").dialog("destroy");
});


$(".helpMenuSubNav a").live("click", function(event){  
    if($(this).attr("name") != "Contact"){
	    event.preventDefault();
	    if ( $(this).parents("#advertiserHelp").length ){
            $("#helpIntroduction").hide();
            $("#helpCustomize").hide();
            $("#helpManagePub").hide();
            $("#helpManageLinks").hide();
            $("#helpCheckNetMsg").hide();
            $("#helpRunReports").hide();
            $("#helpSettings").hide();
        }else{
            $("#helpIntroduction").hide();
            $("#helpCustomize").hide();
            $("#helpAdvertisers").hide();
            $("#helpRetrievingLinks").hide();
            $("#helpCheckNetMsg").hide();
            $("#helpRunReports").hide();
            $("#helpSettings").hide();
        }
        $("#"+$(this).attr("name")).show();
	}
    
});
$(".displayHelp").live("click", function(event){
    event.preventDefault();
	// Dimensions
	dWidth = 800;
	dHeight = 465;
	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = "Atrinsic Affiliate Network Help" //$(this).attr("name");   
    if($(this).attr("id").indexOf("advertiser") > -1){
    	var hdrMenu =  '<ul class="helpMenuNav" id="advertiserHelp">' +
                            '<li><a href="">Menu</a>' +
                                '<ul class="helpMenuSubNav">' +
                                    '<li></li>' +
                                    '<li><a href="" name="helpIntroduction">Introduction</a></li>' +
                                    '<li><a href="" name="helpCustomize">Customizing Your Dashboard</a></li>' +
                                    '<li><a href="" name="helpManagePub">Manage Publishers</a></li>' +
                                    '<li><a href="" name="helpManageLinks">Managing Links and Banners</a></li>' +
                                    '<li><a href="" name="helpCheckNetMsg">Checking Network Messages</a></li>' +
                                    '<li><a href="" name="helpRunReports">Running Reports</a></li>' +
                                    '<li><a href="" name="helpSettings">Settings</a></li>' +
                                    '<li><a href="mailto:help@network.atrinsic.com" name="Contact">Contact us</a></li>' +
                                '</ul>' +
                            '</li>' +
                        '</ul>' 
    }else{
    	var hdrMenu =  '<ul class="helpMenuNav" id="publisherHelp">' +
                            '<li><a href="">Menu</a>' +
                                '<ul class="helpMenuSubNav">' +
                                    '<li></li>' +
                                    '<li><a href="" name="helpIntroduction">Introduction</a></li>' +
                                    '<li><a href="" name="helpCustomize">Customizing Your Dashboard</a></li>' +
                                    '<li><a href="" name="helpAdvertisers">Advertisers</a></li>' +
                                    '<li><a href="" name="helpRetrievingLinks">Retrieving Links and Banners</a></li>' +
                                    '<li><a href="" name="helpCheckNetMsg">Checking Network Messages</a></li>' +
                                    '<li><a href="" name="helpRunReports">Running Reports</a></li>' +
                                    '<li><a href="" name="helpSettings">Settings</a></li>' +
                                    '<li><a href="mailto:help@network.atrinsic.com" name="Contact">Contact us</a></li>' +
                                '</ul>' +
                            '</li>' +
                        '</ul>'         
    }
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
			$("#dashBoardSettingsDlg").html(data);	
			$("#dashBoardSettingsDlg").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               autosize:false,
			               open: function(event, ui) { 			                   
			                   $("#ui-dialog-title-dashBoardSettingsDlg").text(dialogHdr);
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
			                   $(".ui-dialog-titlebar-close span").remove();
			                   $(".ui-dialog-titlebar-close").addClass("newDialogMenuBtn");
			                   $(".ui-dialog-titlebar-close").text("Menu");	
			                   $(".ui-dialog-titlebar").append('<span style="float:right;">' +hdrMenu+'</span>')
			                   $(".ui-dialog-titlebar-close").remove();
		                   } 
		               });
            $("#dashBoardSettingsDlg").bind("dialogclose", function(event, ui) {
                $("#dashBoardSettingsDlg").dialog("destroy");
            });
			               
		},
        error:function (xhr, ajaxOptions, thrownError){
            alert("Status Code: " + xhr.status + ". Further error details should go here.");

        }    
	}); 			   
});



/*********************************** STATUS SECTION ***************************************/
$(".updateStatus").live("click", function(event){
	event.preventDefault();
	// Dimensions
	var dWidth = 600;
	var dHeight = 400;	
	
	var ajaxUrl = $(this).attr("id");		
	var dialogHdr = $(this).attr("name");		
	
	$.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
			$("#dashBoardSettingsDlg").html(data);			
			$("#dashBoardSettingsDlg").dialog({bgiframe:true, 
			               height:dHeight, 
			               width:dWidth, 
			               modal:true, 
			               draggable:false, 
			               resizable:false,
			               open: function(event, ui) { 			                   
			                   $("#ui-dialog-title-dashBoardSettingsDlg").text(dialogHdr);
			                   $(".ui-dialog-titlebar").addClass("ui-widget-header-forDialog");
			                   $(".ui-dialog-titlebar-close span").remove();
			                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
			                   $(".ui-dialog-titlebar-close").text("Close");			                   
		                   } 
		               });
            $("#dashBoardSettingsDlg").bind("dialogclose", function(event, ui) {
                $("#dashBoardSettingsDlg").dialog("destroy");
            });
			               
		},
        error:function (xhr, ajaxOptions, thrownError){
            alert("Status Code: " + xhr.status + ". Further error details should go here.");      

        }    
	}); 			   
});

$(".deleteStatus").live("click", function(event){
    event.preventDefault();
    var ajaxUrl = $(this).attr("id");
    var obj = $(this);
   $.ajax({    		
		type: "GET",
		url: ajaxUrl,
		dataType: "html",
		async: true,
		success: function(data){
		    obj.parent().parent().remove(); 
		}
		    
		}); 
});