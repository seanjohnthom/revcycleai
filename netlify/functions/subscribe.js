// Netlify Function — MailerLite subscriber proxy
// Keeps API key server-side (set MAILERLITE_API_KEY in Netlify env vars)
// Optional: set MAILERLITE_GROUP_ID to add subscribers to a specific group

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const { email, name, source, resource } = JSON.parse(event.body || '{}');

  if (!email || !email.includes('@')) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Valid email required' }),
    };
  }

  const API_KEY  = process.env.MAILERLITE_API_KEY;
  const GROUP_ID = process.env.MAILERLITE_GROUP_ID;

  if (!API_KEY) {
    console.error('MAILERLITE_API_KEY not set');
    return { statusCode: 500, body: JSON.stringify({ error: 'Server config error' }) };
  }

  const payload = {
    email,
    fields: {
      name: name || '',
      last_name: '',
    },
    groups: GROUP_ID ? [GROUP_ID] : [],
    status: 'active',
  };

  try {
    const res = await fetch('https://connect.mailerlite.com/api/subscribers', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok || res.status === 200 || res.status === 201) {
      console.log(`Subscribed: ${email} | Source: ${source || 'unknown'} | Resource: ${resource || 'none'}`);
      
      // Map resource name to download file
      const resourceMap = {
        'prior-auth-checklist-2026': '/downloads/prior-auth-checklist-2026.pdf',
        'leakage-calculator': '/downloads/leakage-calculator.xlsx',
        'appeal-letter-template': '/downloads/appeal-letter-template.pdf',
        'ppo-network-map': '/downloads/ppo-network-map.pdf',
        'cpt-changes-2026': '/downloads/cpt-changes-2026.pdf',
        'denial-tracking-dashboard': '/downloads/denial-tracking-dashboard.xlsx',
      };
      
      const downloadUrl = resource && resourceMap[resource] ? resourceMap[resource] : null;
      
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          success: true, 
          email,
          downloadUrl 
        }),
      };
    }

    // MailerLite returns 409 if already subscribed — treat as success
    if (res.status === 409) {
      const resourceMap = {
        'prior-auth-checklist-2026': '/downloads/prior-auth-checklist-2026.pdf',
        'leakage-calculator': '/downloads/leakage-calculator.xlsx',
        'appeal-letter-template': '/downloads/appeal-letter-template.pdf',
        'ppo-network-map': '/downloads/ppo-network-map.pdf',
        'cpt-changes-2026': '/downloads/cpt-changes-2026.pdf',
        'denial-tracking-dashboard': '/downloads/denial-tracking-dashboard.xlsx',
      };
      
      const downloadUrl = resource && resourceMap[resource] ? resourceMap[resource] : null;
      
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          success: true, 
          email, 
          already_subscribed: true,
          downloadUrl 
        }),
      };
    }

    console.error('MailerLite error:', data);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: data?.message || 'Subscription failed' }),
    };
  } catch (err) {
    console.error('Fetch error:', err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Network error' }),
    };
  }
};
