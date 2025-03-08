document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/documents/')
        .then(response => response.json())
        .then(data => {
            const documentList = document.getElementById('document-list');
            data.forEach(doc => {
                const div = document.createElement('div');
                div.textContent = `${doc.title}: ${doc.content}`;
                documentList.appendChild(div);
            });
        });
});