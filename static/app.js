/* ════════════════════════════════════════════════════════════════════════════
   NutriAI — app.js   |   Frontend Logic for IBM Granite Nutrition Agent
   ════════════════════════════════════════════════════════════════════════════ */

'use strict';

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  sessionId:       null,
  currentPlan:     null,
  currentFilename: null,
  profile:         {},
};

const API = {
  health:      '/api/health',
  generatePlan:'/api/generate-plan',
  chat:        '/api/chat',
  plans:       '/api/plans',
};

// ── Initialisation ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkApiHealth();
  setInterval(checkApiHealth, 30_000);
});

// ── Tab Navigation ──────────────────────────────────────────────────────────────
function showTab(tabName) {
  document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  const section = document.getElementById(`tab-${tabName}`);
  if (section) section.classList.add('active');

  const btn = document.querySelector(`[data-tab="${tabName}"]`);
  if (btn) btn.classList.add('active');

  if (tabName === 'saved') loadSavedPlans();
}

// ── Health Check ────────────────────────────────────────────────────────────────
async function checkApiHealth() {
  const dot   = document.getElementById('statusDot');
  const label = document.getElementById('statusLabel');
  try {
    const res  = await fetch(API.health);
    const data = await res.json();
    if (data.status === 'healthy') {
      if (data.mode === 'live') {
        dot.className = 'status-dot online';
        label.textContent = 'IBM Granite ● Live';
      } else {
        dot.className = 'status-dot demo';
        label.textContent = 'Demo Mode ● Running';
      }
    }
  } catch {
    dot.className = 'status-dot offline';
    label.textContent = 'Offline';
  }
}

// ── Profile Form ─────────────────────────────────────────────────────────────────
async function submitProfile(e) {
  e.preventDefault();

  // Collect checked medical conditions
  const conditions = Array.from(
    document.querySelectorAll('input[name="condition"]:checked')
  ).map(cb => cb.value);
  const extraCondition = document.getElementById('medical_extra').value.trim();
  if (extraCondition) conditions.push(extraCondition);
  const medicalHistory = conditions.length ? conditions.join(', ') : 'None reported';

  const profile = {
    name:            document.getElementById('name').value.trim(),
    age:             document.getElementById('age').value.trim(),
    diet:            document.getElementById('diet').value,
    goals:           document.getElementById('goals').value,
    medical_history: medicalHistory,
    city:            document.getElementById('city').value.trim(),
    country:         document.getElementById('country').value.trim(),
    weight:          document.getElementById('weight').value.trim(),
    height:          document.getElementById('height').value.trim(),
  };

  // Basic validation
  if (!profile.name || !profile.age || !profile.diet || !profile.city || !profile.country) {
    showToast('Please fill in all required fields.', 'error');
    return;
  }

  state.profile = profile;

  // Show loading state
  document.getElementById('planLoading').classList.remove('hidden');
  document.getElementById('generateBtn').disabled = true;
  document.getElementById('generateBtn').textContent = '⏳ Generating…';

  try {
    const res  = await fetch(API.generatePlan, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(profile),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Plan generation failed.');
    }

    state.currentPlan     = data.plan;
    state.currentFilename = data.filename;
    state.sessionId       = data.session_id;

    renderPlan(data.plan, profile);
    showTab('plan');
    showToast('✅ Nutrition plan generated successfully!', 'success');

  } catch (err) {
    showToast(`❌ ${err.message}`, 'error');
  } finally {
    document.getElementById('planLoading').classList.add('hidden');
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('generateBtn').textContent = '🚀 Generate My Nutrition Plan';
  }
}

// ── Render Plan ──────────────────────────────────────────────────────────────────
function renderPlan(planText, profile) {
  const empty   = document.getElementById('planEmpty');
  const content = document.getElementById('planContent');
  const output  = document.getElementById('planOutput');
  const meta    = document.getElementById('planMeta');

  empty.classList.add('hidden');
  content.classList.remove('hidden');

  // Metadata bar
  meta.innerHTML = `
    <strong>${escHtml(profile.name)}</strong> · Age ${escHtml(profile.age)} ·
    ${formatDiet(profile.diet)} · ${escHtml(profile.city)}, ${escHtml(profile.country)}
    ${profile.weight ? '· ' + escHtml(profile.weight) + ' kg' : ''}
  `;

  // Render markdown
  output.innerHTML = marked.parse(planText);
}

function formatDiet(d) {
  const map = {
    'veg':'🥦 Vegetarian','vegan':'🌱 Vegan','non-veg':'🍗 Non-Vegetarian',
    'pescatarian':'🐟 Pescatarian','flexitarian':'🌿 Flexitarian',
  };
  return map[d] || d;
}

