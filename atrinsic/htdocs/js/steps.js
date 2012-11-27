function populate_inner(step){
	selected = new Array();
	for (var i=1;i<=2;i++)
	{
		if (i== 1){
			inputs=$("#step"+step+" .input_val ul li label").children();
		} else if (i = 2){
			inputs=$("#step"+step+" .input_val").children();
		}
	
		if (inputs){
			inputs.each(function(x){
				if (this.type == "select-one" ||this.type == "select-multiple"){
					var var_label = " "+$(this).parent().siblings("label:first").text()
					if ($.trim(var_label) != ""){
						var_label +=": ";
					}
					var var_content = "";
					for (var i = 0; i < this.options.length; i++){
						if (this.options[ i ].selected){
							var_content += ", "+this.options[ i ].text;
						}else if(this.id == "vertical_results"){
							var_content += ", "+this.options[ i ].text;
						}
					}
					if ($.trim(var_content) != ""){
						selected.push(var_label + var_content);	
					}
				}else if(this.type == "text"){
					if($.trim($(this).val()) != "" && $(this).val() != "undefined" && $(this).val() != "NaN"){
						var var_label = $(this).parent().siblings("label:first").text();
						var var_content = "";
						if ($.trim(var_label) != ""){
							var_content = var_label + ": ";
						}
						selected.push(" "+var_content+$(this).val().toString());	
					}
				}else if(this.type == "radio"){
					if(this.checked){
						var var_label = $(this).parent().parents(".input_val").prev().text();
						var var_content = $(this).parents("label").text();
						var_label = var_label + ": ";
						selected.push(var_label + var_content);					
					}
				}
			});	
		}
	}
	var x = selected.toString();
	x = x.replace(/, /g,"<br>");
	$("#inner"+step).html("<p>"+x+"</p>");
	if($.trim($("#inner"+step).text()) != ""){
		$("#reportbox"+step).show();
	}
}
function populate_all_inners(){
	amount_of_steps = $(".step").length;
	for (i=1;i<=amount_of_steps;i++){
		populate_inner(i);
	}	
}
function show_populated(){
	$(".inner").each(function(){
		if($.trim($(this).text()) != ""){
			$(this).parent().show();
		}	
	});
}
var stepping_active = false;
function move_to_step(step, current_step){
	if (stepping_active == false){
		stepping_active = true;
		var amount_steps = $(".step").length;
		$(".step").hide();
		//$(".stepholder").show();
		$("#step"+current_step).show();
		//$("#holder_step"+current_step).hide();
		// delete this line to put back the acordeon
		stepping_active = false;
		
		populate_inner(current_step);
		$(".step").hide();
		$("#step"+step).show();
		/*
		$("#step"+current_step).hide('slide',{},500, 
			function(){$("#holder_step"+current_step).show('slide',{},250, 
				function(){$("#holder_step"+step).hide('slide',{},250, 
					function(){
						$(".step_wrapper").width($("#step"+step).width()+365);
						
						$("#step"+step).show('slide',{},500, function(){
						$(".step").hide();
						$("#step"+step).show();
						$(".stepholder").show();
						$("#holder_step"+step).hide();
						stepping_active = false;
						
					})
				})
			})
		});*/
		//$("#holder_step"+step).hide('slide',{},500, function(){$("#step"+step).show('slide',{},500)});
		if(step == 1){
			$("#previous_step").hide();
			$("#next_step").show();
		}else if(step == amount_steps){
			$("#previous_step").show();
			$("#next_step").hide();
		}else{
			$("#previous_step").show();
			$("#next_step").show();
		}
	}
	return false;
}
function init_stepper(){
	$(".reportbox").hide();
	var amount_steps = $(".step").length;
	var current_step=1
	//$("#step_header").html($("#heading"+current_step).val());
	$("#step"+current_step).show();
	$("#holder_step"+current_step).hide();
	// delete this line to put back the acordeon
	$("#previous_step").hide();
	populate_inner(current_step);
	$(".step_wrapper").width($("#step"+current_step).width()+365);
	$(".stepholder").hide();// to removed to add accordeon
	$("#next_step, .next_btn").click(function(){
		var current_step = parseInt($(".step:visible").attr("id").substring(4));
		var next_step = current_step + 1;
		if (next_step <= amount_steps){
			move_to_step(next_step, current_step)
		}
	});
	$("#previous_step").click(function(){
		var current_step = $(".step:visible").attr("id").substring(4);
		var previous_step = current_step - 1;
		if (previous_step >= 1){
			move_to_step(previous_step, current_step)
		}
	});
	$(".edit_button").click(function(){
		var step = $(this).attr("id").substring(4);
		var current_step = $(".step:visible").attr("id").substring(4);
		move_to_step(step, current_step);
		return false;
	});
	$(".stepholder").click(function(){
		var step = $(this).attr("id").substring(11);
		var current_step = $(".step:visible").attr("id").substring(4);
		move_to_step(step, current_step);
		return false;
	});
	
	$(".input_val select, .input_val input, .input_val radio").change(function(){
		var step_id = parseInt($(".step:visible").attr("id").substring(4));		
		//$("#step_header").html($("#heading"+step_id).val());
		populate_inner(step_id);		
	});
	$("#reportbutton").click(function(){
		$("#report_form").submit();
		return false;
	});
}