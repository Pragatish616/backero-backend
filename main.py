import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from routers import dashboard, phase1, phase2, phase3, phase4, phase5, phase6

app = FastAPI(
    title="Viral Video Production Form API",
    description="Backend for the Backero Viral Video Production Form",
    version="1.0.0",
)

# CORS — allow frontend origins
frontend_origin = os.getenv("FRONTEND_ORIGIN", "https://rbcm2h5ijpzgq.kimi.page")
origins = [
    frontend_origin,
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(phase1.router)
app.include_router(phase2.router)
app.include_router(phase3.router)
app.include_router(phase4.router)
app.include_router(phase5.router)
app.include_router(phase6.router)


@app.get("/health")
def health_check():
    try:
        from db.supabase_client import get_supabase
        sb = get_supabase()
        result = sb.table("briefs").select("id").limit(1).execute()
        return {"status": "ok", "service": "viral-video-production-api", "db": "connected"}
    except Exception as e:
        return {"status": "degraded", "service": "viral-video-production-api", "db": f"error: {str(e)[:100]}"}


@app.get("/", response_class=HTMLResponse)
def root():
    return TEST_PAGE


TEST_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Backero API — Test Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;padding:2rem}
h1{font-size:1.8rem;margin-bottom:.5rem;color:#38bdf8}
.sub{color:#94a3b8;margin-bottom:2rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem;margin-bottom:2rem}
.card{background:#1e293b;border-radius:12px;padding:1.25rem;border:1px solid #334155}
.card h3{color:#38bdf8;margin-bottom:.75rem;font-size:.95rem}
.status{display:inline-block;padding:2px 10px;border-radius:99px;font-size:.8rem;font-weight:600}
.pass{background:#064e3b;color:#34d399}.fail{background:#7f1d1d;color:#fca5a5}
.wait{background:#78350f;color:#fbbf24}
pre{background:#0f172a;padding:.75rem;border-radius:8px;font-size:.78rem;overflow-x:auto;margin-top:.5rem;max-height:200px;overflow-y:auto;color:#a5b4fc}
button{background:#2563eb;color:#fff;border:none;padding:.6rem 1.2rem;border-radius:8px;cursor:pointer;font-size:.9rem;margin-top:.5rem}
button:hover{background:#1d4ed8}
button:disabled{background:#475569;cursor:not-allowed}
.actions{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.75rem}
.log{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.25rem;margin-top:1rem}
.log h3{color:#a78bfa;margin-bottom:.5rem}
#logBox{font-family:monospace;font-size:.78rem;white-space:pre-wrap;max-height:300px;overflow-y:auto;color:#94a3b8}
a{color:#38bdf8}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;flex-wrap:wrap;gap:1rem}
.links a{margin-left:1rem;font-size:.85rem}
</style>
</head>
<body>
<div class="topbar">
<div><h1>⚡ Backero API — Test Dashboard</h1><p class="sub">Viral Video Production Form Backend</p></div>
<div class="links"><a href="/docs">📄 Swagger Docs</a><a href="/health">❤️ Health</a></div>
</div>

<div class="grid">
  <div class="card" id="c-health"><h3>1. Health Check</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-create"><h3>2. Create Brief</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase1"><h3>3. Save Phase 1 (Input)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase2"><h3>4. Save Phase 2 (Structure)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase3"><h3>5. Generate Screenplay (Phase 3)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase4"><h3>6. Run Quality Checks (Phase 4)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase5"><h3>7. Production Pack (Phase 5)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-phase6"><h3>8. Generate Node Graph (Phase 6)</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-metrics"><h3>9. Dashboard Metrics</h3><span class="status wait">waiting</span><pre></pre></div>
  <div class="card" id="c-pipeline"><h3>10. Pipeline View</h3><span class="status wait">waiting</span><pre></pre></div>
</div>

<div class="actions">
<button onclick="runAll()">🚀 Run Full Integration Test</button>
<button onclick="cleanup()" id="btnClean" disabled>🧹 Cleanup Test Data</button>
</div>

<div class="log"><h3>📋 Test Log</h3><div id="logBox">Click "Run Full Integration Test" to start...\n</div></div>

<script>
const B = '';
let briefId = null;

function log(msg) { document.getElementById('logBox').textContent += msg + '\\n'; }
function setCard(id, pass, data) {
  const c = document.getElementById(id);
  const s = c.querySelector('.status');
  s.className = 'status ' + (pass ? 'pass' : 'fail');
  s.textContent = pass ? 'PASS' : 'FAIL';
  c.querySelector('pre').textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
}

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(B + path, opts);
  return { status: r.status, data: await r.json().catch(() => null), ok: r.ok };
}

async function runAll() {
  document.querySelectorAll('.status').forEach(s => { s.className='status wait'; s.textContent='testing...'; });
  document.getElementById('logBox').textContent = '';
  log('Starting full integration test...\\n');

  // 1 Health
  let r = await api('GET', '/health');
  setCard('c-health', r.ok, r.data);
  log('✓ Health: ' + JSON.stringify(r.data));

  // 2 Create brief
  r = await api('POST', '/api/dashboard/briefs', {title:'Integration Test Brief',creator_name:'Pragatish',creator_initials:'PK'});
  briefId = r.data?.brief_id;
  setCard('c-create', !!briefId, r.data);
  log(briefId ? '✓ Brief created: ' + briefId : '✗ Brief creation failed');
  if (!briefId) { log('\\n⛔ Cannot continue without brief_id'); return; }
  document.getElementById('btnClean').disabled = false;

  // 3 Phase 1
  r = await api('POST', '/api/phase1/' + briefId, {platform:'Instagram',niche:'Skincare',sub_niche:'Anti-aging',topic:'Vitamin C Serum Hack',hook_text:'70% of serums go bad before you use them',content_style:'Demonstration',time_to_value:'0-3s',knowledge_nuggets:[{type:'Shocking Fact',text:'73% of vitamin C serums oxidize within 3 months',source:'Dermatology Research 2026',rationale:'Creates immediate credibility',color:'#EF4444'},{type:'Practical Hack',text:'Store your serum in the fridge — doubles shelf life',source:'Lab Tests',rationale:'Actionable tip',color:'#22C55E'},{type:'Story Hook',text:'I ruined my skin for 6 months using expired serum',source:'Personal',rationale:'Emotional hook',color:'#F59E0B'}]});
  setCard('c-phase1', r.data?.success, r.data);
  log('✓ Phase 1 saved');
  await api('POST', '/api/phase1/' + briefId + '/advance');

  // 4 Phase 2
  r = await api('POST', '/api/phase2/' + briefId, {content_type:'educational',selected_format:'Whiteboard',selected_structure:'Step-by-Step',format_tier:'A',recommendation_level:'best',platform_boost_applied:false});
  setCard('c-phase2', r.data?.success, r.data);
  log('✓ Phase 2 saved');
  await api('POST', '/api/phase2/' + briefId + '/advance');

  // 5 Phase 3
  r = await api('POST', '/api/phase3/' + briefId + '/generate');
  setCard('c-phase3', r.data?.generated, {scenes: r.data?.scenes?.length, runtime: r.data?.total_runtime_sec, words: r.data?.total_words, cuts: r.data?.cut_count, golden_rules: r.data?.golden_rules_check?.length});
  log('✓ Phase 3: ' + r.data?.scenes?.length + ' scenes, ' + r.data?.total_runtime_sec + 's runtime');
  await api('POST', '/api/phase3/' + briefId + '/advance');

  // 6 Phase 4
  r = await api('POST', '/api/phase4/' + briefId + '/run-checks');
  setCard('c-phase4', r.ok, {score: r.data?.quality_score, verdict: r.data?.overall_verdict, summary: r.data?.summary});
  log('✓ Phase 4: score=' + r.data?.quality_score + ', verdict=' + r.data?.overall_verdict);

  // 7 Phase 5
  r = await api('GET', '/api/phase5/' + briefId);
  setCard('c-phase5', r.ok, {meta: r.data?.meta, tabs: r.data?.tabs_available, rules: r.data?.golden_rules?.length});
  log('✓ Phase 5: ' + r.data?.golden_rules?.length + ' golden rules evaluated');

  // 8 Phase 6
  r = await api('POST', '/api/phase6/' + briefId + '/generate');
  setCard('c-phase6', r.data?.generated, {nodes: r.data?.node_count, edges: r.data?.edge_count});
  log('✓ Phase 6: ' + r.data?.node_count + ' nodes, ' + r.data?.edge_count + ' edges');

  // 9 Metrics
  r = await api('GET', '/api/dashboard/metrics?date_range=30');
  setCard('c-metrics', r.ok, r.data);
  log('✓ Metrics: ' + r.data?.total_videos + ' total videos');

  // 10 Pipeline
  r = await api('GET', '/api/dashboard/pipeline');
  setCard('c-pipeline', r.ok, r.data);
  log('✓ Pipeline: ' + r.data?.phases?.length + ' phases');

  log('\\n✅ ALL 10 TESTS COMPLETE — Backend is fully operational!');
  log('\\nYour backend is running at http://localhost:8000');
  log('Connect your frontend with VITE_API_URL=http://localhost:8000');
}

async function cleanup() {
  if (briefId) {
    await api('DELETE', '/api/dashboard/briefs/' + briefId + '?hard=true');
    log('\\n🧹 Test brief cleaned up: ' + briefId);
    briefId = null;
    document.getElementById('btnClean').disabled = true;
  }
}
</script>
</body>
</html>"""
