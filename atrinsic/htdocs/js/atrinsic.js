//functions we created a atrinsic-Moncton that dont fit anywheres else.
function init_tooltips(){
	
	
	$(".report_btns, .report_btns2").live("mouseover", function(){
		var position = $(this).position();
		if(!$(this).hasClass("inDialog"))
		{
			if ($(this).siblings(".report_action_tip2").children(".midStyle").children(".textgoeshere").length == 1){
				$(this).siblings(".report_action_tip2").children(".midStyle").children(".textgoeshere").text($(this).text());
				if($(this).hasClass("vertCategory")){		
					$(this).siblings(".report_action_tip2").css("left",position.left-65); // 80
					$(this).siblings(".report_action_tip2").css("top",position.top+60); // nothing				
				}else{
					$(this).siblings(".report_action_tip2").css("left",position.left-65); // 80
					$(this).siblings(".report_action_tip2").css("top",position.top); // nothing	
				}			
				$(this).siblings(".report_action_tip2").show();
			} else {
				if($(this).hasClass("chart_style_lines") || $(this).hasClass("download_it") || $(this).hasClass("lightbox_it")){
					$(this).siblings(".report_action_tip").text($(this).attr("name"));
				}else{
					$(this).siblings(".report_action_tip").text($(this).text());					
				}
				if($(this).hasClass("right")){
					$(this).siblings(".report_action_tip").css("left",position.left-40);
				}else{
					$(this).siblings(".report_action_tip").css("left",position.left);	
				}				
				$(this).siblings(".report_action_tip").css("top",position.top);
				$(this).siblings(".report_action_tip").show();
			}
		}
	});
	$(".action_buttons").live("mouseout", function(){
		$(".report_action_tip, .report_action_tip2, .tooltipab").hide();
	});
	
	$(".report_btns3").live("mouseover", function(){
		var position = $(this).position();
			$(".toolTipTextab").html($(this).text());
			$(this).siblings(".tooltipab").css("left",position.left);
			$(this).siblings(".tooltipab").css("top",position.top+25);
			$(this).siblings(".tooltipab").show();
	});
}

function DropDownController(from, to){
	for (var i=(from.options.length-1); i>=0; i--) { 
		if (from.options[i].selected) { 
			var option = new Option(from.options[i].text, from.options[i].value);
			if ($.browser.msie){
                to.add(option);
            }else{
                to.add(option, null);
            }
            from.options[i] = null;
            sortSelects(to);
		}
	}
	
}

function selectVerticles(){
	dropdown = $("#vertical_results")[0];
	for (var i=0; i < dropdown.options.length; i++) {
		dropdown.options[i].selected = true;
	}
	$("#vertical_results").attr("name","id_vertical");
	
}
function sortSelects(obj){
	var o = new Array();
	for (var i=0; i < obj.options.length; i++) {
		o[o.length] = new Option( obj.options[i].text, obj.options[i].value, obj.options[i].defaultSelected, obj.options[i].selected) ;
		}
	if (o.length==0) { return; }
	o = o.sort( 
		function(a,b) { 
			if ((a.text+"") < (b.text+"")) { return -1; }
			if ((a.text+"") > (b.text+"")) { return 1; }
			return 0;
			} 
		);	
	for (var i=0; i < o.length; i++) {
		obj.options[i] = new Option(o[i].text, o[i].value, o[i].defaultSelected, o[i].selected);
	}
}
function init_notifications(){
    $('#notifications_btn').click(function(event){
        event.preventDefault();
        $('#notifications').slideToggle("slow");
        
    });
    $('#notification_close').click(function(event){
        event.preventDefault();
        $('#notifications').slideUp("slow");
        
    });
    $('.notification_delete').click(function(event){
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
function State_Province_Toggle(country_field){
    if($(country_field).val() == 'US'){
        $(country_field).parent().parent().next().next().show();
        $(country_field).parent().parent().next().next().next().next().hide();
    }else if($(country_field).val() == 'CA'){
        $(country_field).parent().parent().next().next().hide();
        $(country_field).parent().parent().next().next().next().next().show();
    }    
}