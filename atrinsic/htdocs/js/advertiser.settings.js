function initFilterFormManipulation() {
    function hideFilterType(){
        value = $("select[name='field']").val();
        int_value = parseInt(value);
        if (int_value == '1') {
            $('#id_state').parent().parent().hide();
            $('#id_country').parent().parent().show();
            $('#id_value').parent().parent().hide();
            $('#id_publisher_vertical').parent().parent().hide();
            $('#id_promotion_method').parent().parent().hide();
        } else if (int_value == 2) {
            $('#id_state').parent().parent().show();
            $('#id_country').parent().parent().hide();
            $('#id_value').parent().parent().hide();
            $('#id_publisher_vertical').parent().parent().hide();
            $('#id_promotion_method').parent().parent().hide();
        } else if (int_value == 4) {
            $('#id_state').parent().parent().hide();
            $('#id_country').parent().parent().hide();
            $('#id_value').parent().parent().hide();
            $('#id_publisher_vertical').parent().parent().hide();
            $('#id_promotion_method').parent().parent().show();
        } else if (int_value == 6) {
            $('#id_state').parent().parent().hide();
            $('#id_country').parent().parent().hide();
            $('#id_value').parent().parent().hide();
            $('#id_promotion_method').parent().parent().hide();
            $('#id_publisher_vertical').parent().parent().show();
        } else {
            $('#id_state').parent().parent().hide();
            $('#id_country').parent().parent().hide();
            $('#id_promotion_method').parent().parent().hide();
            $('#id_publisher_vertical').parent().parent().hide();
            $('#id_value').parent().parent().show();
        }
    }
    hideFilterType();
    $("#id_field").bind("change", function(e){
    	hideFilterType();
    });
}

function initFeedFormManipulation(){    
	function hideCredentials() {
		value = $("select[name='datafeed_type']").val();
		int_value = parseInt(value);
		if (int_value == 2) {
		    $('#id_username').parent().parent().show();
		    $('#id_password').parent().parent().show();
		    $('#id_server').parent().parent().show();
		} else {
		    $('#id_username').parent().parent().hide();
		    $('#id_password').parent().parent().hide();
		    $('#id_server').parent().parent().hide();
		}
	}
	hideCredentials();
	$('#id_datafeed_type').change(function() {
		hideCredentials();
	});	
}
$(".addActionBtn").live("click", function(event){
    event.preventDefault()    
    $('#add_form').show();
    $('#program_list').hide();      
});

$(".addActionBtn2").live("click", function(event){
    event.preventDefault()
    $('#frmAddAction').submit();
});

$(".cancelBtn2").live("click", function(event){
    event.preventDefault()
    $('#add_form').hide();
    $('#program_list').show();
});


