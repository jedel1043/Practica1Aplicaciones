$(document).ready(function(){
    const LoginWindow = $(".login");

    LoginWindow.on("click", "#submitBtn", function(e){
        e.preventDefault();

        let username = LoginWindow.find("#userInput").val();
        window.location = "main.html?username="+username;
    })
})