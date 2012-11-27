var replaceMsgHolder = "CONFIRM_MSG"
var confirmationBox = '<div id="confirmLightBox">' +
                          '<div class="contentCtn">' +
                              '<div class="confirmMessage">' + replaceMsgHolder + '</div>' +
                              '<div class="confirmActions">' +
                                  '<a href="" class="yesBtnBlueBG"></a>' +
                                  '<a href="" class="noBtnBlueBG"></a>' +
                              '</div>' +
                          '</div>' +
                      '</div>';
                  
function initConfirmationBox(strConfirmText){
    confirmationBox = confirmationBox.replace(replaceMsgHolder, strConfirmText)
    $(".contentCtn").append(confirmationBox)
    $(".confirmDelete, .confirmExpire").click( function(event) {
        event.preventDefault();
        var deleteLink = $(this).attr("id");
		var dialogHdr = $(this).attr("name");
		var confirmDialog = $("#confirmLightBox").clone();
        confirmDialog.dialog({bgiframe: true,
                                     height: 173, 
                                     width: 800,
                                     modal: true,
                                     draggable: false,
                                     resizable: false, 
                                     open: function(event, ui) {
                                         $("#ui-dialog-title-confirmLightBox").text(dialogHdr); 
                                         $("#ui-dialog-title-confirmLightBox").addClass("modifyDialogTitle"); 
                                     }
});
        $(".noBtnBlueBG").click(function(event){
            event.preventDefault();
            confirmDialog.dialog("destroy");            
        }); 
         
        $(".yesBtnBlueBG").click(function(event){
            event.preventDefault();
            window.location = deleteLink;     
         });
         
        return false;
    });
}
