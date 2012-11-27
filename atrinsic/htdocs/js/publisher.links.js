// Global Objects used for Publisher Links Search

// JSON Objects that contain element properties that need to be added to page.
// This is due to the fact that our form elements are of a multiple select type, and we need
// a regular select for functionality purposes.
selVertical = eval({ originalFormElementID:'#id_vertical', 
                     displayName:'Vertical', 
                     newSelectBoxID: '#selectbox_vertical', 
                     chosenCriteriaCtn:'#srchByVertical',
                     attrName: 'selectbox_vertical' })
                                     
selPromotion = eval({ originalFormElementID:'#id_link_promotion_type', 
                      displayName:'Promotion', 
                      newSelectBoxID: '#selectbox_promotion', 
                      chosenCriteriaCtn:'#srchByPromotion',
                      attrName: 'selectbox_promotion'})
allElements = eval({'selectbox_vertical':selVertical, 
                    'selectbox_promotion': selPromotion }); 
                     

/********** Bind Search Form **********/

    function ajaxLoading(){   
    	$(".contentCtn .ajaxLoading").height($(".contentCtn").height());
    	$(".contentCtn .ajaxLoading").width($(".contentCtn").width());
    	$(".contentCtn .ajaxLoading").show();
    }
    function hideAjaxLoading(){
        $(".contentCtn .ajaxLoading").hide();
    }
    var options1 = {
        	target:        '#dynamicResults',   // target element to update
        	success:       showResponse  // post-submit callback
    };
    
    $('#pubLinksSearchForm').bind('submit', function() {
        ajaxLoading();
    	$(this).ajaxSubmit(options1);
    	return false; // <-- important!
    });
    
    function showResponse(responseText, statusText)  { 
        hideAjaxLoading(); 
    	$("#dynamicResults").show();
        return true;
    } 

/********** END Bind Search Form **********/

function appendOptionsToSelectBox(selBox){
    $(selBox.newSelectBoxID + " option").remove();
    $(selBox.newSelectBoxID).append('<option value="-9999">Click to Select '+selBox.displayName+'</option')            
    $options = $(selBox.originalFormElementID +" option");
    $options.each(function(){
        $(selBox.newSelectBoxID).append('<option value="' + $(this).val() + '">' + $(this).html() + '</option>')
    });    	
}
function refreshSelectBoxes(Selector){
    // If Selector is null, then reload entire contents of Select Boxes
    if(Selector == null) { 
        for (elemObject in allElements){       
           appendOptionsToSelectBox(allElements[elemObject])
      }
    }else{
        appendOptionsToSelectBox(allElements[Selector])
    }   
     
}
function checkHiddenMultis(){    
    bolSubmit = false;    
    for (elemObject in allElements){  
        $options = $(allElements[elemObject].originalFormElementID + " option");				
        $options.each(function(){
            if($(this).attr("selected")){   
                bolSubmit = true;                
            }        
    	});    	
    }
    if(!bolSubmit){
        $("#dynamicResults").hide();
    }else{
        $("#pubLinksSearchForm").ajaxSubmit(options1);            
    }
    
}
function initSelectBoxChangeEvs(){
    $(".FindBy").change(function () {    
        currentSelectBoxID = $(this).attr("id");
        
        if($(allElements[currentSelectBoxID].chosenCriteriaCtn).children(".srchCriteriaChosen").length == 0){
            $(allElements[currentSelectBoxID].chosenCriteriaCtn).show();  
        }
    		
        // Get Options from Current viewable Select Box based on ID and predefined Object(s)    
        $options = $(allElements[currentSelectBoxID].newSelectBoxID + " option")
    	$options.each(function(){
    		if ( this.selected ){
    			if ($(this).val() != -9999){
    			    selectedOptionID = $(this).val();
    			    // Add selection to our SelectBoxes' searchCriteria Container
    			    $(allElements[currentSelectBoxID].chosenCriteriaCtn).append('<div class="srchCriteriaChosen" id="' + $(this).val() + '"><a href="" name="' + allElements[currentSelectBoxID].attrName + '">Remove</a>' + $(this).html() + '</div>')
    				selectedID = $(this).val();				
    			    // Remove from viewable Select Box
    				$(this).remove();
    			}
    		}
    	});    
    	
    	// Mark our selection from viewable select box, as "selected" in our Hidden Multiple Select Box
    	$options = $(allElements[$(this).attr("id")].originalFormElementID + " option");			
    	$options.each(function(){
    		if ( this.value == selectedOptionID ){
    			$(this).attr("selected","selected");
    		}			
    	});
        // Unbind all "Remove" links and re-bind. 
        // NOTE: Live bind does not work for us in this case.
    	$('.srchCriteriaChosen a').unbind('click');	
    	$(".srchCriteriaChosen a").bind("click", function(event){
            event.preventDefault();
            currentSelectBox = allElements[$(this).attr("name")].newSelectBoxID
            refreshSelectBoxes($(this).attr("name"))        
            removeThisID = $(this).parent().attr("id");
            
            // Unselect from our Hidden Multiple Select Box
    		$options = $(allElements[$(this).attr("name")].originalFormElementID + " option");		
    		$options.each(function(){
    			if ( this.value == removeThisID ){
    				$(this).attr("selected","");
    			}			
    		});
    		$(this).parent().remove();
            
    		// Since we refreshed the entire contents of our viewable SelectBox, we must now remove
    		// all options (from the selectbox) that have already been added.    		
    		$options = $(currentSelectBox + " option")
    		$currentCriteria = $(allElements[$(this).attr("name")].chosenCriteriaCtn).children(".srchCriteriaChosen")		
            $currentCriteria.each(function(){
                criteriaID = $(this).attr("id")
                $options.each(function(){
        			if ( this.value == criteriaID ){
        				$(this).remove();
        			}			
        		});
    		});
    		
                		
            if($(allElements[$(this).attr("name")].chosenCriteriaCtn).children(".srchCriteriaChosen").length == 0){
                $(allElements[$(this).attr("name")].chosenCriteriaCtn).hide();  
            }else{
    		    $("#pubLinksSearchForm").ajaxSubmit(options1);
    		}
    		
    		// Check both Hidden Multiple Select Boxes for any remaining selected values
    		checkHiddenMultis();
        });
        $("#pubLinksSearchForm").ajaxSubmit(options1);
    });
}

