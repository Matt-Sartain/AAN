function getCompetitors(){
     
campid = $('#id_campaigns').val();

url = 'competitors/'+campid+'/';
ajaxGet(url,$("#id_competitor"));

url = 'keywordgroups/'+campid+'/';
ajaxGet(url,$("#id_keyword_groups"));
    
}

function ajaxGet(url,dropdown){

    $.ajax({	
			type: "GET",
			url:  url,
			dataType: "text",
			async: true,
			success: function(data){
			    
			    var jsonObject = eval( "(" + data + ")" );
			    
				dropdown.find('option').remove().end();
                dropdown.dropdownchecklist("destroy");
                
                $.each(jsonObject, function(val, text) {
                    dropdown.append(
                        $('<option></option>').val(val).html(text)
                    );
                });
                
                dropdown.dropdownchecklist({firstItemChecksAll: true, maxDropHeight: 100,width:300});
			}
		});
}

function getKeywords(){
	idlist = "";
	campid = $('#id_campaigns').val();
	
	$(":checkbox").each(function () {
	
		elementid = this.id;

		if(elementid.search("id_keyword_groups") >= 0){
			if($(this).is(':checked')){
			
				value=$(this).val();
				if(value != 0){
					idlist+= (value.substring(0,value.indexOf('|')) + ",")
				}
					
			}
		}	
		
	});
	
	idlist = idlist.slice(0,idlist.length-1);
	if(idlist == ""){
		alert("Please Select Keyword Groups.");
	}else{
		
		if($("#lastKeywords").val() != idlist){
			
			$("#getKeywords").toggle();
			$("#ajaxLoader").toggle();
			
			dropdown = $("#id_keywords");
			dropdown.find('option').remove().end();
	        dropdown.dropdownchecklist("destroy");
			$("#lastKeywords").val(idlist);
			
			url = "keywords/";
			postData = {'idlist':$("#lastKeywords").val(),'campaign':$('#id_campaigns').val()}
			rawData = ajaxPost(url,postData);
		
			var allOptionsArray = rawData.split("\n");
	
		    dropdown.append($('<option></option>').val('0').html('(all)'));
			for (var i in allOptionsArray) {
		 		dropdown.append($('<option></option>').val(allOptionsArray[i]).html(allOptionsArray[i]));
			}
			
			
			dropdown.dropdownchecklist({firstItemChecksAll: true, maxDropHeight: 100, width:250});
			//$("#keywords").children().click(function() {getKeywords();});
			$("#ajaxLoader").toggle();
			$("#keywordlist").toggle();
			
			
		}else{
			$("#getKeywords").toggle();
			$("#keywordlist").toggle();
		}
	}
	
	
}

function ajaxPost(url,data){
	returnVal = ""

    $.ajax({	
			type: "POST",
			url:  url,
			dataType: "text",
			data: data,
			async: false,
			success: function(data){
			    returnVal = data;
			}
		});
		
		return returnVal;
}

function kwChange(){
	if($("#keywordlist").is(":visible")){
		$("#keywordlist").hide();	
	}
		
	if($("#getKeywords").not(":visible")){
		$("#getKeywords").show();	
	}
}

var allFields = ['start_date','end_date','competitors','keyword_groups','keywords','ad_offer_type','time_period','listing','exclude_tracking_urls'];

// Report Specs {fieldName:required}
var rank = {"start_date" : 1,"end_date" : 1,"competitors" : 0,"keyword_groups" : 0,"keywords" : 0};
var market_share = {"start_date" : 1,"end_date" : 1,"competitors" : 0,"keyword_groups" : 0};
var day_part = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"time_period" : 1};
var copy_changes = {"start_date" : 1,"end_date" : 1,"keyword_groups" : 0,"keywords" : 0};
var copy_details = {"ad_offer_type" : 0,"competitors" : 1,"keyword_groups" : 1,"keywords" : 1,"time_period" : 1};
var keyword = {"start_date" : 1,"end_date" : 1,"competitors" : 0,"keyword_groups" : 0,"keywords" : 0};
var keyword_details = {"start_date" : 1,"end_date" : 1,"competitors" : 1,"keyword_groups" : 0,"keywords" : 0};
var offer_keywords = {"keyword_groups" : 0,"keywords" : 0,"time_period" : 1};
var offer_advertisers = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"time_period" : 1};
var listing = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"listing" : 0,"start_date" : 1};
var listing_details = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"listing" : 0,"start_date" : 1};
var trademark = {"start_date" : 1,"end_date" : 1};
var trademark_details = {"start_date" : 1,"end_date" : 1};
var url_highjacks = {"start_date" : 1,"end_date" : 1};
var url_highjacks_details = {"start_date" : 1,"end_date" : 1,"keyword_groups" : 0};
var affiliate = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"start_date" : 1,"end_date" : 1,"exclude_tracking_urls" : 1};
var affiliate_details = {"competitors" : 0,"keyword_groups" : 0,"keywords" : 0,"start_date" : 1,"end_date" : 1,"exclude_tracking_urls" : 1};

function reportChange(typeName){

	var specs = eval(typeName) 
	// Hide or show fields
	$("#validation").hide();
	for(var i in allFields) {
		var field = $("#" + allFields[i]);
		var formField  = $("#id_" + allFields[i]);
		if(allFields[i] in specs){

			//show field if its not
			if(field.not(":visible")){
			    formField.removeAttr("disabled"); 
				field.show();	
			}
			
			// add css if required
			if(specs[allFields[i]] == 1){
				if(!(field.hasClass('req'))){
					field.addClass('req');
				}
			}else{
				if(field.hasClass('req')){
					field.removeClass('req');
				}
			}
			
		}else{

			//hide field if its currently displayed
			if(field.is(":visible")){
			    formField.attr("disabled", true); 
				field.hide();
			}
		}
		
	}	
	
	
} 



function validation(){
	var valid = true
	var report = $("#id_reportType").val();
	var specs = eval(report);
	var msg = "";
	
	for(var i in specs){

		if(specs[i] == 1){

			var elem = $("#id_" + i);
			if(elem.val()=='' || elem.val()==0 || elem.val()== null){
				valid = false;
				msg += ("<li>" + i + " is required</li>") 
			}
		}
		
	}
	
	if (!(valid)){
		var validationHtml = "Validation results<ul>" + msg + "</ul>"
	}
	
	$("#validation").html(validationHtml);
	return valid;
}

