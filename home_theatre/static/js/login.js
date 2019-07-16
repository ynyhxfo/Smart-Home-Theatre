function login() {
 
    var username = Document.getElementById("username");
    var pass = Document.getElementById("password");
 
    if (username.value == "") {
 
        alert("please input your user name");
 
    } else if (pass.value  == "") {
 
        alert("please input your password");
 
    } else if(username.value == "admin" && pass.value == "123456"){
 
        window.location.href="welcome.html";
 
    } else {
 
        alert("please check your username or your password")
 
    }
}
