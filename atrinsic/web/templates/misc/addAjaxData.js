function showResponse(responseText, statusText)  { } 
var opts = {
    target:        '#AjaxContent',
	success:       showResponse  // post-submit callback
};
$('form').bind('submit', function() {
	$(this).ajaxSubmit(opts);
	return false; // <-- important!
});	