function initMessages(){ 	
    $(".deleteAllMsgs").live("click", function(event){
        event.preventDefault();
        $('#deleteMsgForm').submit(); 
    });
}
function initComposeReplyFormManipulation(){
    $("#id_message").css("height", "300px");
}
function initCampaigns(){
    $('.emailView').click(function(event) {	
        event.preventDefault();
        $('.emailBody').show();
        $('.emailHide').show();
        $(this).hide();
    });
    $('.emailHide').click(function(event) {	
        event.preventDefault();
       $('.emailBody').hide();
       $('.emailView').show();
       $(this).hide(); 
    });
    
    $('.htmlView').click(function(event) {	
        event.preventDefault();
        $('.htmlBody').show();
        $('.htmlHide').show();
        $(this).hide();
    });
    $('.htmlHide').click(function(event) {	
        event.preventDefault();
      $('.htmlBody').hide();
      $('.htmlView').show();
      $(this).hide();
      
    });
    $('.showAddCriteria').click(function(event) {	
        event.preventDefault();
        $('#add_criteria').dialog({bgiframe:true, 
				               height:350, 
				               width:560, 
				               modal:true, 
				               draggable:false, 
				               resizable:false,
				               title:'Add Criteria',
				               open: function(event, ui) { 
				                   $("#ui-dialog-title-addVertical").text("Add Criteria"); 
				                   $("#ui-dialog-title-addVertical").addClass("modifyDialogTitle");
				                   $(".ui-dialog-titlebar-close span").remove();
				                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
				                   $(".ui-dialog-titlebar-close").text("Close");
			                   } 
			               });
      
    });
    

    $('.updateFilters').click(function(event) {	
        event.preventDefault(); 
        if($(this).attr("name") == "Verticals"){
            $dialogCtn = $("#addVertical")
            strHeader = "Verticals"
        }else if($(this).attr("name") == "Terms"){
            $dialogCtn = $("#addTerm")
            strHeader = "Program Terms"
        }else if($(this).attr("name") == "Groups"){
            $dialogCtn = $("#addGroup")
            strHeader = "Groups"
        }else if($(this).attr("name") == "Methods"){
            $dialogCtn = $("#addMethod")
            strHeader = "Methods"
        }
        $dialogCtn.dialog({bgiframe:true, 
				               height:350, 
				               width:560, 
				               modal:true, 
				               draggable:false, 
				               resizable:false,
				               open: function(event, ui) { 
				                   $("#ui-dialog-title-addVertical").text("Verticals"); 
				                   $("#ui-dialog-title-addVertical").addClass("modifyDialogTitle");
				                   $(".ui-dialog-titlebar-close span").remove();
				                   $(".ui-dialog-titlebar-close").addClass("newDialogCloseBtn");
				                   $(".ui-dialog-titlebar-close").text("Close");
			                   } 
			               });
        $("#addVertical").bind("dialogclose", function(event, ui) {
            $("#addVertical").dialog("destroy");
        });
        refreshAllVerticals();
        
    });
    $('.updateProgram').click(function(event) {	
        event.preventDefault();    
        $(this).parents("td").html($("#addTerm").html())
        $(this).hide();      
    });
    $('.updatePubGroup').click(function(event) {	
        event.preventDefault();    
        $(this).parents("td").html($("#addGroup").html())
        $(this).hide();      
    });
    $('.updatePromoMethod').click(function(event) {	
        event.preventDefault();    
        $(this).parents("td").html($("#addMethod").html())
        $(this).hide();      
    });
    //---------------- Update Verticals -------------------//
    function refreshAllVerticals(){
        $("#availableDisplay_Verts option").remove();
        $("#availableDisplay_Verts").append('<option value="-9999">Select...</option')                         
        $activeOptions = $("#activeDisplay_Verts option")
        $options = $("#selAllVerticals option");        
        $options.each(function(){
            addMe = true
            $curVert = $(this)
            $activeOptions.each(function(){
                if($curVert.val() == $(this).val()){
                    addMe = false
                }
            });
            if(addMe){
                $("#availableDisplay_Verts").append('<option value="' + $curVert.val() + '">' + $curVert.html() + '</option>')    	
            }
        });    	
        
        $("#availableDisplay_Terms option").remove();
        $("#availableDisplay_Terms").append('<option value="-9999">Select...</option')                         
        $activeOptions = $("#activeDisplay_Terms option")
        $options = $("#selAllTerms option");        
        $options.each(function(){
            addMe = true
            $curVert = $(this)
            $activeOptions.each(function(){
                if($curVert.val() == $(this).val()){
                    addMe = false
                }
            });
            if(addMe){
                $("#availableDisplay_Terms").append('<option value="' + $curVert.val() + '">' + $curVert.html() + '</option>')    	
            }
        });    	
        $("#availableDisplay_Groups option").remove();
        $("#availableDisplay_Groups").append('<option value="-9999">Select...</option')                         
        $activeOptions = $("#activeDisplay_Groups option")
        $options = $("#selAllGroups option");        
        $options.each(function(){
            addMe = true
            $curVert = $(this)
            $activeOptions.each(function(){
                if($curVert.val() == $(this).val()){
                    addMe = false
                }
            });
            if(addMe){
                $("#availableDisplay_Groups").append('<option value="' + $curVert.val() + '">' + $curVert.html() + '</option>')    	
            }
        });    	
        $("#availableDisplay_Methods option").remove();
        $("#availableDisplay_Methods").append('<option value="-9999">Select...</option')                         
        $activeOptions = $("#activeDisplay_Methods option")
        $options = $("#selAllMethods option");        
        $options.each(function(){
            addMe = true
            $curVert = $(this)
            $activeOptions.each(function(){
                if($curVert.val() == $(this).val()){
                    addMe = false
                }
            });
            if(addMe){
                $("#availableDisplay_Methods").append('<option value="' + $curVert.val() + '">' + $curVert.html() + '</option>')    	
            }
        });    	
    }

    $('.addFilterToList').click(function(event) {	
        event.preventDefault(); 
        typeSelector = $(this).attr("name")
        $options = $("#availableDisplay_"+typeSelector+" option")
    	$options.each(function(){
    		if ( this.selected ){
    		    if ( this.value != -9999 ){          		        
    		        $("#activeDisplay_"+typeSelector).append('<option value="' + this.value + '">' + this.text +'</option>');    		                $("#active_"+typeSelector).append('<option value="' + this.value + '">' + this.text +'</option>');
        		    $(this).remove();
        		}
    		}
    	});    	
        
    });    
    function removeFromMultiSel(typeSelector){        
        $activeOptions = $("#activeDisplay_"+typeSelector+" option")
	    $Options = $("#active_"+typeSelector+" option")
    	$activeOptions.each(function(){
    		if ( this.selected ){
    		    $curSelection = $(this)
    	        $Options.each(function(){
    	            if($(this).val() == $curSelection.val())
    	                $(this).remove();
    	        });
    		    $(this).remove();        		
    		}
    	});
        refreshAllVerticals();        
    }
    $('.remFilterFromList').click(function(event) {	
        event.preventDefault();      
        typeSelector = $(this).attr("name")
        removeFromMultiSel(typeSelector)
        
    });
    
    
    $('.updateBtn').click(function(event) {	
        typeSelector = $(this).attr("name")
        $activeHidden = $("#active_"+typeSelector+" option")
        $activeOptions = $("#activeDisplay_"+typeSelector+" option")
        $activeOptions.each(function(){
            //$(this).attr('selected', 'selected');
            $currentActive = $(this)
            $activeHidden.each(function(){
                if($(this).val() == $currentActive.val()){
                    $(this).attr('selected', 'selected');
                }
            });
        });
        $("#frmAddActive_"+typeSelector).submit();
    });
    //---------------- END Update Verticals -------------------//
    
    
}

$(".viewThenReply").live("click", function(event){
    event.preventDefault();
    $("#ajaxLightbox").dialog("destroy");
    var thisId = $(this).attr("id")
    //$("#" + thisId).click();
    
    $('.primaryDisplayTable tbody tr').each( function() {
            if(thisId == $(this).children(".Action").children("a[name='Reply']").attr("id")){
                $(this).children(".Action").children("a[name='Reply']").click();
            }
        });
        
});