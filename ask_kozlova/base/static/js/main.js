function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var items = document.getElementsByClassName('like-section')

//console.log(items);

for (let item of items) {
    const [button_like, counter, button_dislike] = item.children;

    button_like.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('question_id', button_like.dataset.id)

        const request = new Request('/like/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
        .then((response) => response.json())
        .then((data) => {
            counter.innerHTML = data.count;
        });
    })

    button_dislike.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('question_id', button_dislike.dataset.id)

        const request = new Request('/dislike/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
        .then((response) => response.json())
        .then((data) => {
            counter.innerHTML = data.count;
        });
    })
}

var correctable_answers = document.getElementsByClassName('correct-section')

console.log(correctable_answers);

for (let answer of correctable_answers) {
    const [button_correct,,] = answer.children;

    button_correct.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('answer_id', button_correct.dataset.answer)
        formData.append('question_id', button_correct.dataset.question)

        const request = new Request('/correct/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
        .then((response) => response.json())
        .then((data) => {
            button_correct.innerHTML = data.correctable;
        });
    })
}

var likable_answers = document.getElementsByClassName('like-answer-section')

for (let item of likable_answers) {
    const [button_like, counter, button_dislike] = item.children;

    button_like.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('answer_id', button_like.dataset.id)

        const request = new Request('/like_answer/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
        .then((response) => response.json())
        .then((data) => {
            counter.innerHTML = data.count;
        });
    })

    button_dislike.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('answer_id', button_dislike.dataset.id)

        const request = new Request('/dislike_answer/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
        .then((response) => response.json())
        .then((data) => {
            counter.innerHTML = data.count;
        });
    })
}