$(".dialogLinks").live("click", function() {
	saveLinksList = $("#dialog").html();
	callURL = $(this).attr("href");		
	$.ajax({
		type: "GET",
		url: callURL,
		dataType: "html",
		success: function(data){
			$("#dialog").html(data);														
			bindViewLinkForm()
		}
	});
	return false;						
});
$("#goBack").live("click", function() {
	$("#dialog").html(saveLinksList);		
});
function bindViewLinkForm(){
	var optionsLink = {
		target:        '#dialog',   // target element to update
		beforeSubmit:  showReqDlg,  // pre-submit callback
		success:       showRespDlg  // post-submit callback
	};	
	$("#viewLinkForm").bind("submit", function() {
		$(this).ajaxSubmit(optionsLink);
		return false; // <-- important!
	});
}	
function showReqDlg(formData, jqForm, options) { 
	getLinksBack = $("#dialog").html();
    return true; 
} 
function showRespDlg(responseText, statusText)
{
	return true; 	
}