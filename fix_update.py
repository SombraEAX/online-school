with open('templates/edit_bot_mailings.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    function updateTextarea() {
        const editor = document.getElementById('editor');
        const textarea = document.getElementById('mailing_text');
        let html = editor.innerHTML;
        // Remove <div> and <p> tags
        html = html.replace(/<(\/)?(div|p)[^>]*>/gi, '');
        // Remove any other unsupported tags except allowed ones (b, i, a, br)
        html = html.replace(/<(?!\/?(b|i|a|br)\b)[^>]*>/gi, '');
        textarea.value = html;
    }'''

new = '''    function updateTextarea() {
        const editor = document.getElementById('editor');
        const textarea = document.getElementById('mailing_text');
        let html = editor.innerHTML;
        // Remove <div> and <p> tags
        html = html.replace(/<(\\/)?(div|p)[^>]*>/gi, '');
        // Remove any other unsupported tags except allowed ones (b, i, a, br)
        html = html.replace(/<(?!\\/?(b|i|a|br)\\b)[^>]*>/gi, '');
        textarea.value = html;
    }'''

content = content.replace(old, new)
with open('templates/edit_bot_mailings.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed')
