const API_BASE = "https://flowchat-production.up.railway.app";
let currentUserId = 1;
let currentChatId = 1;
let messages = [];
let organizedView = false;
let currentCategory = 'all';
let categorizedData = {};

function categorizeMessages(messages) {
    const categories = {
        text: [],
        links: [],
        images: [],
        pdf: [],
        ppt: [],
        other_files: []
    };
    
    messages.forEach(msg => {
        if (msg.message_type === 'text') {
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            if (urlRegex.test(msg.content)) {
                categories.links.push(msg);
            } else {
                categories.text.push(msg);
            }
        } else if (msg.message_type === 'file') {
            const ext = msg.file_type?.toLowerCase();
            if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
                categories.images.push(msg);
            } else if (ext === 'pdf') {
                categories.pdf.push(msg);
            } else if (['ppt', 'pptx'].includes(ext)) {
                categories.ppt.push(msg);
            } else {
                categories.other_files.push(msg);
            }
        }
    });
    
    return categories;
}

function toggleOrganizer() {
    const normalView = document.getElementById('messageContainer');
    const organizedViewElement = document.getElementById('organizedView');
    
    organizedView = !organizedView;
    
    if (organizedView) {
        categorizedData = categorizeMessages(messages);
        updateCategoryCounts();
        normalView.style.display = 'none';
        organizedViewElement.style.display = 'block';
    } else {
        normalView.style.display = 'block';
        organizedViewElement.style.display = 'none';
        loadMessages();
    }
}

function updateCategoryCounts() {
    document.getElementById('linksCount').textContent = categorizedData.links.length;
    document.getElementById('pdfCount').textContent = categorizedData.pdf.length;
    document.getElementById('pptCount').textContent = categorizedData.ppt.length;
    document.getElementById('imagesCount').textContent = categorizedData.images.length;
}

function showCategory(category) {
    currentCategory = category;
    const container = document.getElementById('messageContainer');
    const organizedViewElement = document.getElementById('organizedView');
    
    organizedViewElement.style.display = 'none';
    container.style.display = 'block';
    container.innerHTML = `<div class="category-header">
        <button onclick="backToOrganizer()">← Back to Organizer</button>
        <h3>${category.toUpperCase()} (${categorizedData[category].length} items)</h3>
    </div>`;
    
    categorizedData[category].forEach(message => {
        // FIX: Use correct message type classification
        const typeClass = (parseInt(message.sender_id) === currentUserId) ? 'sent' : 'received';

        displayMessage(message.content, typeClass, message);
    });
}

