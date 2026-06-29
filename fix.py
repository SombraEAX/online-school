with open('templates/edit_bot_mailings.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_update = False
for line in lines:
    if 'function updateTextarea' in line:
        in_update = True
        new_lines.append(line)
        new_lines.append('        const editor = document.getElementById(\'editor\');\n')
        new_lines.append('        const textarea = document.getElementById(\'mailing_text\');\n')
        new_lines.append('        let html = editor.innerHTML;\n')
        new_lines.append('        // Remove <div> and <p> tags\n')
        new_lines.append('        html = html.replace(/<(\\/)?(div|p)[^>]*>/gi, \'\');\n')
        new_lines.append('        // Remove any other unsupported tags except allowed ones (b, i, a, br)\n')
        new_lines.append('        html = html.replace(/<(?!\\/?(b|i|a|br)\\b)[^>]*>/gi, \'\');\n')
        new_lines.append('        textarea.value = html;\n')
        new_lines.append('    }\n')
        continue
    if in_update:
        if line.strip() == '}':
            in_update = False
        continue
    new_lines.append(line)

with open('templates/edit_bot_mailings.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done')
