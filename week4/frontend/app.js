async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes(query = '') {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = query ? `/notes/search/?q=${encodeURIComponent(query)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    const text = document.createElement('span');
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const nextTitle = prompt('New title', n.title);
      if (nextTitle === null) return;
      const nextContent = prompt('New content', n.content);
      if (nextContent === null) return;
      await fetchJSON(`/notes/${n.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: nextTitle, content: nextContent }),
      });
      loadNotes(query);
    };
    li.appendChild(editBtn);

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = async () => {
      await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes(query);
    };
    li.appendChild(deleteBtn);
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('note-search');
  const searchForm = document.getElementById('note-search-form');
  const searchClear = document.getElementById('note-search-clear');

  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes(searchInput.value.trim());
  });

  searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loadNotes(searchInput.value.trim());
  });

  searchClear.addEventListener('click', async () => {
    searchInput.value = '';
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  loadNotes();
  loadActions();
});
