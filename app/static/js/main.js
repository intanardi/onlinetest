$( document ).ready(function() {
    // START SCRIPT

    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
    }, false);

    $( "#repasswordF, #passwordF" ).keyup(function(e) {
        var password = $("#passwordF").val();
        var confirm_password = $("#repasswordF").val();
            if(password != confirm_password) {
              $("#password-message").removeClass("text-success");
              $("#password-message").addClass("text-danger");
               $("#password-message").text('Password Different !');
            }
            else{
               $("#password-message").removeClass("text-danger");
               $("#password-message").addClass("text-success");
               $("#password-message").text('Password Validated !');
            }
      });
    
    $(".confirmation-candidate").on("click", function (e) {
        const res = window.confirm("Anda yakin sudah mengerti ?");
        e.preventDefault();
        if(!res){
            console.log(1);
        }else {
            $.ajax({
                type: "POST",
                url: "update_status_psikotest/"+ $(this).attr("target_candidate_id"),
                data: {
                    'name': 'delete-dialog',
                    'value': $(this).attr("target-id")
                },
                success: function (response) {
                    console.log(response)
                    window.location.href = response;
                }
            });
        }
                
        });
    
    $(".delete-dialog",).on("click", function (e) {
    const getId = $(this).attr("target-id");
    const column_element = $(this).parent();
    const res = window.confirm("Are you sure you want to delete this data ?");
    e.preventDefault();
    if(!res){
        console.log(1);
    }else {
        $.ajax({
            type: "POST",
            url: "delete/"+ $(this).attr("target-id"),
            data: {
                'name': 'delete-dialog',
                'value': $(this).attr("target-id")
            },
            success: function () {
                column_element.parent().hide(250)
                console.log(123)
            }
        });
        return false;
    }
            
    });
      // END OF SCRIPT
});

$(".duration-check",).on("keydown", function (e) {
    console.log("duration")
    // Only ASCII character in that range allowed
    var ASCIICode = (e.which) ? e.which : e.keyCode
    if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57)) {
        $("#error-message").addClass("text-danger");
        $("#error-message").text('Set Duration in number Only');
    }
    else {
        $("#error-message").removeClass("text-danger");
        $("#error-message").text('');
    }
});

$(".backButton").click(function(){
    window.history.go(-1);
});

const lalert = $('#alertshow');
if (lalert.is(":checked")) {
    $("#alertBox").show() ;
}

$('#alertShow').click(function() {
    // $("#alertBox").toggle(this.checked);
    if(this.checked) {
        $("#alertBox").show() ;
    } else {
        $("#alertBox").hide() ;
        $("#alertBox").val(""); 
    }
});