function backToOrganizer() {
    document.getElementById('messageContainer').style.display = 'none';
    document.getElementById('organizedView').style.display = 'block';
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    if (!content) return;

    const messageData = {
        content: content,
        chat_id: currentChatId,
        sender_id: 1,
        message_type: "text"
    };

    try {
        const response = await fetch('${API_BASE}/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(messageData)
        });

        if (response.ok) {
            messageInput.value = '';
            // Immediately show sent message in blue
            displayMessage(content, 'sent', {
                content: content,
                sender_id: 1,
                message_type: 'text',
                created_at: new Date().toISOString()
            });
            // Refresh from server after a short delay
            setTimeout(() => loadMessages(true), 200);
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

// Instagram-style timestamp display with click to show
// REPLACE the displayMessage function with this corrected version:
function displayMessage(content, type, messageObj = null) {
    const container = document.getElementById('messageContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    let timeStr = '';
    if (messageObj && messageObj.created_at) {
        const msgTime = new Date(messageObj.created_at);
        timeStr = msgTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } else {
        const now = new Date();
        timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    let messageContent = content;

    // File message with download button
    if (messageObj && messageObj.message_type === 'file') {
        messageContent = `
            <div class="file-message">
                <span>📎 ${messageObj.content}</span>
                <button class="download-btn" onclick="window.open('/files/${messageObj.content}', '_blank')">
                    💾 Download
                </button>
            </div>
        `;
    }
    // Text with clickable links
    else if (messageObj && messageObj.message_type === 'text') {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const urls = content.match(urlRegex);
        if (urls) {
            messageContent = `
                <div class="text-with-links">
                    <div class="message-text">${content}</div>
                    <div class="link-buttons">
                        ${urls.map(url => `
                            <button class="link-btn" onclick="window.open('${url}', '_blank')">
                                🔗 Open Link
                            </button>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    // FIX: Correct timestamp behavior - hidden by default, click to show
    messageDiv.innerHTML = `
        <div onclick="toggleTimestamp('${messageId}')">${messageContent}</div>
        <div class="message-time" id="${messageId}" style="display: none;">${timeStr}</div>
    `;

    container.appendChild(messageDiv);
}

// Check if timestamp should be shown (Instagram-style time gaps)
function shouldShowTimestamp(messageObj) {
    if (!messageObj || !messageObj.created_at) return false;
    
    const msgTime = new Date(messageObj.created_at);
    const now = new Date();
    const timeDiff = (now - msgTime) / (1000 * 60); // minutes
    
    // Show timestamp if message is older than 5 minutes
    return timeDiff > 5;
}

// Toggle timestamp visibility on click
function toggleTimestamp(messageId) {
    const timestampEl = document.getElementById(messageId);
    if (timestampEl) {
        timestampEl.style.display = timestampEl.style.display === 'none' ? 'block' : 'none';
    }
}

async function loadMessages(scrollToBottom = false) {
    try {
        const response = await fetch(`${API_BASE}/api/messages/chat/${currentChatId}`);
        const data = await response.json();
        const container = document.getElementById('messageContainer');
        container.innerHTML = '';
        messages = data.messages;

        messages.forEach(message => {
            // FIX: Ensure proper integer comparison
            const typeClass = (parseInt(message.sender_id) === currentUserId) ? 'sent' : 'received';

            displayMessage(message.content, typeClass, message);
        });

        if (scrollToBottom) {
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 100);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

// REPLACE sendMessage function with this fixed version:
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    if (!content) return;

    const messageData = {
        content: content,
        chat_id: currentChatId,
        sender_id: 1,
        message_type: "text"
    };

    try {
        const response = await fetch('${API_BASE}/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(messageData)
        });

        if (response.ok) {
            messageInput.value = '';
            // FIX: Only reload messages once, no double rendering
            setTimeout(() => loadMessages(true), 100);
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const fileInput = document.getElementById('fileInput');

    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    fileInput.addEventListener('change', async function() {
        const file = this.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('chat_id', currentChatId);
        formData.append('sender_id', 1);

        try {
            const response = await fetch('${API_BASE}/api/messages/send-file', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                alert('File uploaded successfully!');
                setTimeout(() => loadMessages(true), 200);
            } else {
                alert('File upload failed!');
            }
        } catch (error) {
            console.error('File upload error:', error);
            alert('File upload error!');
        }
        this.value = "";
    });

    loadMessages();
});

function searchMessages() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const filter = document.getElementById('searchFilter').value;
    
    let filteredMessages = messages;
    
    if (filter !== 'all') {
        const categories = categorizeMessages(messages);
        filteredMessages = categories[filter] || [];
    }
    
    if (searchTerm) {
        filteredMessages = filteredMessages.filter(msg => 
            msg.content.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
    
    const container = document.getElementById('messageContainer');
    container.innerHTML = `
        <div class="search-results">
            Found ${filteredMessages.length} results for "${filter}" ${searchTerm ? `containing "${searchTerm}"` : ''}
            <button onclick="loadMessages()" style="float: right;">Clear Search</button>
        </div>
    `;
    
    filteredMessages.forEach(message => {
        const typeClass = (parseInt(message.sender_id) === currentUserId) ? 'sent' : 'received';

        displayMessage(message.content, typeClass, message);
    });
}
