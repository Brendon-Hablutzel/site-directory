fetch('ENTER URL HERE', {
    method: 'POST',
    mode: 'cors',
    cache: 'no-cache',
    /* credentials: 'same-origin', */
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: JSON.stringify({
      "name": document.title,
      "category": prompt("Category: "),
      "url": window.location.href
    })
})
  .then((response) => response.json())
  .then((data) => alert(JSON.stringify(data)));