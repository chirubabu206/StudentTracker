function addStudent() {
    const name = document.getElementById('name').value;
    const subject = document.getElementById('subject').value;
    const score = document.getElementById('score').value;

    fetch('/add_student', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, subject, score })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        fetchStudents();
    });
}

function fetchStudents() {
    fetch('/get_students')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('studentList');
            list.innerHTML = '';
            data.forEach(student => {
                const item = document.createElement('li');
                item.textContent = `${student.name} - ${student.subject}: ${student.score}`;
                list.appendChild(item);
            });
        });
}

// Fetch on page load
window.onload = fetchStudents;
