class WYSIWYGEditor {
    constructor(textareaId, options = {}) {
        this.textarea = document.getElementById(textareaId);
        if (!this.textarea) {
            console.error(`Textarea with id "${textareaId}" not found`);
            return;
        }

        this.options = {
            height: options.height || '400px',
            placeholder: options.placeholder || 'Enter text here...',
            ...options
        };

        this.init();
    }

    init() {
        this.createEditor();
        this.setupEventListeners();
    }

    createEditor() {
        // Create editor container
        const editorContainer = document.createElement('div');
        editorContainer.className = 'wysiwyg-editor';
        editorContainer.style.cssText = `
            border: 1px solid #ced4da;
            border-radius: 0.375rem;
            background: white;
        `;

        // Create toolbar
        const toolbar = this.createToolbar();
        
        // Create editable area
        const editor = document.createElement('div');
        editor.className = 'wysiwyg-content';
        editor.contentEditable = true;
        editor.style.cssText = `
            min-height: ${this.options.height};
            padding: 12px;
            outline: none;
            overflow-y: auto;
            max-height: 600px;
        `;

        // Set initial content
        editor.innerHTML = this.textarea.value || '';
        if (!editor.innerHTML.trim()) {
            editor.innerHTML = `<p><br></p>`;
        }

        // Assemble editor
        editorContainer.appendChild(toolbar);
        editorContainer.appendChild(editor);

        // Hide original textarea and insert editor
        this.textarea.style.display = 'none';
        this.textarea.parentNode.insertBefore(editorContainer, this.textarea.nextSibling);

        // Save references
        this.editor = editor;
        this.toolbar = toolbar;
        this.editorContainer = editorContainer;
    }

    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'wysiwyg-toolbar';
        toolbar.style.cssText = `
            background: #f8f9fa;
            border-bottom: 1px solid #ced4da;
            padding: 8px;
        `;
        


        // Button groups
        const buttonGroups = [
            // Text formatting
            [
                { icon: 'fa-bold', title: 'Bold', command: 'bold' },
                { icon: 'fa-italic', title: 'Italic', command: 'italic' },
                { icon: 'fa-underline', title: 'Underline', command: 'underline' },
                { icon: 'fa-strikethrough', title: 'Strikethrough', command: 'strikeThrough' }
            ],
            // Headings
            [
                { icon: 'fa-heading', title: 'Heading 1', command: 'formatBlock', value: 'h1' },
                { icon: 'fa-heading', title: 'Heading 2', command: 'formatBlock', value: 'h2' },
                { icon: 'fa-heading', title: 'Heading 3', command: 'formatBlock', value: 'h3' },
                { icon: 'fa-paragraph', title: 'Paragraph', command: 'formatBlock', value: 'p' }
            ],
            // Lists
            [
                { icon: 'fa-list-ul', title: 'Bullet List', command: 'insertUnorderedList' },
                { icon: 'fa-list-ol', title: 'Numbered List', command: 'insertOrderedList' },
                { icon: 'fa-indent', title: 'Increase Indent', command: 'indent' },
                { icon: 'fa-outdent', title: 'Decrease Indent', command: 'outdent' }
            ],
            // Alignment
            [
                { icon: 'fa-align-left', title: 'Align Left', command: 'justifyLeft' },
                { icon: 'fa-align-center', title: 'Align Center', command: 'justifyCenter' },
                { icon: 'fa-align-right', title: 'Align Right', command: 'justifyRight' },
                { icon: 'fa-align-justify', title: 'Justify', command: 'justifyFull' }
            ],
            // Other
            [
                { icon: 'fa-link', title: 'Insert Link', command: 'createLink', custom: true },
                { icon: 'fa-square', title: 'Insert Button Link', command: 'createButtonLink', custom: true },
                { icon: 'fa-image', title: 'Insert Image', command: 'insertImage', custom: true },
                { icon: 'fa-play-circle', title: 'Insert YouTube Video', command: 'insertVideo', custom: true },
                { icon: 'fa-code', title: 'Code', command: 'formatBlock', value: 'pre' },
                { icon: 'fa-quote-left', title: 'Blockquote', command: 'formatBlock', value: 'blockquote' }
            ],
            // History and extras
            [
                { icon: 'fa-undo', title: 'Undo', command: 'undo' },
                { icon: 'fa-redo', title: 'Redo', command: 'redo' },
                { icon: 'fa-remove-format', title: 'Clear Formatting', command: 'removeFormat' },
                { icon: 'fa-eye', title: 'View HTML', command: 'viewSource', custom: true }
            ]
        ];

