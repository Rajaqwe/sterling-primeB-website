module.exports = async (req,res) => {
  if(req.method !== 'POST') return res.status(405).json({ok:false,message:'Method not allowed'});
  try {
    const p = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const required = ['name','company','email','phone','giftType','quantity'];
    if(required.some(k => !p[k])) return res.status(400).json({ok:false,message:'Please complete the required fields.'});
    if(!process.env.RESEND_API_KEY) return res.status(503).json({ok:false,message:'Email delivery is not configured yet.',code:'EMAIL_NOT_CONFIGURED'});
    const safe = v => String(v ?? '').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const html = Object.entries(p).map(([k,v]) => '<p><strong>'+safe(k)+'</strong>: '+safe(v)+'</p>').join('');
    const response = await fetch('https://api.resend.com/emails',{
      method:'POST',
      headers:{Authorization:'Bearer '+process.env.RESEND_API_KEY,'Content-Type':'application/json'},
      body:JSON.stringify({
        from:process.env.QUOTE_FROM_EMAIL || 'Sterling Prime Website <onboarding@resend.dev>',
        to:[process.env.QUOTE_TO_EMAIL || 'info@mysterling.in'],
        subject:'New Sterling Prime Quote Enquiry',
        html
      })
    });
    const data = await response.json();
    if(!response.ok) return res.status(502).json({ok:false,message:'Email delivery failed. Please try again or call us.'});
    return res.status(201).json({ok:true,message:'Thank you! Our team will reach out within 24 hours.'});
  } catch(e) {
    return res.status(400).json({ok:false,message:'Invalid request.'});
  }
};