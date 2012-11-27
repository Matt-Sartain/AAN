function initSearchFormManipulation() {  
    // Move the Date_to field to same line as Date_from and add "and" between
    $("#id_date_to").parent().insertAfter($("#id_date_from").parent());
    $("#id_date_from").parent().append("and");
    // Remove Empty Line that remains.
    $("#id_vertical").parent().parent().prev().remove();
    $(".clearBtn").insertAfter($("#id_vertical").parent());
    $(".filterBtn").insertAfter($("#id_vertical").parent());
    $("#id_date_to, #id_date_from").datepicker({showOn: "both", clickInput:true, dateFormat: "mm/dd/yy", buttonImage: "/images/blankdatepicker.png",buttonImageOnly: true});
}
   	
function initRecruitPublishers(){
    $(".recruitSelected").mouseover(function(){
        var link = "/advertiser/publishers/recruit/?publisher_id=";
        $("input[name='publisher_id_h']").each(function(){
            link += this.value + "&publisher_id=";
        });
        link = link.substring(0, link.lastIndexOf("&publisher_id="), 0);
        $(".recruitSelected").attr('id', link);
    });  
    $("input:checkbox").click(function(event) {
        if(this.checked){
            $("#All_pub_ID").append('<input type="hidden" name="publisher_id_h" value="'+this.value+'" id="o_'+this.value+'_h"/>');
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
                $("#All_pub_ID").append('<input type="hidden" name="publisher_id_h" value="'+this.value+'" id="o_'+this.value+'_h"/>');
            }            
        });
    });
    
    //$(".recruitSelected").click(function(event) {
    //    event.preventDefault();
    //    bolContinue = false;
    //    var link = "/advertiser/publishers/recruit/?publisher_ids=";
    //    $("input:checkbox").each( function() {
    //        if(this.checked){
    //            bolContinue = true;
    //        }
    //    });
    //    if(bolContinue){
    //        $("input[name='publisher_id_h']").each(function(){
    //            link += this.value + ",";
    //        });
    //        alert(link);
    //        $("#checkbox_form").attr("action", link );
    //        $("#checkbox_form").submit();
    //    }
    //});        
} 
function initMyPublishers(){
    $(".expirePublisher").click( function(event) {
        event.preventDefault();
        var expireLink = $(this).attr("id");
        $("#confirmLightBox").dialog({bgiframe: true,
                                     height: 200, 
                                     width: 800,
                                     modal: true,
                                     draggable: false,
                                     resizable: false, 
                                     open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); } 
        });
        
        $("#confirmLightBox").bind("dialogclose", function(event, ui) {
            $("#dialogLightBox").dialog("destroy");
        });	
        $(".noBtnBlueBG").click(function(event){
            event.preventDefault();
            $("#confirmLightBox").dialog("destroy");
            return false;
         });
         
        $(".yesBtnBlueBG").click(function(event){
            event.preventDefault();
            window.location = expireLink;
         });
        return false;
    });
    $(".expireSelected").click(function(event) {
        event.preventDefault();
        $("#checkbox_form").attr("action", "/advertiser/publishers/expire/");
        $("#checkbox_form").submit();
    });
}

function initPendingApplications(){
    $(".approveSelectedBtn").click( function(event) {
        event.preventDefault();
        $("#method").val("approve");
        $("#actionForm").submit();        
    });

    $(".declineSelectedBtn").click( function(event) {
        event.preventDefault();
        $("#method").val("deny");
        $("#actionForm").submit();        
    });
} 


function initGroups(){
     $(".deleteGroup").click( function(event) {
        event.preventDefault();
        var delLink = $(this).attr("id");
        $("#confirmLightBox").dialog({bgiframe: true,
                                     height: 200, 
                                     width: 800,
                                     modal: true,
                                     draggable: false,
                                     resizable: false, 
                                     open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); } 
        });
        
        $("#confirmLightBox").bind("dialogclose", function(event, ui) {
            $("#dialogLightBox").dialog("destroy");
        });	
        
        $(".noBtnBlueBG").click(function(event){
            event.preventDefault();
            $("#confirmLightBox").dialog("destroy");
            return false;
         });
         
        $(".yesBtnBlueBG").click(function(event){
            event.preventDefault();
            window.location = delLink;
         });
        return false;
    });

} 


function DataTableResults() {
    $(".dataTableSearchResults").dataTable({"bFilter":true,
                             "bLengthChange":true,
                             "bPaginate": true,
                             "sPaginationType": "full_numbers",
                             "iDisplayLength":25,        
                             "bAutoWidth": false,
                             "aoColumns" : [
                                { sWidth: "4%" },
                                { sWidth: "23%" },
                                { sWidth: "20%" },
                                { sWidth: "13%" },
                                { sWidth: "10%" },
                                { sWidth: "10%" },
                                { sWidth: "20%" }
                            ]                            
    });
    $(".dataTables_length").parent().removeClass("ui-widget-header");
    $(".dataTables_info").parent().removeClass("ui-widget-header");    
    
    $(".customDisabledPrevPage").css("background-image","url(/images/BL_prev.gif)");
    $(".customDisabledNextPage").css("background-image","url(/images/BL_next.gif)");
    $(".customNextPage").css("background-image","url(/images/BL_next_blue.gif)");
    
    $(".customPrevPage").css("background-image","url(/images/BL_prev_blue.gif)");
    $(".customPrevPage").css("width","77px");
    
    $(".paginate_active").parent().css("float","left");
    $(".dataTables_paginate").css("width","500px");
}


