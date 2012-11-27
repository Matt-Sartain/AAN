function hideZones(){
	$('.widget_holder').each(function(){
		if ($(this).children().length == 0){
			$(this).hide();
			if ($(this).parent().children().length==1){
				$(this).parent().hide();
			}
		}
		
	});
	$('.input_val').children().children().children().children().click(function(){
		do_filter(this);
		
	});
	$('#id_advertiser_category,#id_specific_advertiser,#id_report_type,#id_start_date,#id_end_date,#id_run_reporting_by_group,#id_run_reporting_by_vertical,#id_run_reporting_by_publisher').change(function(){
		do_filter(this);
	});
	$(".downloadCSV").live("click",function(event) {
		event.preventDefault();
		$("#target").val("0");
		$('#download_types').dialog("destroy");
		$("#report_form").submit();
		$("#target").val("");
    });

    $(".downloadXLS").live("click",function(event) {
		event.preventDefault();
		$("#target").val("2");
		$('#download_types').dialog("destroy");
		$("#report_form").submit();
		$("#target").val("");
    });
    $(".downloadTAB").live("click",function(event) {
		event.preventDefault();
		$("#target").val("1");
		$('#download_types').dialog("destroy");
		$("#report_form").submit();
		$("#target").val("");
    });
	$('.report_edit_btn').click(function(event){
		event.preventDefault()
		val_to_focus_on = $(this).parent().siblings(".report_holder").text()
		inputs=$(".input_val").children();
		if (inputs){
			inputs.each(function(x){
				if ($(this).val() == val_to_focus_on){
					$(this).focus();
				}
				if (this.type == "select-one"){
					if (this.options[this.selectedIndex].text==val_to_focus_on){
						$(this).focus();
					}
				}
				if(this.type == "select-multiple"){
					var var_content = '';
					for (var i = 0; i < this.options.length; i++){
						if (this.options[ i ].selected){
							if(var_content == ""){
								var_content = this.options[ i ].text;
							}else{
								var_content += ", "+this.options[ i ].text;	
							}
						}
					}
					if (var_content == val_to_focus_on){
						$(this).focus();
					}
				}
			});
		}
	});
	$('.report_delete_btn').click(function(event){
		event.preventDefault()
		var val_to_focus_on = $(this).parent().siblings(".report_holder").text()
		var inputs = $(".input_val").children();
		var x_btn = $(this);
		$(this).parent().siblings('.report_holder').text();
		$(this).parent().parent().hide();
		var radio_btns = $(".input_val").children().children().children();
		if (radio_btns){
			radio_btns.each(function(x){
				if($(this).parent().text() == val_to_focus_on){
					$(this).css("color","#000000");
					this.selected=false;	
				}
			});
		}
		if (inputs){
			inputs.each(function(x){
				if ($(this).val() == val_to_focus_on){
					$(this).val('');
					//x_btn.parent().siblings('.report_holder').hide();
					x_btn.parent().siblings('.report_holder').text();
				}else if (this.type == "select-one"){
					if (this.options[this.selectedIndex].text==val_to_focus_on){
						this.selectedIndex = -1;
					}
				}else if(this.type == "select-multiple"){
					var var_content = '';
					for (var i = 0; i < this.options.length; i++){
						if (this.options[ i ].selected){
							if(var_content == ""){
								var_content = this.options[ i ].text;
							}else{
								var_content += ", "+this.options[ i ].text;	
							}
						}
					}
					if (var_content == val_to_focus_on){
						for (var i = 0; i < this.options.length; i++){
							this.options[i].selected = false;
						}
					}
				}
			});
		}
	});
}
function refilter(){
	$('#id_advertiser_category,input:radio,#id_specific_advertiser,#id_report_type,#id_start_date,#id_end_date').each(function(){
		do_filter(this,true);
	});
}
function do_filter(obj,is_refilter){	
	if (obj.type == "select-one" ||obj.type == "select-multiple"){
		var var_content = "";
		for (var i = 0; i < obj.options.length; i++){
			if (obj.options[ i ].selected){
				if(var_content == ""){
					var_content = obj.options[ i ].text;
				}else{
					var_content += ", "+obj.options[ i ].text;	
				}
			}
		}
	}else{
		var_content = $(obj).val();
	}
	if($(obj).attr("id")=='id_specific_advertiser' || $(obj).attr("id")=='id_advertiser_category'){
		if (var_content != ""){
			$("#advertiser_holder").text(var_content);
			$("#advertiser_holder").parent().show();		
		}
	}else if($(obj).attr("id")=='id_run_reporting_by_group' || $(obj).attr("id")=='id_run_reporting_by_vertical' || $(obj).attr("id")=='id_run_reporting_by_publisher'){
		if (var_content != ""){
			$("#publisher_holder").text(var_content);
			$("#publisher_holder").parent().show();
		}
	}else if($(obj).attr("id")=='id_report_type'){
		$("#report_type_holder").text(var_content);
		$("#report_type_holder").parent().show();	
	}else if($(obj).attr("id")=='id_start_date'){
		$("#start_date_holder").text(var_content);
		$("#start_date_holder").parent().show();	
	}else if($(obj).attr("id")=='id_end_date'){
		$("#end_date_holder").text(var_content);
		$("#end_date_holder").parent().show();	
	}else if($(obj).attr("id")=='id_group_by'){
		$("#group_by_holder").text(var_content);
		$("#group_by_holder").parent().show();	
	}
	$('.close_lb_button').bind('click', function(event) {
	    event.preventDefault();
        $(".hidden_diag_lb").dialog("destroy");
    });
    $("input:submit").click(function(event){
		event.preventDefault();
		$('.hidden_diag_lb').css('position','absolute')
		$('.hidden_diag_lb').css('left','-300px')
		$('.hidden_diag_lb').css('top','-300px')
		$('.hidden_diag_lb').show();
		$('#report_form').append($('.hidden_diag_lb'));
		$("#report_form").submit();
	});
	if (obj.type=='radio'){
		if(obj.checked){
			$(obj).parent().css("color","#6b8500");
			$(obj).parent().parent().siblings().children('label').css("color","#000000");
			var chosen_type =$(obj).parent().text();
			
			if ($.trim(chosen_type) == "Advertiser" || $.trim(chosen_type) == "Vertical" || $.trim(chosen_type) == "Group" || $.trim(chosen_type) == "Publishers"){
				if (!is_refilter){
				    $('#'+$.trim(chosen_type)).dialog({width:425, height:325 });
                    $('#'+$.trim(chosen_type)).bind('dialogclose', function(event, ui) {
		                $('#'+$.trim(chosen_type)).dialog("destroy");
	                });	
	                
			    }
			}else if ($.trim(chosen_type) == "All Advertisers"){
			    $(".hidden_diag_lb").dialog("destroy");
				document.getElementById('id_specific_advertiser').selectedIndex = -1;
				for (var i = 0; i < document.getElementById('id_advertiser_category').options.length; i++){
					document.getElementById('id_advertiser_category').options[ i ].selected = false;
				}
				$("#advertiser_holder").text($.trim(chosen_type));
				$("#advertiser_holder").parent().show();
			}else if ($.trim(chosen_type) == "All Publishers"){
				document.getElementById('id_run_reporting_by_publisher').selectedIndex = -1;
				for (var i = 0; i < document.getElementById('id_run_reporting_by_vertical').options.length; i++){
					document.getElementById('id_run_reporting_by_vertical').options[ i ].selected = false;
				}
				for (var i = 0; i < document.getElementById('id_run_reporting_by_group').options.length; i++){
					document.getElementById('id_run_reporting_by_group').options[ i ].selected = false;
				}
				$("#publisher_holder").text($.trim(chosen_type));
				$("#publisher_holder").parent().show();
				
			}else{
				$("#group_by_holder").text($.trim(chosen_type));
				$("#group_by_holder").parent().show();
			}
		}
	}
}