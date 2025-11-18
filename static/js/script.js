// Código principal que espera a cargar el DOM
document.addEventListener("DOMContentLoaded", function () {


    // en el DOM referencio los elementos del formulario y el formulario
    const form = document.getElementById("login-form");
    const nombreInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const emailInput = document.getElementById("email");


    // Expresiones regulares
    const regexNombre = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{5,40}$/;
    const regexDni = /^[1-9]\d{7}$/;
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    // Eventos para los elemenos del DOM que se escuchan y relacionarlos con una funcion
    form.addEventListener("submit", manejarEnvio);
    nombreInput.addEventListener("input", validarNombre);
    emailInput.addEventListener("input", validarEmail);
    passwordInput.addEventListener("input", validarPassword)
    

});


function validarNombre(nombreInput) {

    const valor=nombreInput.value.trim()
    const errorElement=document.getElementById()
  



    // Esto selecciona el <span> que esté dentro de .input-group del #username, sin importar qué clase tenga.
    const errorUsername = document.querySelector("#username").parentElement.querySelector("span");
    if (username === "") {
        mostrarError(errorUsername, "Missing Username");
        return false;
    }
    else if (username.length <= 3) {
        mostrarError(errorUsername, "Debe tener mas de 3 caracteres");
        return false;
    }
    else {
        mostrarExito(errorUsername, "√");
        return true;
    }
}


