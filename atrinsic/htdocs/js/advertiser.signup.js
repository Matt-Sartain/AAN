function initStep1FormManipulation(){    
    $('#id_country').change(function(){state_toggle('#id_country');});
    state_toggle('#id_country');    
}

function initStep2FormManipulation(){
    $('#id_date_site_launched').datepicker({showOn: 'both', buttonImage: '/images/blankdatepicker.png', buttonImageOnly: true, dateFormat: 'mm/dd/yy'});
}

function initStep3FormManipulation(){
    $('#recaptcha_response_field').css({'left': '0px'});    
}

function state_toggle(dropdown){    
    $('#id_state').parent().parent().hide();
	$('#id_province').parent().parent().hide();
    if($(dropdown).val() == 'US'){
        $('#id_state').parent().parent().show();
        $('#id_province').parent().parent().hide();
    }else if($(dropdown).val() == 'CA'){
        $('#id_province').parent().parent().show();
        $('#id_state').parent().parent().hide();
    }else{
        $('#id_province').parent().parent().hide();
        $('#id_state').parent().parent().hide();
    }
}
function state_toggle_pub(dropdown){
    $('#id_pub_state').parent().parent().hide();
	$('#id_pub_province').parent().parent().hide();
    if($(dropdown).val() == 'US'){
        $('#id_pub_state').parent().parent().show();
        $('#id_pub_province').parent().parent().hide();
    }else if($(dropdown).val() == 'CA'){
        $('#id_pub_province').parent().parent().show();
        $('#id_pub_state').parent().parent().hide();
    }else{
        $('#id_pub_province').parent().parent().hide();
        $('#id_pub_state').parent().parent().hide();
    }
}