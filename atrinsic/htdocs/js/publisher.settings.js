function initPubIncentives() {  
    function showfields() {
        value = $("select[name='datafeed_type']").val();
        int_value = parseInt(value);
        if (int_value == 1) {
            $('#id_username').parent().parent().show();
            $('#id_password').parent().parent().show();
            $('#id_server').parent().parent().show();
        } else {
            $('#id_username').parent().parent().hide();
            $('#id_password').parent().parent().hide();
            $('#id_server').parent().parent().hide();
        }
    }
    
    $('#id_datafeed_type').change(function() {
        showfields();
    });
    showfields();
    
    
    $(".rdtbtn").click(function() { 
        $("#form").submit();
    });
}	

