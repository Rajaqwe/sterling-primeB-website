/* Sterling Prime upgrade layer: quote list, lead form, trust sections, live counts */
(function(){
/* Add REAL clients/testimonials here; sections stay hidden while these are empty.
   CLIENTS=[{name:'Acme Ltd',logo:'raw%20images/clients/acme.png'}]  TESTIMONIALS=[{quote:'...',who:'Name, Role, Company'}] */
var CLIENTS=[],TESTIMONIALS=[];
var BRANDS=['boAt','Noise','JBL','Portronics','Borosil','Milton','Wonderchef','Lifelong','Pebble','Samsonite','Adidas','Cross','Carlton London','Ferns N Petals','Procter'];
var TILES=[['Employee joining kits','🎒','employee-onboarding-kits'],['Festive & Diwali hampers','🪔','festive-hampers-gourmet'],['Healthcare & pharma','⚕️','healthcare-medical'],['Awards & recognition','🏆','trophies-awards-medals'],['Executive gift sets','🎁','executive-combo-sets'],['Tech & gadgets','🔌','smart-tech-accessories']];
var EMAIL='pmanji2@gmail.com',WA='917041614713',KEY='sp_quote_v1',Q=[];
try{Q=JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){}
var $=function(s,r){return(r||document).querySelector(s)};
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
function save(){try{localStorage.setItem(KEY,JSON.stringify(Q))}catch(e){}}
function info(c){var im=$('img',c),b=$('.brand-subtitle span',c);
 var sku=c.getAttribute('data-sku')||(($('.sku-badge',c)||{}).textContent||'').trim();
 var name=($('.product-name',c)||{}).textContent||'Item';
 return{k:sku||name,name:name.trim(),sku:sku,brand:b?b.textContent:'',cat:c.getAttribute('data-category-name')||'',img:c.getAttribute('data-img')||(im&&im.getAttribute('src'))||''}}
function has(k){return Q.some(function(i){return i.k===k})}
function toggle(i){Q=has(i.k)?Q.filter(function(x){return x.k!==i.k}):Q.concat(i);save();sync()}
function enhance(c){if(c.dataset.q)return;var a=$('.card-actions',c);if(!a)return;c.dataset.q=1;
 var b=document.createElement('button');b.type='button';b.className='btn-quote';
 b.onclick=function(e){e.stopPropagation();toggle(info(c))};a.insertBefore(b,a.firstChild);label(c)}
function label(c){var b=$('.btn-quote',c);if(!b)return;var on=has(info(c).k);b.className='btn-quote'+(on?' on':'');b.textContent=on?'✓ In quote':'+ Add to quote'}
function sync(){document.querySelectorAll('.product-card').forEach(label);
 var f=$('#q-fab');f.style.display=Q.length?'block':'none';$('b',f).textContent=Q.length;
 $('#q-list').innerHTML=Q.length?Q.map(function(i,n){return'<div class="q-item"><img src="'+esc(i.img)+'" alt=""><div><b>'+esc(i.name)+'</b><br><small>'+esc(i.brand)+(i.sku?' · '+esc(i.sku):'')+'</small></div><button aria-label="Remove" data-n="'+n+'">×</button></div>'}).join(''):'<p style="padding:20px;color:#666">Your quote list is empty. Tap “Add to quote” on any product.</p>'}
function lines(){return Q.map(function(i,n){return(n+1)+'. '+i.name+(i.sku?' ['+i.sku+']':'')+' – '+i.brand}).join('\n')}
function send(data,box,done){var m=$('.q-msg',box);m.className='q-msg';m.textContent='Sending…';
 data._subject='Sterling Prime website enquiry – '+(data.name||'');data._template='table';data._captcha='false';
 fetch('https://formsubmit.co/ajax/'+EMAIL,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(data)})
 .then(function(r){return r.json()}).then(function(r){if(!(r.success===true||r.success==='true'))throw 0;
  m.className='q-msg ok';m.textContent='Thank you! We have your request and will reply shortly.';done&&done()})
 .catch(function(){m.className='q-msg err';m.textContent='Could not send. Please use the WhatsApp button instead.'})}
function fields(f){var d={};new FormData(f).forEach(function(v,k){d[k]=v});return d}
function build(){
 document.body.insertAdjacentHTML('beforeend','<button id="q-fab" type="button">Quote list<b>0</b></button><div id="q-dim"></div>'+
 '<aside id="q-drawer" aria-label="Quote list"><header><strong>Your quote list</strong><button id="q-close" aria-label="Close">×</button></header><div id="q-list"></div>'+
 '<form id="q-form"><div class="row"><input name="name" placeholder="Your name" required><input name="company" placeholder="Company"></div><div class="row"><input name="phone" placeholder="Phone / WhatsApp" required><input name="email" type="email" placeholder="Email"></div><textarea name="notes" rows="2" placeholder="Quantity, branding (logo/engraving), delivery city, date needed"></textarea><div class="q-msg"></div><button class="q-send">Send quote request</button><a class="q-wa" id="q-wa" target="_blank" rel="noopener">Send on WhatsApp instead</a></form></aside>');
 var d=$('#q-drawer'),dim=$('#q-dim');
 function open(o){d.classList.toggle('open',o);dim.classList.toggle('open',o)}
 $('#q-fab').onclick=function(){open(1)};$('#q-close').onclick=dim.onclick=function(){open(0)};
 $('#q-list').onclick=function(e){var n=e.target.getAttribute('data-n');if(n!==null){Q.splice(+n,1);save();sync()}};
 $('#q-wa').onmouseenter=$('#q-wa').onfocus=$('#q-wa').ontouchstart=function(){var f=fields($('#q-form'));
  this.href='https://wa.me/'+WA+'?text='+encodeURIComponent('Hi Sterling Prime, please share a quotation for:\n\n'+lines().slice(0,1400)+'\n\nName: '+(f.name||'')+'\nCompany: '+(f.company||'')+'\n'+(f.notes||''))};
 $('#q-form').onsubmit=function(e){e.preventDefault();if(!Q.length){var m=$('.q-msg',this);m.className='q-msg err';m.textContent='Add at least one product first.';return}
  var f=this,x=fields(f);x.items=lines();send(x,f,function(){Q=[];save();sync();f.reset()})}}
function sections(){var a=$('#about');if(!a)return;
 a.insertAdjacentHTML('beforebegin','<section class="up-sec" id="how"><h2>How it works</h2><p class="sub">From shortlist to doorstep, with branding handled for you.</p><div class="steps">'+
 [['Choose','Browse and tap “Add to quote” on everything you like.'],['Share details','Send quantities and your logo with one request.'],['Approve mockup','Review the branded mockup before production.'],['Delivered pan-India','Typically 5–7 days from order confirmation.']].map(function(s,i){return'<div class="step"><span>'+(i+1)+'</span><h3>'+s[0]+'</h3><p>'+s[1]+'</p></div>'}).join('')+'</div></section>'+
 '<section class="up-sec faq" id="faq"><h2>Common questions</h2><p class="sub">Quick answers for corporate buyers.</p>'+
 [['How long does delivery take?','Typically 5–7 days from the date of order confirmation, anywhere in India.'],['Can you brand the products?','Yes. Custom corporate branding, laser engraving and bulk B2B packaging are available on our products.'],['How do I get pricing?','Prices depend on quantity and branding. Add items to your quote list or use the form below and we will send bulk pricing.'],['Can I get a full brand catalogue?','Yes. Ask for the master range or individual brand catalogues (boAt, Noise, Borosil, Milton, Samsonite and more) via WhatsApp or email.']].map(function(q){return'<details><summary>'+q[0]+'</summary><p>'+q[1]+'</p></details>'}).join('')+'</section>'+
 '<section class="up-sec" id="enquire"><h2>Tell us what you need</h2><p class="sub">One short form. We reply with options and bulk pricing.</p><form class="lead-form" id="lead"><div class="row"><input name="name" placeholder="Your name" required><input name="company" placeholder="Company"></div><div class="row"><input name="phone" placeholder="Phone / WhatsApp" required><input name="email" type="email" placeholder="Email"></div><select name="occasion"><option>Occasion…</option><option>Employee joining kits</option><option>Festive / Diwali gifting</option><option>Client gifts</option><option>Events &amp; conferences</option><option>Healthcare / pharma communication</option><option>Other</option></select><textarea name="notes" rows="3" placeholder="Approx. quantity, budget per piece, date needed"></textarea><div class="q-msg"></div><button class="q-send">Request a quote</button></form></section>');
 $('#lead').onsubmit=function(e){e.preventDefault();var f=this;send(fields(f),f,function(){f.reset()})}}
function hero(){var h=$('.hero');if(h)h.insertAdjacentHTML('beforeend','<div class="hero-cta"><a class="p" href="#gallery">Browse catalogue</a><a class="s" href="#enquire">Get a quote</a></div>')}
function extras(){var g=$('#gallery');if(g)g.insertAdjacentHTML('beforebegin','<section class="up-sec" id="need"><h2>Shop by need</h2><p class="sub">Jump straight to what you are gifting for.</p><div class="tiles">'+TILES.map(function(t){return'<button type="button" class="tile" data-cat="'+t[2]+'"><span>'+t[1]+'</span>'+t[0]+'</button>'}).join('')+'</div></section>');
 var n=$('#need');if(n)n.onclick=function(e){var t=e.target.closest('.tile');if(!t)return;var b=$('.cat-btn[data-cat="'+t.getAttribute('data-cat')+'"]');if(b)b.click();$('#gallery').scrollIntoView({behavior:'smooth'})};
 var h=$('#how');if(!h)return;var x='<section class="up-sec" id="brands"><h2>Brands in our catalogue</h2><p class="sub">Choose from leading brands alongside our in-house range.</p><div class="chips">'+BRANDS.map(function(b){return'<span>'+esc(b)+'</span>'}).join('')+'</div></section>';
 if(CLIENTS.length)x+='<section class="up-sec" id="clients"><h2>Trusted by</h2><div class="chips">'+CLIENTS.map(function(c){return c.logo?'<img src="'+esc(c.logo)+'" alt="'+esc(c.name)+'" height="44">':'<span>'+esc(c.name)+'</span>'}).join('')+'</div></section>';
 if(TESTIMONIALS.length)x+='<section class="up-sec" id="voices"><h2>What clients say</h2><div class="steps">'+TESTIMONIALS.map(function(t){return'<div class="step"><p>“'+esc(t.quote)+'”</p><small>'+esc(t.who)+'</small></div>'}).join('')+'</div></section>';
 h.insertAdjacentHTML('beforebegin',x)}
function init(){build();sections();extras();hero();var g=$('#galleryGrid');
 if(g){g.querySelectorAll('.product-card').forEach(enhance);
  new MutationObserver(function(){g.querySelectorAll('.product-card:not([data-q])').forEach(enhance)}).observe(g,{childList:true})}
 sync()}
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init):init();
})();
