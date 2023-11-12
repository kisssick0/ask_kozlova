const form = document.getElementById('form');
const login = document.getElementById('flogin');
const password = document.getElementById('fpassword');



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

const validateInputs = () => {
    const loginValue = login.value.trim();
    const passwordValue = password.value.trim();

    if(loginValue === '') {
        setError(login, 'Login is required');
    } else if (loginValue.length < 4) {
        setError(login, 'Login must be at least 4 characters');
    } else if (loginValue.length > 20) {
        setError(login, 'Login max length 20 characters');
    } else {
        setSuccess(login);
    }

    if(passwordValue === '') {
        setError(password, 'Password is required');
    } else if (passwordValue.length < 8) {
        setError(password, 'Password must be at least 8 characters');
    } else {
        setSuccess(password);
    }

    if (document.querySelectorAll('.success').length === 2) {
        form.submit();
    }

};