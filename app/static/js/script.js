var dropdown = document.getElementsByClassName("dropdown-btn");
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function() {
  this.classList.toggle("active");
  var dropdownContent = this.nextElementSibling;
  if (dropdownContent.style.display === "block") {
  dropdownContent.style.display = "none";
  } else {
  dropdownContent.style.display = "block";
  }
  });
}
$(function(){
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

  // ADD REMOVE JQUERY ELEMENT
  $('a#addChoices').click(function() {
    const main_element = '<div class="input-group mt-2 mb-2 parentElement">'+
    '<input type="text" class="form-control form-target-check" placeholder="Choice" name="answer[]">'+
    '<div class="input-group-append removeElement">'+
      '<button class="btn btn-danger" type="button">'+
        '<i class="fa fa-trash"></i>'+
      '</button>'+
    '</div></div>';
    $('#answer_lists').append(main_element);
    $('.removeElement').click(function(e) {
      $(this).parent().remove()
    });
    $('.form-target-check').click(function(e) {
      console.log(1)
    });
  });
});
var countDownDate = "{{ test_time }}";

  var x = setInterval(function() {

    // Get today's date and time
    var now = new Date().getTime();
    console.log(countDownDate)
    console.log(now)
    // Find the distance between now and the count down date
    var distance = countDownDate - now;
      
    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      
    // Output the result in an element with id="demo"
    document.getElementById("demo").innerHTML = hours + " Jam "
    + minutes + " Menit " + seconds + " Detik ";
      
    // If the count down is over, write some text 
    if (distance < 0) {
      clearInterval(x);
      document.getElementById("demo").innerHTML = "EXPIRED";
    }
  }, 1000);