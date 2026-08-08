/* ================================================================
   VIBEZ PROTOCOL — script.js
   Author: Oyeyemi Olamilekan
   ================================================================ */


// ── BACKEND URL ──────────────────────────────────────────────────────────
// 🔑 LOCAL: leave as-is while developing on your PC
// 🔑 DEPLOY: replace with your Render URL, e.g:
//    'https://vibezprotocol-api.onrender.com/api'
// The frontend is served from a different origin than the API, so this must be
// absolute. Falls back to the local backend when opened from a file:// or
// localhost origin, so development does not need an edit here.
const API_URL = ['localhost', '127.0.0.1', ''].includes(location.hostname)
  ? 'http://localhost:8001/api'
  : 'https://vibezprotocol-api.onrender.com/api';


// ── 1. NAV — shrink on scroll ─────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
});


// ── 2. MOBILE MENU — hamburger toggle ────────────────────────────────────
const hamburger   = document.getElementById('hamburger');
const mobileMenu  = document.getElementById('mobileMenu');
const mobileLinks = document.querySelectorAll('.mobile-link');

hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
mobileLinks.forEach(link => link.addEventListener('click', () => mobileMenu.classList.remove('open')));


// ── 3. SCROLL ANIMATIONS — fade up on enter ──────────────────────────────
const animatedEls = document.querySelectorAll('[data-animate]');

const scrollObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const siblings = [...entry.target.parentElement.children];
        entry.target.style.transitionDelay = `${siblings.indexOf(entry.target) * 0.1}s`;
        entry.target.classList.add('visible');
        scrollObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 }
);

animatedEls.forEach(el => scrollObserver.observe(el));


// ── 4. ACTIVE NAV LINK on scroll ─────────────────────────────────────────
const sections   = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.getAttribute('id');
  });
  navAnchors.forEach(a => {
    a.style.color = a.getAttribute('href') === `#${current}` ? 'var(--accent)' : '';
  });
});


// ── 5. CONTACT FORM → Backend API ────────────────────────────────────────
const contactForm = document.getElementById('contactForm');
const submitBtn   = document.getElementById('submitBtn');
const formNote    = document.getElementById('formNote');

if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      name:    contactForm.name.value.trim(),
      email:   contactForm.email.value.trim(),
      subject: contactForm.subject.value.trim(),
      message: contactForm.message.value.trim(),
    };

    if (!payload.name || !payload.email || !payload.subject || !payload.message) {
      showNote('Please fill in all fields.', 'error');
      return;
    }

    submitBtn.textContent = 'SENDING...';
    submitBtn.disabled    = true;

    try {
      const res = await fetch(`${API_URL}/contact`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });

      if (res.ok) {
        showNote("Message received! We'll be in touch soon.", "success");
        contactForm.reset();
      } else {
        const err = await res.json().catch(() => ({}));
        showNote(readError(err), "error");
      }

    } catch {
      // Backend unreachable — fall back to mailto
      showNote('Sending via email...', 'error');
      setTimeout(() => {
        window.location.href =
          `mailto:vibezprotocol@gmail.com` +
          `?subject=${encodeURIComponent(payload.subject)}` +
          `&body=${encodeURIComponent(`Name: ${payload.name}\nEmail: ${payload.email}\n\n${payload.message}`)}`;
      }, 1200);
    } finally {
      submitBtn.textContent = 'SEND MESSAGE';
      submitBtn.disabled    = false;
    }
  });
}

// FastAPI sends plain strings for HTTPException but an array of objects for
// validation failures — rendering that array directly prints "[object Object]".
function readError(err) {
  const detail = err && err.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    const field = detail[0].loc && detail[0].loc[detail[0].loc.length - 1];
    const labels = { email: 'email address', name: 'name', subject: 'subject', message: 'message' };
    return field
      ? `Please check your ${labels[field] || field} and try again.`
      : 'Please check your details and try again.';
  }
  return 'Something went wrong. Please try again.';
}

let noteTimer;

function showNote(message, type) {
  // Clear any pending hide, or a previous message's timer would cut this one short.
  clearTimeout(noteTimer);
  formNote.textContent = message;
  formNote.className   = `form-note ${type}`;
  // Errors linger — they usually ask the visitor to fix something.
  noteTimer = setTimeout(() => formNote.classList.add('is-hidden'),
                         type === 'error' ? 8000 : 5000);
}


// ── 6. LOAD PROJECTS from Backend ────────────────────────────────────────
async function loadProjects() {
  const workGrid = document.getElementById('workGrid');
  if (!workGrid) return;

  try {
    const res      = await fetch(`${API_URL}/projects`);
    if (!res.ok) return;
    const projects = await res.json();

    // No projects yet — keep the placeholder cards
    if (!projects || projects.length === 0) return;

    workGrid.innerHTML = projects.map(p => `
      <div class="work-card" data-animate>
        ${p.is_featured ? '<span class="work-placeholder">FEATURED</span>' : '<span class="work-placeholder">PROJECT</span>'}
        <div class="work-badge">${p.category}</div>
        <div class="work-title">${p.title}</div>
        <div class="work-sub">${p.description.length > 90 ? p.description.slice(0,90) + '...' : p.description}</div>
        ${p.tags ? `
          <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:1rem">
            ${p.tags.split(',').map(t => `<span class="tag">${t.trim()}</span>`).join('')}
          </div>` : ''}
        ${p.url ? `
          <a href="${p.url}" target="_blank" rel="noopener"
             style="display:inline-block;margin-top:1.25rem;font-family:var(--font-mono);
                    font-size:0.68rem;color:var(--accent);letter-spacing:0.1em;
                    text-decoration:none;border-bottom:1px solid rgba(0,255,157,0.3)">
            VIEW PROJECT →
          </a>` : ''}
      </div>
    `).join('');

    // Observe new cards for scroll animation
    workGrid.querySelectorAll('[data-animate]').forEach(el => scrollObserver.observe(el));

  } catch {
    // Backend offline — placeholder cards stay, no crash
    console.log('Projects API not reachable — showing placeholder cards.');
  }
}

loadProjects();


// ── 7. CURSOR GLOW (desktop only) ────────────────────────────────────────
if (window.matchMedia('(pointer: fine)').matches) {
  const glow = document.createElement('div');
  glow.style.cssText = `
    position:fixed; width:300px; height:300px; border-radius:50%;
    background:radial-gradient(circle, rgba(0,255,157,0.04) 0%, transparent 70%);
    pointer-events:none; z-index:9999; transform:translate(-50%,-50%);
    transition:left 0.15s ease, top 0.15s ease; will-change:left,top;
  `;
  document.body.appendChild(glow);
  document.addEventListener('mousemove', e => {
    glow.style.left = e.clientX + 'px';
    glow.style.top  = e.clientY + 'px';
  });
}


// ── 8. AUTO COPYRIGHT YEAR ────────────────────────────────────────────────
const copyEl = document.querySelector('.footer-copy');
if (copyEl) {
  copyEl.textContent =
    `© ${new Date().getFullYear()} VIBEZ PROTOCOL · OYEYEMI OLAMILEKAN · ALL RIGHTS RESERVED`;
}
