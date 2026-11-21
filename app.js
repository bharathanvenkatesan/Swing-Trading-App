async function api(url, options={}) {
  const response = await fetch(url, {headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
  let body={}; try{body=await response.json()}catch(e){}
  if(!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}
async function loadDashboard(){
  const banner=document.getElementById("modeBanner"); if(!banner)return;
  try{
    const d=await api("/api/dashboard");
    banner.textContent=d.mode;
    document.getElementById("watchCount").textContent=d.watchlist.length;
    document.getElementById("holdingCount").textContent=d.holdings.length;
    document.getElementById("snapshotRows").innerHTML=d.snapshot.map(x=>`<tr><td><b>${x.symbol}</b></td><td>${x.name}</td><td>₹${Number(x.price).toLocaleString("en-IN")}</td><td>${x.change_pct>0?"+":""}${x.change_pct}%</td><td>${x.source}</td></tr>`).join("");
    document.getElementById("watchRows").innerHTML=d.watchlist.map(x=>`<li>${x.symbol}<button class="linkbtn" onclick="removeWatch('${x.symbol}')">Remove</button></li>`).join("") || '<li class="muted">No symbols yet.</li>';
    document.getElementById("holdRows").textContent=d.holdings.length?d.holdings.map(x=>`${x.symbol} · ${x.quantity} shares · ${x.broker}`).join(" | "):"No holdings synced yet. Connect a broker in Settings to get started.";
  }catch(e){banner.textContent=e.message}
}
async function addWatch(){
  const el=document.getElementById("watchSymbol"), symbol=el.value.trim().toUpperCase(); if(!symbol)return;
  try{await api("/api/watchlist",{method:"POST",body:JSON.stringify({symbol})});el.value="";loadDashboard()}catch(e){alert(e.message)}
}
async function removeWatch(symbol){await api("/api/watchlist/"+encodeURIComponent(symbol),{method:"DELETE"});loadDashboard()}
async function saveSecret(key){
  const input=document.getElementById(key), value=input.value.trim();if(!value){alert("Enter a credential first.");return}
  try{const r=await api("/api/settings",{method:"POST",body:JSON.stringify({key,value})});input.value="";document.getElementById(key+"_status").textContent=r.message;loadSettings()}catch(e){alert(e.message)}
}
async function removeSecret(key){
  if(!confirm("Disconnect and delete this saved credential?"))return;
  try{await api("/api/settings/"+key,{method:"DELETE"});loadSettings()}catch(e){alert(e.message)}
}
async function loadSettings(){
  if(!document.getElementById("gemini_api_key_status"))return;
  try{const d=await api("/api/settings");for(const key of ["gemini_api_key","groq_api_key","upstox_access_token"]){const s=d.settings[key];document.getElementById(key+"_status").textContent=s?.configured?`Saved securely · ${s.masked}`:"Not configured";}}catch(e){}
}
async function testUpstox(){
  const el=document.getElementById("upstoxResult");el.textContent="Testing…";
  try{const r=await api("/api/connections/upstox/test",{method:"POST"});el.textContent=r.ok?`Connected: ${r.account}`:r.error}catch(e){el.textContent=e.message}
}
document.addEventListener("DOMContentLoaded",()=>{loadDashboard();loadSettings()});
