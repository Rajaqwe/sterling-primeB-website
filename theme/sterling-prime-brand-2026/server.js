const http=require('http');
const fs=require('fs');
const path=require('path');
const {URL}=require('url');
const PORT=process.env.PORT||3000;
const ROOT=__dirname;
const REPO_ROOT=path.join(ROOT,'..','..');
const QUOTES=path.join(ROOT,'data','quotes.json');

const products=[
{id:'desk-clock-pen',name:'Desk Clock & Pen Holder',category:'Desk Essentials',tag:'Bestseller',image:'/raw-images/DESK CLOCK & PEN HOLDER.jpeg'},
{id:'character-gift-set',name:'Character Gift Set',category:'Gift Sets',tag:'New',image:'/raw-images/CHARACTER GIFT SET.jpeg'},
{id:'care-comfort-kit',name:'Care & Comfort Kit',category:'Employee Gifting',tag:'Popular',image:'/raw-images/CARE & CONFORT KIT.JPEG'},
{id:'clipboard',name:'Premium Clipboard',category:'Desk Essentials',tag:'Bulk Pick',image:'/raw-images/CLIPBOARD.jpeg'},
{id:'coaster-set',name:'Coaster Set',category:'Home & Lifestyle',tag:'Popular',image:'/raw-images/COASTER SET (2).jpeg'},
{id:'branded-pouch',name:'Custom Branded Pouch',category:'Travel & Utility',tag:'Custom',image:'/raw-images/CUSTOM BRANDED POUCH.JPEG'},
{id:'desk-calendar',name:'Desk Calendar',category:'Desk Essentials',tag:'Seasonal',image:'/raw-images/DESK CALENDER.jpeg'},
{id:'desk-clock',name:'Desk Clock',category:'Desk Essentials',tag:'Premium',image:'/raw-images/DESK CLOCK.JPEG'}];

function json(res,status,data){const b=JSON.stringify(data);res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(b)}
function getQuotes(){try{return JSON.parse(fs.readFileSync(QUOTES,'utf8'))}catch{return[]}}
function saveQuotes(v){fs.mkdirSync(path.dirname(QUOTES),{recursive:true});fs.writeFileSync(QUOTES,JSON.stringify(v,null,2))}
function mime(file){const ext=path.extname(file).toLowerCase();return ext==='.svg'?'image/svg+xml':ext==='.png'?'image/png':ext==='.webp'?'image/webp':'image/jpeg'}

const server=http.createServer((req,res)=>{
  const u=new URL(req.url,'http://localhost');
  if(req.method==='GET'&&u.pathname==='/api/health')return json(res,200,{ok:true,service:'sterling-prime-theme'});
  if(req.method==='GET'&&u.pathname==='/api/products')return json(res,200,{products});
  if(req.method==='POST'&&u.pathname==='/api/quotes'){
    let raw='';req.on('data',c=>raw+=c);req.on('end',()=>{
      try{
        const p=JSON.parse(raw||'{}');
        const required=['name','company','email','phone','giftType','quantity'];
        if(required.some(k=>!p[k]))return json(res,400,{ok:false,message:'Please complete the required fields.'});
        const list=getQuotes();const id='Q-'+Date.now();
        list.unshift({...p,id,createdAt:new Date().toISOString()});saveQuotes(list);
        json(res,201,{ok:true,quoteId:id,message:'Thank you! Our team will reach out within 24 hours.'});
      }catch(e){json(res,400,{ok:false,message:'Invalid request.'})}
    });return;
  }
  if(u.pathname.startsWith('/raw-images/')){
    const rel=decodeURIComponent(u.pathname.slice('/raw-images/'.length));
    return fs.readFile(path.join(REPO_ROOT,'raw images',rel),(err,data)=>{if(err){res.writeHead(404);return res.end('Not found')}res.writeHead(200,{'Content-Type':mime(rel)});res.end(data)});
  }
  fs.readFile(path.join(ROOT,'index.html'),(err,data)=>{if(err){res.writeHead(500);return res.end('Theme file missing')}res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(data)});
});
server.listen(PORT,()=>console.log('Sterling Prime theme running at http://localhost:'+PORT));