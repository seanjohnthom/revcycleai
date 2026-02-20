// RevCycleAI — MailerLite subscribe handler
// Used across all pages. Forms call subscribeEmail(email, name, source, resource).

async function subscribeEmail(email, name, source, resource) {
  const res = await fetch('/.netlify/functions/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email, 
      name: name || '', 
      source: source || 'website',
      resource: resource || null
    }),
  });
  return res.json();
}

function initSubscribeForms() {
  document.querySelectorAll('[data-subscribe-form]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput    = form.querySelector('input[type="email"]');
      const nameInput     = form.querySelector('input[name="name"]');
      const resourceInput = form.querySelector('input[name="resource"]');
      const btn           = form.querySelector('button[type="submit"]');
      const source        = form.dataset.subscribeSource || 'website';

      const email    = emailInput?.value?.trim();
      const name     = nameInput?.value?.trim() || '';
      const resource = resourceInput?.value || null;

      if (!email) return;

      const origText = btn.textContent;
      btn.disabled = true;
      btn.textContent = resource ? 'Sending download...' : 'Subscribing...';

      try {
        const data = await subscribeEmail(email, name, source, resource);
        if (data.success) {
          btn.textContent = resource ? '✅ Downloading...' : '✅ You\'re in!';
          btn.style.background = '#10B981';
          emailInput.value = '';
          if (nameInput) nameInput.value = '';
          
          // Trigger download if resource was requested
          if (data.downloadUrl) {
            const link = document.createElement('a');
            link.href = data.downloadUrl;
            link.download = '';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Update success message for downloads
            const msg = document.createElement('p');
            msg.style.cssText = 'font-size:13px;color:#10B981;margin-top:8px;text-align:center;font-weight:600';
            msg.textContent = 'Download started! Check your Downloads folder.';
            form.appendChild(msg);
          } else {
            // Show newsletter success message
            const msg = document.createElement('p');
            msg.style.cssText = 'font-size:13px;color:#10B981;margin-top:8px;text-align:center';
            msg.textContent = 'Check your inbox — first issue arrives Tuesday.';
            form.appendChild(msg);
          }
        } else {
          btn.disabled = false;
          btn.textContent = origText;
          alert(data.error || 'Something went wrong. Please try again.');
        }
      } catch (err) {
        btn.disabled = false;
        btn.textContent = origText;
        console.error(err);
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', initSubscribeForms);