function initPublisherLinks(){    
    $("legend").remove();
    $("#dynamicSearchForm").append('<div class="clearfix"></div>'); 
    // On page load, reload entire contents of both Select Boxes
    refreshSelectBoxes(null);  
    
    for (elemObject in allElements){       
        bolSubmit = false;
        $options = $(allElements[elemObject].originalFormElementID + " option");				
        $options.each(function(){
            if($(this).attr("selected")){
                $(allElements[elemObject].chosenCriteriaCtn).append('<div class="srchCriteriaChosen" id="' + $(this).val() + '"><a href="" name="' + allElements[elemObject].attrName + '">Remove</a>' + $(this).html() + '</div>')     
                bolSubmit = true;
                
            }        
    	});
    	if(bolSubmit){
            $(allElements[elemObject].chosenCriteriaCtn).show();
            $("#dynamicResults").show();
            $("#pubLinksSearchForm").ajaxSubmit(options1);
        }else{
            $("#dynamicResults").hide();
        }
    }
    /***************************************************************************/
    /*************** Initialize both Selext Box change events ******************/
    initSelectBoxChangeEvs();
    /***************************************************************************/      
}

/*************************** Ajax Initialization Functions ***************************/
function initGetLinks(){

    function ajaxLoading(){        
		$(".contentCtn .profileView .ajaxLoading").height($(".ajaxLoading").parents(".contentCtn .profileView").height());
		$(".contentCtn .profileView .ajaxLoading").width($(".ajaxLoading").parents(".contentCtn .profileView").width());
		$(".contentCtn .profileView .ajaxLoading").show();
    }
    function hideAjaxLoading(){
        $(".contentCtn .profileView .ajaxLoading").hide();
    }
	$(".getLink").live("click", function(event){
	    event.preventDefault();
		// Default Dimensions
		dWidth = 600;
		dHeight = 550;
		//alert("getLink")
		var ajaxUrl = $(this).attr("id");		
		var dialogHdr = $(this).attr("name");		
		ajaxLoading();
		
    	$.ajax({    		
			type: "GET",
			url: ajaxUrl,
			dataType: "html",
			async: true,
			success: function(data){
			    hideAjaxLoading();
				$("#ajaxLightbox").html(data);			
				$("#ajaxLightbox").dialog({bgiframe:true, 
				               height:250, 
				               width:550, 
				               modal:false, 
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
                    $("#ajaxLightbox").dialog("destroy");
                });
				               
			},
            error:function (xhr, ajaxOptions, thrownError){
                alert("Status Code: " + xhr.status + ". Further error details should go here.");                                
			    hideAjaxLoading();
            }    
		}); 		
	});	
}	