// ── Download Current Plan ─────────────────────────────────────────────────────────
async function downloadCurrentPlan() {
  if (!state.currentFilename) {
    showToast('No plan available to download.', 'error');
    return;
  }
  try {
    const res  = await fetch(`${API.plans}/${state.currentFilename}`);
    const text = await res.text();
    downloadAsFile(text, state.currentFilename, 'text/markdown');
    showToast('📥 Plan downloaded!', 'success');
  } catch {
    showToast('Download failed. Please try again.', 'error');
  }
}

function downloadAsFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Chat ──────────────────────────────────────────────────────────────────────────
function handleChatKey(e) {
  if (e.key === 'Enter' && e.ctrlKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendQuickMessage(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

async function sendMessage() {
  const input   = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  const sendBtn = document.getElementById('sendBtn');
  sendBtn.disabled = true;
  input.value = '';

  // Render user bubble
  appendChatMessage(message, 'user');

  // Show typing indicator
  const typing = document.getElementById('typingIndicator');
  typing.classList.remove('hidden');
  scrollChatToBottom();

  try {
    const res  = await fetch(API.chat, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        message,
        profile:    state.profile,
        session_id: state.sessionId,
      }),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Chat failed.');
    }

    if (!state.sessionId) state.sessionId = data.session_id;

    typing.classList.add('hidden');
    appendChatMessage(data.response, 'bot', data.tool_used);

  } catch (err) {
    typing.classList.add('hidden');
    appendChatMessage(`⚠️ ${err.message} — Please try again.`, 'bot');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

function appendChatMessage(text, role, toolUsed) {
  const window = document.getElementById('chatWindow');
  const div    = document.createElement('div');
  div.className = `chat-message ${role === 'user' ? 'user-message' : 'bot-message'}`;

  const avatarHtml = role === 'user'
    ? '<div class="avatar">👤</div>'
    : '<div class="avatar">🥗</div>';

  // Render markdown for bot, escape HTML for user
  const content = role === 'bot'
    ? marked.parse(text)
    : `<p>${escHtml(text)}</p>`;

  const toolBadge = (role === 'bot' && toolUsed && toolUsed !== 'off_topic_redirect' && toolUsed !== 'guardrail_block')
    ? `<div style="font-size:0.72rem;color:var(--text-light);margin-top:6px;">🔧 Tool: ${formatToolName(toolUsed)}</div>`
    : '';

  div.innerHTML = `
    ${avatarHtml}
    <div class="bubble">${content}${toolBadge}</div>
  `;

  window.appendChild(div);
  scrollChatToBottom();
}

function formatToolName(tool) {
  return {
    'generate_nutrition_plan': 'Nutrition Plan Generator',
    'answer_nutrition_query':  'Nutrition Q&A',
    'get_local_food_tips':     'Local Food Advisor',
    'calculate_bmi':           'BMI Calculator',
  }[tool] || tool;
}

function scrollChatToBottom() {
  const w = document.getElementById('chatWindow');
  w.scrollTop = w.scrollHeight;
}

// ── Saved Plans ──────────────────────────────────────────────────────────────────
async function loadSavedPlans() {
  const loading = document.getElementById('savedLoading');
  const empty   = document.getElementById('savedEmpty');
  const grid    = document.getElementById('savedList');

  loading.classList.remove('hidden');
  empty.classList.add('hidden');
  grid.classList.add('hidden');

  try {
    const res  = await fetch(API.plans);
    const data = await res.json();

    loading.classList.add('hidden');

    if (!data.plans || data.plans.length === 0) {
      empty.classList.remove('hidden');
      return;
    }

    grid.innerHTML = data.plans.map(p => `
      <div class="plan-card">
        <div class="plan-card-name">📄 ${escHtml(p.filename)}</div>
        <div class="plan-card-meta">
          📅 ${escHtml(p.modified)} &nbsp;|&nbsp; 📦 ${p.size_kb} KB
        </div>
        <div class="plan-card-actions">
          <button class="btn btn-secondary btn-sm" onclick="downloadPlan('${escHtml(p.filename)}')">
            ⬇️ Download
          </button>
        </div>
      </div>
    `).join('');

    grid.classList.remove('hidden');

  } catch {
    loading.classList.add('hidden');
    empty.classList.remove('hidden');
  }
}

async function downloadPlan(filename) {
  try {
    const res  = await fetch(`${API.plans}/${filename}`);
    const text = await res.text();
    downloadAsFile(text, filename, 'text/markdown');
    showToast('📥 Plan downloaded!', 'success');
  } catch {
    showToast('Download failed.', 'error');
  }
}

// ── Form Utilities ────────────────────────────────────────────────────────────────
function clearForm() {
  document.getElementById('profileForm').reset();
  document.querySelectorAll('input[name="condition"]').forEach(cb => cb.checked = false);
}

// ── Toast Notifications ───────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast     = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

// ── Helpers ───────────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
