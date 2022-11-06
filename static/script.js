function getPage() {
    const id = document.getElementById("page-id-input").value;
    if (id != "") {
        window.open('http://127.0.0.1:5000/page/' + id, '_blank');
    } else {
        alert("Must enter an id");
    }
}

function deletePage() {
    const id = document.getElementById("page-id-input").value;
    if (id != "") {
        fetch('http://127.0.0.1:5000/page/' + id, {
            method: 'DELETE',
            mode: 'cors',
        })
            .then((response) => response.json())
            .then(data => {
                if (data.success === true) {
                    location.reload();
                } else {
                    alert(JSON.stringify(data))
                }
            });
    } else {
        alert("Must enter an id");
    }
}

async function fetchPageData(id) {
    const response = await fetch('http://127.0.0.1:5000/page/' + id);
    const data = await response.json();
    return data
}

async function updatePage() {
    const id = document.getElementById("page-id-input").value;
    if (id != "") {
        data = await fetchPageData(id);
        if (data.success == true) {
            fetch('http://127.0.0.1:5000/page/' + id, {
                method: 'PATCH',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "name": prompt("Name: ", data.page.name),
                    "category": prompt("Category: ", data.page.category),
                    "url": prompt("URL: ", data.page.url)
                })
            })
                .then((response) => response.json())
                .then(data => {
                    if (data.success === true) {
                        location.reload();
                    } else {
                        alert(JSON.stringify(data))
                    }
                });
        } else {
            alert(JSON.stringify(data));
        }
    } else {
        alert("Must enter an id");
    }
}

window.onload = (event) => {
    document.getElementById("get-page-button").addEventListener("click", getPage);
    document.getElementById("delete-page-button").addEventListener("click", deletePage);
    document.getElementById("update-page-button").addEventListener("click", updatePage);
}