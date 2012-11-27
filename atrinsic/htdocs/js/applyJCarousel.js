function applyJCarousel(){
	var $fieldSet = $("#mycarousel");
	var chldCount = $fieldSet.children().size();
	var resPerPane = 8;
	var numPanes = Math.ceil(chldCount / resPerPane)
	// Wrap First Pane
	var $kids = $fieldSet.children(":lt(" + resPerPane + ")")
	$kids.wrapAll(document.createElement("li"));
	
	// Wrap all remaining panes, in groups of $resPerPane
	var lt, gt;
	for(x=0;x <= numPanes - 2; x++)
	{
		lt = resPerPane + x+1;	
		gt = x;
		$kids = $fieldSet.children(":lt(" + lt + "):gt(" + gt + ")");
		$kids.wrapAll(document.createElement("li"));				
	}
	if(chldCount > 0){
		jQuery('#mycarousel').jcarousel({
	    	start: 1,
	    	offset: 1,
	        scroll: 1,
	        visible: true
	    });
	    
	}else{
		$("#mycarousel").html("<div class='noResults'>Your search returned 0 results.</div>")
	}
}