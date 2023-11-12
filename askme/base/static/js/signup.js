const form = document.getElementById('form');
const login = document.getElementById('flogin');
const email = document.getElementById('femail');
const nickname = document.getElementById('fnickname');
const password = document.getElementById('fpassword');
const passwordRepeat = document.getElementById('frepeat-password');



form.addEventListener('submit', e => {
    e.preventDefault();

    validateInputs();
});

const setError = (element, message) => {
    const inputCheckError = element.parentElement;
    const errorDisplay = inputCheckError.querySelector('.error-message');

    errorDisplay.innerText = message;
    inputCheckError.classList.add('error');
    inputCheckError.classList.remove('success')
}


const setSuccess = element => {
    const inputCheckError = element.parentElement;
    const errorDisplay = inputCheckError.querySelector('.error-message');

    errorDisplay.innerText = '';
    inputCheckError.classList.add('success');
    inputCheckError.classList.remove('error');
};

const isValidEmail = email => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

const validateInputs = () => {
    const loginValue = login.value.trim();
    const emailValue = email.value.trim();
    const nicknameValue = nickname.value.trim();

    const passwordValue = password.value.trim();
    const passwordRepeatValue = passwordRepeat.value.trim();

    if(loginValue === '') {
        setError(login, 'Login is required');
    } else if (loginValue.length < 4) {
        setError(login, 'Login must be at least 4 characters');
    } else if (loginValue.length > 20) {
        setError(login, 'Login max length 20 characters');
    } else {
        setSuccess(login);
    }

    if(emailValue === '') {
        setError(email, 'Email is required');
    } else if (!isValidEmail(emailValue)) {
        setError(email, 'Provide a valid email');
    } else {
        setSuccess(email);
    }

    if(nicknameValue === '') {
        setError(nickname, 'Nickname is required');
    } else if (nicknameValue.length < 4) {
        setError(nickname, 'Nickname must be at least 4 characters');
    } else if (nicknameValue.length > 20) {
        setError(nickname, 'Nickname max length 20 characters');
    } else {
        setSuccess(nickname);
    }

    if(passwordValue === '') {
        setError(password, 'Password is required');
    } else if (passwordValue.length < 8) {
        setError(password, 'Password must be at least 8 characters');
    } else {
        setSuccess(password);
    }

    if(passwordRepeatValue === '') {
        setError(passwordRepeat, 'Confirm your password');
    } else if (passwordRepeatValue !== passwordValue) {
        setError(passwordRepeat, "Passwords doesn't match");
    } else {
        setSuccess(passwordRepeat);
    }

    if (document.querySelectorAll('.success').length === 5) {
        form.submit();
    }

};