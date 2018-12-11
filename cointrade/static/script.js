
  $(document).ready(function() {
$( ".deletebtn" ).click(function() {
  alert( "Are you sure you want to delete this user?" );
  $.ajax({
    type: "DELETE",
    url: "http://127.0.0.1:5000/api/user/" + $(this).attr("data-id"),
    success: function(data) {
      window.location.reload("http://127.0.0.1:5000/");
    }
  });

});
});
