const form = document.getElementById('form');
const title = document.getElementById('ftitle');
const text = document.getElementById('fask');
const tags = document.getElementById('ftags');



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

const isValidTags = tags => {
    const re = /^\s*([a-zA-Z]+\s*,\s*){0,2}[a-zA-Z]+\s*$/;
    return re.test(String(tags).toLowerCase());
}

const validateInputs = () => {
    const titleValue = title.value.trim();
    const textValue = text.value.trim();
    const tagsValue = tags.value.trim();

    if(titleValue === '') {
        setError(title, 'Title is required');
    } else if (titleValue.length > 255) {
        setError(title, 'Login max length 255 characters');
    } else {
        setSuccess(title);
    }

    if(textValue === '') {
        setError(text, 'Text is required');
    } else if (textValue.length < 10) {
        setError(text, 'Text must be at least 10 characters');
    } else if (textValue.length > 800) {
        setError(text, 'Text max length 800 characters');
    } else {
        setSuccess(text);
    }

    if(tagsValue === '') {
        setError(tags, 'Tags is required');
    } else if (!isValidTags(tagsValue)) {
        setError(tags, 'Valid tags like: cat, dog, elf; Max: 3 tags');
    } else {
        setSuccess(tags);
    }

    if (document.querySelectorAll('.success').length === 3) {
        form.submit();
    }

};