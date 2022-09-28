document.querySelectorAll('.info-title').forEach(title => {
    title.addEventListener('click', event => {
        
        title.querySelectorAll('.arrow').forEach(arrow => {
            if (arrow.className === "arrow") {
                arrow.className = "arrow arrow-hide";
            } else {
                arrow.className = "arrow";
            }
        })

        title.parentNode.querySelectorAll('.info-content').forEach(content => {
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        })
    })
})
