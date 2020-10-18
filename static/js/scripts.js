// display an error message when the
function displayLoginError(){
  $("form.login").submit(function(){
    username = $("#username").val();
    password = $("#password").val();
    if(!(username != "" && password !="")){
        alert("Veuillez saisir le nom d'utilsateur et le mot de passe.");
        return false;
    }
  });
}