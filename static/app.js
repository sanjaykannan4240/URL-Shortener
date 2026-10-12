const form = document.querySelector('#shorten-form');
const urlInput = document.querySelector('#url');
const customToggle = document.querySelector('#custom-toggle');
const customCode = document.querySelector('#custom-code');
const message = document.querySelector('#message');
const result = document.querySelector('#result');
const shortUrl = document.querySelector('#short-url');
const originalUrl = document.querySelector('#original-url');
const copyButton = document.querySelector('#copy-button');
const list = document.querySelector('#links-list');

customToggle.addEventListener('change', () => {
  customCode.disabled = !customToggle.checked;
  if (customToggle.checked) customCode.focus();
  else customCode.value = '';
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.textContent = '';
  const button = document.querySelector('#submit-button');
  button.disabled = true;
  button.textContent = 'Creating…';
  try {
    const response = await fetch('/api/shorten', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url:urlInput.value, custom_code:customCode.value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not create short URL.');
    shortUrl.href = data.short_url;
    shortUrl.textContent = data.short_url;
    originalUrl.textContent = data.original_url;
    result.classList.remove('hidden');
    form.reset(); customCode.disabled = true;
    await loadLinks();
  } catch (error) { message.textContent = error.message; }
  finally { button.disabled = false; button.innerHTML = 'Shorten link <span>→</span>'; }
});

copyButton.addEventListener('click', async () => {
  await navigator.clipboard.writeText(shortUrl.href);
  copyButton.textContent = 'Copied!';
  setTimeout(() => { copyButton.textContent = 'Copy'; }, 1600);
});

document.querySelector('#refresh-button').addEventListener('click', loadLinks);

async function loadLinks() {
  const response = await fetch('/api/urls');
  const data = await response.json();
  if (!data.urls.length) { list.innerHTML = '<div class="empty-state">No links yet — your recent links will appear here.</div>'; return; }
  list.innerHTML = data.urls.map(item => `<article class="link-item"><div class="link-main"><a href="${item.short_url}" target="_blank" rel="noopener">${item.short_url}</a><p title="${escapeHtml(item.original_url)}">${escapeHtml(item.original_url)}</p></div><div class="link-meta">${item.clicks} click${item.clicks === 1 ? '' : 's'}<br>${formatDate(item.created_at)}</div></article>`).join('');
}
function formatDate(value) { const date = new Date(value.replace(' ', 'T') + 'Z'); return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'}); }
function escapeHtml(value) { return value.replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char])); }
loadLinks();
