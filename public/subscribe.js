// RevCycleAI — MailerLite subscribe handler
// Used across all pages. Forms call subscribeEmail(email, name, source).

async function subscribeEmail(email, name, source) {
  const res = await fetch('/.netlify/functions/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name: name || '', source: source || 'website' }),
  });
  return res.json();
}

function initSubscribeForms() {
  document.querySelectorAll('[data-subscribe-form]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput = form.querySelector('input[type="email"]');
      const nameInput  = form.querySelector('input[name="name"]');
      const btn        = form.querySelector('button[type="submit"]');
      const source     = form.dataset.subscribeSource || 'website';

      const email = emailInput?.value?.trim();
      const name  = nameInput?.value?.trim() || '';

      if (!email) return;

      const origText = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Subscribing...';

      try {
        const data = await subscribeEmail(email, name, source);
        if (data.success) {
          btn.textContent = '✅ You\'re in!';
          btn.style.background = '#10B981';
          emailInput.value = '';
          if (nameInput) nameInput.value = '';
          // Show success message
          const msg = document.createElement('p');
          msg.style.cssText = 'font-size:13px;color:#10B981;margin-top:8px;text-align:center';
          msg.textContent = 'Check your inbox — first issue arrives Tuesday.';
          form.appendChild(msg);
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
