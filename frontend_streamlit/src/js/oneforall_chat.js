const BACKEND_URL = '{{BACKEND_URL}}';
const TOKEN = '{{TOKEN}}';
const headers = { 'Authorization': `Bearer ${TOKEN}` };

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const fileInput = document.getElementById('fileInput');
const attachBtn = document.getElementById('attachBtn');
const existingBtn = document.getElementById('existingBtn');
const scrapeBtn = document.getElementById('scrapeBtn');
const existingDiv = document.getElementById('existingDocs');
const scrapeDiv = document.getElementById('scrapeUrl');

let selectedDocs = [];

async function fetchMessages(chat_id) {
  const res = await fetch(`${BACKEND_URL}/chats/${chat_id}/messages`, { headers });
  const data = await res.json();
  messagesEl.innerHTML = '';
  data.messages.forEach(m => {
    const div = document.createElement('div');
    div.className = `message ${m.role}`;
    div.textContent = m.content;
    messagesEl.appendChild(div);
  });
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(chat_id, content) {
  // add user message
  await fetch(`${BACKEND_URL}/chats/${chat_id}/add_message`, {
    method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id, role: 'user', content })
  });

  // fetch assistant response
  const payload = { chat_id, doc_ids: selectedDocs, messages: [{ role:'user', content }] };
  const res = await fetch(`${BACKEND_URL}/unified_chat`, {
    method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) { alert('Error: ' + res.status); return; }
  fetchMessages(chat_id);
}

// Replace with actual chat_id loading logic
const chat_id = window.chat_id || null;
if (chat_id) fetchMessages(chat_id);

sendBtn.onclick = () => {
  const text = inputEl.value;
  if (!text.trim()) return;
  sendMessage(chat_id, text);
  inputEl.value = '';
};

attachBtn.onclick = () => fileInput.click();
fileInput.onchange = async () => {
  const files = fileInput.files;
  for (let f of files) {
    const form = new FormData(); form.append('file', f);
    await fetch(`${BACKEND_URL}/docs/upload`, { method:'POST', headers, body:form });
  }
  fileInput.value = null;
};
existingBtn.onclick = async () => {
  const isHidden = existingDiv.style.display === 'none';
  existingDiv.style.display = isHidden ? 'block' : 'none';

  // Only fetch and render if the div is being shown and is empty
  if (isHidden && existingDiv.innerHTML.trim() === '') {
    existingDiv.innerHTML = '<span>Loading documents...</span>';
    try {
      const res = await fetch(`${BACKEND_URL}/docs/list`, { headers });
      if (!res.ok) {
        existingDiv.innerHTML = '<span>Failed to load documents.</span>';
        return;
      }
      const docs = await res.json();
      existingDiv.innerHTML = ''; // Clear loading message

      if (docs.length === 0) {
        existingDiv.innerHTML = '<span>No documents found.</span>';
        return;
      }

      docs.forEach(doc => {
        const docEl = document.createElement('div');
        docEl.className = 'doc-item';
        docEl.setAttribute('data-doc-id', doc.doc_id);
        
        const title = doc.doc_title || 'Untitled';
        const visibility = doc.visibility || 'private';
        const createdAt = new Date(doc.created_at).toLocaleString();

        docEl.innerHTML = `
          <div class="doc-title">${title}</div>
          <div class="doc-meta">
            <span>${visibility}</span> | <span>${createdAt}</span>
          </div>
        `;

        // Check if this doc is already selected
        if (selectedDocs.includes(doc.doc_id)) {
            docEl.classList.add('selected');
        }

        docEl.onclick = () => {
          const docId = docEl.getAttribute('data-doc-id');
          if (docEl.classList.contains('selected')) {
            // Deselect
            docEl.classList.remove('selected');
            selectedDocs = selectedDocs.filter(id => id !== docId);
          } else {
            // Select
            docEl.classList.add('selected');
            selectedDocs.push(docId);
          }
        };
        existingDiv.appendChild(docEl);
      });
    } catch (error) {
      console.error("Error fetching documents:", error);
      existingDiv.innerHTML = '<span>An error occurred.</span>';
    }
  }
};


scrapeBtn.onclick = () => {
  scrapeDiv.style.display = scrapeDiv.style.display === 'none' ? 'block' : 'none';
  if (!scrapeDiv.querySelector('input')) {
    const inp = document.createElement('input'); inp.type='text'; inp.placeholder='URL to scrape';
    const btn = document.createElement('button'); btn.textContent='Go';
    btn.onclick = async () => {
      const url = inp.value;
      await fetch(`${BACKEND_URL}/scrape`, { method:'POST', headers:{...headers,'Content-Type':'application/json'}, body:JSON.stringify({url}) });
      scrapeDiv.style.display='none';
    };
    scrapeDiv.append(inp, btn);
  }
};