        buttonGroups.forEach(group => {
            const groupContainer = document.createElement('div');
            groupContainer.className = 'wysiwyg-btn-group';
            groupContainer.style.cssText = 'display: inline-flex; gap: 2px; border-right: 1px solid #dee2e6; padding-right: 8px; margin-right: 4px; flex-shrink: 0;';

            group.forEach(buttonConfig => {
                const button = this.createButton(buttonConfig);
                groupContainer.appendChild(button);
            });

            toolbar.appendChild(groupContainer);
        });

        return toolbar;
    }

    createButton(config) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'wysiwyg-btn';
        button.title = config.title;
        button.innerHTML = `<i class="fas ${config.icon}"></i>`;
        button.style.cssText = `
            background: white;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 6px 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 32px;
            height: 32px;
            transition: all 0.2s;
        `;

        button.addEventListener('mouseover', () => {
            button.style.background = '#e9ecef';
        });

        button.addEventListener('mouseout', () => {
            button.style.background = 'white';
        });

        button.addEventListener('mousedown', (e) => {
            e.preventDefault();
            
            if (config.custom) {
                this.handleCustomCommand(config.command);
            } else {
                this.execCommand(config.command, config.value);
            }
        });

        return button;
    }

    execCommand(command, value = null) {
        this.editor.focus();
        
        if (value) {
            document.execCommand(command, false, value);
        } else {
            document.execCommand(command, false, null);
        }

        this.updateTextarea();
        this.updateButtonStates();
    }

    handleCustomCommand(command) {
        switch (command) {
            case 'createLink':
                this.insertLink();
                break;
            case 'createButtonLink':
                this.insertButtonLink();
                break;
            case 'insertImage':
                this.insertImage();
                break;
            case 'insertVideo':
                this.insertVideo();
                break;
            case 'viewSource':
                this.toggleSourceView();
                break;
        }
    }

    insertLink() {
        const url = prompt('Enter link URL:', 'https://');
        if (url) {
            this.execCommand('createLink', url);
        }
    }

    insertButtonLink() {
        this.showButtonLinkDialog();
    }

    showButtonLinkDialog() {
        // Save current cursor position
        this.savedRange = window.getSelection().getRangeAt(0);
        
        // Create modal window
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;

        dialog.innerHTML = `
            <h3 style="margin: 0 0 20px 0; color: #333;">Insert Button Link</h3>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">Button Text:</label>
                <input type="text" id="button-text" placeholder="Click here" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">Link URL:</label>
                <input type="url" id="button-url" placeholder="https://example.com" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">Button Style:</label>
                <select id="button-style" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <option value="primary">Primary (Blue)</option>
                    <option value="secondary">Secondary (Gray)</option>
                    <option value="success">Success (Green)</option>
                    <option value="danger">Danger (Red)</option>
                    <option value="warning">Warning (Yellow)</option>
                    <option value="info">Info (Blue)</option>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                </select>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">Size:</label>
                <select id="button-size" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <option value="btn-sm">Small</option>
                    <option value="" selected>Normal</option>
                    <option value="btn-lg">Large</option>
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" id="button-block" style="margin: 0;">
                    <span style="font-weight: normal; color: #555;">Full width</span>
                </label>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button id="cancel-btn" style="padding: 8px 16px; border: 1px solid #ddd; background: #f8f9fa; color: #333; border-radius: 4px; cursor: pointer;">
                    Cancel
                </button>
                <button id="insert-btn" style="padding: 8px 16px; border: none; background: #007bff; color: white; border-radius: 4px; cursor: pointer;">
                    Insert
                </button>
            </div>
        `;

        modal.appendChild(dialog);
        document.body.appendChild(modal);

        // Event handlers
        const buttonText = dialog.querySelector('#button-text');
        const buttonUrl = dialog.querySelector('#button-url');
        const buttonStyle = dialog.querySelector('#button-style');
        const buttonSize = dialog.querySelector('#button-size');
        const buttonBlock = dialog.querySelector('#button-block');
        const cancelBtn = dialog.querySelector('#cancel-btn');
        const insertBtn = dialog.querySelector('#insert-btn');

        // Focus on first field
        buttonText.focus();

        // Add debug logging
        console.log('Modal elements:', { buttonText, buttonUrl, buttonStyle, buttonSize, buttonBlock, insertBtn });

        insertBtn.addEventListener('click', (e) => {
            console.log('Insert button clicked');
            e.preventDefault();
            
            const text = buttonText.value.trim();
            const url = buttonUrl.value.trim();
            
            console.log('Form values:', { text, url });
            
            if (!text) {
                alert('Please enter button text.');
                buttonText.focus();
                return;
            }
            
            if (!url) {
                alert('Please enter link URL.');
                buttonUrl.focus();
                return;
            }
            
            console.log('Creating button link...');
            this.createButtonLink(text, url, buttonStyle.value, buttonSize.value, buttonBlock.checked);
            document.body.removeChild(modal);
        });

        cancelBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        // Enter key handling in fields
        [buttonText, buttonUrl].forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    insertBtn.click();
                }
            });
        });
    }

    createButtonLink(text, url, style, size, block) {
        // CSS classes for different button styles
        const styleClasses = {
            primary: 'btn-primary',
            secondary: 'btn-secondary', 
            success: 'btn-success',
            danger: 'btn-danger',
            warning: 'btn-warning',
            info: 'btn-info',
            light: 'btn-light',
            dark: 'btn-dark'
        };

        // Create CSS styles for button
        const cssStyles = {
            primary: { bg: '#007bff', border: '#007bff', color: 'white' },
            secondary: { bg: '#6c757d', border: '#6c757d', color: 'white' },
            success: { bg: '#28a745', border: '#28a745', color: 'white' },
            danger: { bg: '#dc3545', border: '#dc3545', color: 'white' },
            warning: { bg: '#ffc107', border: '#ffc107', color: '#212529' },
            info: { bg: '#17a2b8', border: '#17a2b8', color: 'white' },
            light: { bg: '#f8f9fa', border: '#f8f9fa', color: '#212529' },
            dark: { bg: '#343a40', border: '#343a40', color: 'white' }
        };

        const styleCss = cssStyles[style] || cssStyles.primary;
        const sizeClass = size || '';
        const blockClass = block ? 'btn-block' : '';
        
        // Create button HTML
        const buttonHtml = `<a href="${url}" target="_blank" 
            class="editor-button ${styleCss} ${sizeClass} ${blockClass}"
            style="display: inline-block; 
                   padding: ${block ? '12px' : '8px 16px'}; 
                   background: ${styleCss.bg}; 
                   color: ${styleCss.color}; 
                   border: 1px solid ${styleCss.border}; 
                   border-radius: 4px; 
                   text-decoration: none; 
                   cursor: pointer; 
                   font-weight: 500; 
                   text-align: center; 
                   transition: all 0.2s ease;
                   ${block ? 'width: 100%; display: block;' : ''}">
            ${text}
        </a>`;
        
        // Restore saved cursor position
        this.editor.focus();
        
        if (this.savedRange) {
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(this.savedRange);
        }
        
        // Insert HTML at saved cursor position
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        
        // Create element from HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = buttonHtml;
        const buttonElement = tempDiv.firstChild;
        
        // Insert element at current position
        range.deleteContents();
        range.insertNode(buttonElement);
        
        // Move cursor after inserted element
        range.setStartAfter(buttonElement);
        range.setEndAfter(buttonElement);
        selection.removeAllRanges();
        selection.addRange(range);
        
        this.updateTextarea();
        
        this.showNotification('Button link added successfully!', 'success');
    }

    insertImageAtPosition(url) {
        // Restore saved cursor position
        this.editor.focus();
        
        if (this.savedRange) {
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(this.savedRange);
        }
        
        // Create image HTML
        const imgHtml = `<img src="${url}" alt="Image" style="max-width: 100%; height: auto; border-radius: 4px; margin: 0.5rem 0;">`;
        
        // Insert HTML at saved position
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        
        // Create element from HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = imgHtml;
        const imgElement = tempDiv.firstChild;
        
        // Insert element at current position
        range.deleteContents();
        range.insertNode(imgElement);
        
        // Move cursor after inserted element
        range.setStartAfter(imgElement);
        range.setEndAfter(imgElement);
        selection.removeAllRanges();
        selection.addRange(range);
        
        this.updateTextarea();
        this.showNotification('Image added successfully!', 'success');
    }

    insertImage() {
        this.showImageDialog();
    }

    showImageDialog() {
        // Save current cursor position
        this.savedRange = window.getSelection().getRangeAt(0);
        
        // Create modal window
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;

        dialog.innerHTML = `
            <h3 style="margin: 0 0 20px 0; color: #333;">Insert Image</h3>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Choose method:</label>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button id="upload-btn" style="flex: 1; padding: 10px; border: 2px solid #007bff; background: #007bff; color: white; border-radius: 4px; cursor: pointer; font-size: 14px;">
                        📁 Upload from device
                    </button>
                    <button id="url-btn" style="flex: 1; padding: 10px; border: 2px solid #6c757d; background: #6c757d; color: white; border-radius: 4px; cursor: pointer; font-size: 14px;">
                        🔗 Insert by URL
                    </button>
                </div>
            </div>
            
            <div id="upload-section" style="display: none;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Select image file:</label>
                <input type="file" id="file-input" accept="image/*" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                <div style="font-size: 12px; color: #666; margin-bottom: 15px;">
                    Supported formats: PNG, JPG, JPEG, GIF, WEBP (max 16MB)
                </div>
            </div>
            
            <div id="url-section" style="display: none;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Image URL:</label>
                <input type="url" id="url-input" placeholder="https://example.com/image.jpg" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button id="cancel-btn" style="padding: 8px 16px; border: 1px solid #ddd; background: #f8f9fa; color: #333; border-radius: 4px; cursor: pointer;">
                    Cancel
                </button>
                <button id="insert-btn" style="padding: 8px 16px; border: none; background: #28a745; color: white; border-radius: 4px; cursor: pointer; display: none;">
                    Insert
                </button>
            </div>
        `;

        modal.appendChild(dialog);
        document.body.appendChild(modal);

        // Event handlers
        const uploadBtn = dialog.querySelector('#upload-btn');
        const urlBtn = dialog.querySelector('#url-btn');
        const uploadSection = dialog.querySelector('#upload-section');
        const urlSection = dialog.querySelector('#url-section');
        const fileInput = dialog.querySelector('#file-input');
        const urlInput = dialog.querySelector('#url-input');
        const cancelBtn = dialog.querySelector('#cancel-btn');
        const insertBtn = dialog.querySelector('#insert-btn');

        let selectedMode = null;

        uploadBtn.addEventListener('click', () => {
            selectedMode = 'upload';
            uploadSection.style.display = 'block';
            urlSection.style.display = 'none';
            insertBtn.style.display = 'block';
            uploadBtn.style.borderColor = '#007bff';
            uploadBtn.style.background = '#007bff';
            urlBtn.style.borderColor = '#6c757d';
            urlBtn.style.background = '#6c757d';
        });

        urlBtn.addEventListener('click', () => {
            selectedMode = 'url';
            uploadSection.style.display = 'none';
            urlSection.style.display = 'block';
            insertBtn.style.display = 'block';
            urlBtn.style.borderColor = '#007bff';
            urlBtn.style.background = '#007bff';
            uploadBtn.style.borderColor = '#6c757d';
            uploadBtn.style.background = '#6c757d';
            urlInput.focus();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                insertBtn.textContent = 'Upload & Insert';
            }
        });

        urlInput.addEventListener('input', () => {
                insertBtn.textContent = 'Insert';
        });

        insertBtn.addEventListener('click', async () => {
            if (selectedMode === 'upload') {
                const file = fileInput.files[0];
                if (file) {
                    await this.handleImageUpload(file);
                    document.body.removeChild(modal);
                } else {
                    alert('Please select an image file.');
                }
            } else if (selectedMode === 'url') {
                const url = urlInput.value.trim();
                if (url) {
                    // Insert image with position preservation
                    this.insertImageAtPosition(url);
                    document.body.removeChild(modal);
                } else {
                    alert('Please enter image URL.');
                }
            }
        });

        cancelBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    async handleImageUpload(file) {
        // Check file size (max 16MB)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            alert('File too large. Maximum size is 16MB.');
            return;
        }

        // Check file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            return;
        }

        // Show upload progress
        this.showUploadProgress();

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/upload-image', {
                method: 'POST',
                body: formData
            });

            // Get response text for debugging
            const responseText = await response.text();
            console.log('Server response:', responseText);
            
            let result;
            try {
                result = JSON.parse(responseText);
            } catch (jsonError) {
                console.error('JSON parsing error:', jsonError);
                console.error('Response text:', responseText);
                throw new Error('Server returned an invalid response. There may be an authentication or permission issue.');
            }

            if (response.ok && result.url) {
                // Insert uploaded image with position preservation
                this.insertImageAtPosition(result.url);
                
                // Show success notification
                this.showNotification('Image uploaded successfully!', 'success');
            } else {
                throw new Error(result.error || 'Upload error: ' + response.statusText);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Image upload error: ' + error.message, 'error');
        } finally {
            this.hideUploadProgress();
        }
    }

    showUploadProgress() {
        // Create progress indicator
        const progressDiv = document.createElement('div');
        progressDiv.id = 'wysiwyg-upload-progress';
        progressDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 10000;
            text-align: center;
        `;
        progressDiv.innerHTML = `
            <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>
            Uploading image...
        `;
        
        document.body.appendChild(progressDiv);
    }

    hideUploadProgress() {
        const progressDiv = document.getElementById('wysiwyg-upload-progress');
        if (progressDiv) {
            document.body.removeChild(progressDiv);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 4px;
            color: white;
            z-index: 10000;
            max-width: 300px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        // Set color based on type
        switch (type) {
            case 'success':
                notification.style.background = '#28a745';
                break;
            case 'error':
                notification.style.background = '#dc3545';
                break;
            default:
                notification.style.background = '#17a2b8';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 100);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    insertVideo() {
        this.showVideoDialog();
    }

    showVideoDialog() {
        // Save current cursor position
        this.savedRange = window.getSelection().getRangeAt(0);
        
        // Create modal window
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;

        dialog.innerHTML = `
            <h3 style="margin: 0 0 20px 0; color: #333;">Insert Video</h3>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Choose method:</label>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button id="upload-btn" style="flex: 1; padding: 10px; border: 2px solid #007bff; background: #007bff; color: white; border-radius: 4px; cursor: pointer; font-size: 14px;">
                        📹 Upload from device
                    </button>
                    <button id="youtube-btn" style="flex: 1; padding: 10px; border: 2px solid #ff0000; background: #ff0000; color: white; border-radius: 4px; cursor: pointer; font-size: 14px;">
                        ▶️ YouTube Video
                    </button>
                </div>
            </div>
            
            <div id="upload-section" style="display: none;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Select video file:</label>
                <input type="file" id="file-input" accept="video/*" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                <div style="font-size: 12px; color: #666; margin-bottom: 15px;">
                    Supported formats: MP4, AVI, MOV, WMV, FLV, WebM, MKV (max 50MB)
                </div>
            </div>
            
            <div id="youtube-section" style="display: none;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">YouTube Video URL:</label>
                <input type="url" id="youtube-url-input" placeholder="https://www.youtube.com/watch?v=..." style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;">
                <div style="font-size: 12px; color: #666; margin-bottom: 15px;">
                    Paste a YouTube video link
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button id="cancel-btn" style="padding: 8px 16px; border: 1px solid #ddd; background: #f8f9fa; color: #333; border-radius: 4px; cursor: pointer;">
                    Cancel
                </button>
                <button id="insert-btn" style="padding: 8px 16px; border: none; background: #28a745; color: white; border-radius: 4px; cursor: pointer; display: none;">
                    Insert
                </button>
            </div>
        `;

        modal.appendChild(dialog);
        document.body.appendChild(modal);

        // Event handlers
        const uploadBtn = dialog.querySelector('#upload-btn');
        const youtubeBtn = dialog.querySelector('#youtube-btn');
        const uploadSection = dialog.querySelector('#upload-section');
        const youtubeSection = dialog.querySelector('#youtube-section');
        const fileInput = dialog.querySelector('#file-input');
        const youtubeUrlInput = dialog.querySelector('#youtube-url-input');
        const cancelBtn = dialog.querySelector('#cancel-btn');
        const insertBtn = dialog.querySelector('#insert-btn');

        let selectedMode = null;

        uploadBtn.addEventListener('click', () => {
            selectedMode = 'upload';
            uploadSection.style.display = 'block';
            youtubeSection.style.display = 'none';
            insertBtn.style.display = 'block';
            uploadBtn.style.borderColor = '#007bff';
            uploadBtn.style.background = '#007bff';
            youtubeBtn.style.borderColor = '#ff0000';
            youtubeBtn.style.background = '#ff0000';
        });

        youtubeBtn.addEventListener('click', () => {
            selectedMode = 'youtube';
            uploadSection.style.display = 'none';
            youtubeSection.style.display = 'block';
            insertBtn.style.display = 'block';
            youtubeBtn.style.borderColor = '#007bff';
            youtubeBtn.style.background = '#007bff';
            uploadBtn.style.borderColor = '#ff0000';
            uploadBtn.style.background = '#ff0000';
            youtubeUrlInput.focus();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                insertBtn.textContent = 'Upload & Insert';
            }
        });

        youtubeUrlInput.addEventListener('input', () => {
                insertBtn.textContent = 'Insert';
        });

        insertBtn.addEventListener('click', async () => {
            if (selectedMode === 'upload') {
                const file = fileInput.files[0];
                if (file) {
                    await this.handleVideoUpload(file);
                    document.body.removeChild(modal);
                } else {
                    alert('Please select a video file.');
                }
            } else if (selectedMode === 'youtube') {
                const url = youtubeUrlInput.value.trim();
                if (url) {
                    this.insertYouTubeVideo(url);
                    document.body.removeChild(modal);
                } else {
                    alert('Please enter a YouTube video URL.');
                }
            }
        });

        cancelBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    async handleVideoUpload(file) {
        // Check file size (max 50MB)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            alert('File too large. Maximum size is 50MB.');
            return;
        }

        // Check file type
        if (!file.type.startsWith('video/')) {
            alert('Please select a video file.');
            return;
        }

        // Show upload progress
        this.showVideoUploadProgress();

        const formData = new FormData();
        formData.append('video', file);

        try {
            const response = await fetch('/upload-video', {
                method: 'POST',
                body: formData
            });

            // Get response text for debugging
            const responseText = await response.text();
            console.log('Server response:', responseText);
            
            let result;
            try {
                result = JSON.parse(responseText);
            } catch (jsonError) {
                console.error('JSON parsing error:', jsonError);
                console.error('Response text:', responseText);
                throw new Error('Server returned an invalid response. There may be an authentication or permission issue.');
            }

            if (response.ok && result.url) {
                // Insert uploaded video
                const video = `<video controls style="max-width: 100%; height: auto; border-radius: 4px; margin: 0.5rem 0;">
                    <source src="${result.url}" type="${file.type}">
                    Your browser does not support video.
                </video>`;
                
                this.editor.focus();
                document.execCommand('insertHTML', false, video);
                this.updateTextarea();
                
                // Show success notification
                this.showNotification('Video uploaded successfully!', 'success');
            } else {
                throw new Error(result.error || 'Upload error: ' + response.statusText);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Video upload error: ' + error.message, 'error');
        } finally {
            this.hideVideoUploadProgress();
        }
    }

    insertYouTubeVideo(url) {
        const videoId = this.extractYouTubeVideoId(url);
        if (videoId) {
            // Restore saved cursor position
            this.editor.focus();
            
            if (this.savedRange) {
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(this.savedRange);
            }
            
            const iframe = `<div class="video-container">
                <iframe src="https://www.youtube.com/embed/${videoId}" 
                        frameborder="0" 
                        allowfullscreen
                        style="width: 560px; height: 315px; border: none;">
                </iframe>
            </div><br><br>`;
            
        // Insert HTML at saved position
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            
            // Create element from HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = iframe;
            const videoElement = tempDiv.firstChild;
            
            // Insert element at current position
            range.deleteContents();
            range.insertNode(videoElement);
            
            // Move cursor after inserted element
            range.setStartAfter(videoElement);
            range.setEndAfter(videoElement);
            selection.removeAllRanges();
            selection.addRange(range);
            
            this.updateTextarea();
            this.showNotification('YouTube video added successfully!', 'success');
        } else {
            alert('Invalid YouTube video URL. Please enter a correct link.');
        }
    }

    showVideoUploadProgress() {
        // Create progress indicator
        const progressDiv = document.createElement('div');
        progressDiv.id = 'wysiwyg-video-upload-progress';
        progressDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 10000;
            text-align: center;
        `;
        progressDiv.innerHTML = `
            <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>
            Uploading video...
        `;
        
        document.body.appendChild(progressDiv);
    }

    hideVideoUploadProgress() {
        const progressDiv = document.getElementById('wysiwyg-video-upload-progress');
        if (progressDiv) {
            document.body.removeChild(progressDiv);
        }
    }

    extractYouTubeVideoId(url) {
        // Regular expressions for various YouTube URL formats
        const patterns = [
            /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
            /youtube\.com\/watch\?.*v=([^&\n?#]+)/,
            /youtu\.be\/([^&\n?#]+)/,
            /youtube\.com\/embed\/([^&\n?#]+)/
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }

        return null;
    }

    toggleSourceView() {
        if (this.sourceMode) {
            // Switch back to edit mode
            this.editor.innerHTML = this.editor.textContent;
            this.editor.contentEditable = true;
            this.sourceMode = false;
        } else {
            // Switch to HTML view mode
            this.editor.contentEditable = false;
            this.editor.textContent = this.editor.innerHTML;
            this.sourceMode = true;
        }
    }

    updateTextarea() {
        this.textarea.value = this.editor.innerHTML;
    }

    updateButtonStates() {
        const buttons = this.toolbar.querySelectorAll('.wysiwyg-btn');
        buttons.forEach(button => {
            const command = button.getAttribute('data-command');
            if (command) {
                try {
                    const isActive = document.queryCommandState(command);
                    button.style.background = isActive ? '#007bff' : 'white';
                    button.style.color = isActive ? 'white' : 'black';
                } catch (e) {
                    // Some commands may not be supported
                }
            }
        });
    }

    setupEventListeners() {
        // Update textarea when content changes
        this.editor.addEventListener('input', () => {
            this.updateTextarea();
        });

        this.editor.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = e.clipboardData.getData('text/plain');
            document.execCommand('insertText', false, text);
            this.updateTextarea();
        });

        // Update button states on text selection
        this.editor.addEventListener('mouseup', () => {
            this.updateButtonStates();
        });

        this.editor.addEventListener('keyup', () => {
            this.updateButtonStates();
        });

        // Prevent focus loss when clicking toolbar
        this.toolbar.addEventListener('mousedown', (e) => {
            e.preventDefault();
        });
    }

    // Public methods
    getContent() {
        return this.editor.innerHTML;
    }

    setContent(content) {
        this.editor.innerHTML = content;
        this.updateTextarea();
    }

    focus() {
        this.editor.focus();
    }

    destroy() {
        this.editorContainer.remove();
        this.textarea.style.display = 'block';
    }
}

// Note: Editor is initialized manually in templates to prevent duplication
