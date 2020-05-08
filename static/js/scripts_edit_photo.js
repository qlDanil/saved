function tagControl(e) {
    tag = e.target.value;
    e.target.value = tag.replace(/\s+/g, '').slice(0,30);
}

document.getElementById('hashtagItem').addEventListener('change', tagControl, false);
