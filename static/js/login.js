document.getElementById("Formulario_Login").addEventListener('submit', function (e) {

    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    const nombreValido = validarNombre(username);
    const emailValido = validarEmail(email);
    const passwordValido = validarPassword(password);

    if (nombreValido && emailValido && passwordValido) {
        this.submit(); 
    }

});


function validarNombre(username) {
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


function validarEmail(email) {
    // Esto selecciona el <span> que esté dentro de .input-group del #email, sin importar qué clase tenga.
    const errorEmail = document.querySelector("#email").parentElement.querySelector("span");
    const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (email === "") {
        mostrarError(errorEmail, "Missing Email");
        return false;
    }
    else if (!regexEmail.test(email)) {
        mostrarError(errorEmail, "No válido");
        return false;
    }
    else {
        mostrarExito(errorEmail, "√")
        return true;
    }
}

function validarPassword(password) {
    // Esto selecciona el <span> que esté dentro de .input-group del #password, sin importar qué clase tenga.
    const errorPassword = document.querySelector("#password").parentElement.querySelector("span");
    if (password === "") {
        mostrarError(errorPassword, "Missing Password");
        return false;
    }
    else if (password.length <= 6) {
        mostrarError(errorPassword, "Mas de seis caracteres")
        return false;
    }
    else {
        mostrarExito(errorPassword, "√")
        return true
    }
}


function mostrarError(elemento, mensaje) {
    elemento.textContent = mensaje;
    if (elemento.className !== "error-message-show") {
        elemento.className = "error-message-show";
    }
}

function mostrarExito(elemento, mensaje) {
    elemento.textContent = mensaje;
    if (elemento.className !== "success-icon") {
        elemento.className = "success-icon";
    }

}



// Al cambiar el contenido del input, se valida en tiempo real
document.getElementById("username").addEventListener("input", function () {
    const valor = this.value.trim();
    validarNombre(valor);
});


document.getElementById("email").addEventListener("input", function () {
    validarEmail(this.value.trim());
});

document.getElementById("password").addEventListener("input", function () {
    validarPassword(this.value.trim());
});


