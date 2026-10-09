const toggle = document.querySelector('.menu-toggle');
const nav = document.getElementById('navigation');
const dropdowns = [...document.querySelectorAll('.nav-dropdown')];

function closeNavigation() {
  dropdowns.forEach(item => { item.open = false; });
  toggle?.setAttribute('aria-expanded', 'false');
  nav?.classList.remove('open');
}

toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  if (!open) closeNavigation();
  else {
    toggle.setAttribute('aria-expanded', 'true');
    nav?.classList.add('open');
  }
});
dropdowns.forEach(item => item.addEventListener('toggle', () => {
  if (item.open) dropdowns.forEach(other => { if (other !== item) other.open = false; });
}));
document.addEventListener('click', event => {
  if (!event.target.closest('header')) closeNavigation();
});
nav?.addEventListener('click', event => {
  if (event.target.closest('a')) closeNavigation();
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const openDropdown = dropdowns.find(item => item.open);
  if (openDropdown) {
    openDropdown.open = false;
    openDropdown.querySelector('summary')?.focus();
  } else if (nav?.classList.contains('open')) {
    closeNavigation();
    toggle?.focus();
  }
});

const tabs = [...document.querySelectorAll('.service-option')];
function selectTab(index) {
  tabs.forEach((button, i) => {
    const active = i === index;
    button.setAttribute('aria-selected', String(active));
    button.tabIndex = active ? 0 : -1;
    const panel = document.getElementById(button.getAttribute('aria-controls'));
    if (panel) panel.hidden = !active;
  });
}

const portfolioFilters = [...document.querySelectorAll('.portfolio-filter')];
const portfolioCards = [...document.querySelectorAll('.portfolio-card[data-category]')];
portfolioFilters.forEach(filter => filter.addEventListener('click', () => {
  const value = filter.dataset.filter;
  portfolioFilters.forEach(item => {
    const active = item === filter;
    item.classList.toggle('is-active', active);
    item.setAttribute('aria-pressed', String(active));
  });
  portfolioCards.forEach(card => {
    card.hidden = value !== 'all' && card.dataset.category !== value;
  });
}));
tabs.forEach((button, index) => {
  button.addEventListener('click', () => selectTab(index));
  button.addEventListener('keydown', event => {
    let next;
    if (['ArrowRight', 'ArrowDown'].includes(event.key)) next = (index + 1) % tabs.length;
    if (['ArrowLeft', 'ArrowUp'].includes(event.key)) next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    selectTab(next);
    tabs[next].focus();
  });
});

const form = document.getElementById('enquiry-form');
if (form) {
  const submit = form.querySelector('button[type="submit"]');
  const note = document.getElementById('form-note');
  const status = document.getElementById('form-status');
  const verification = document.getElementById('enquiry-verification');
  let directSend = false;
  let widgetId;
  let token = '';
  let requestId;
  let sending = false;
  let waitingForVerification = false;
  let verificationTimer;
  form.addEventListener('input', () => { requestId = undefined; });
  function announce(message) {
    status.textContent = message;
    status.focus();
  }
  function currentToken() {
    return token || window.turnstile?.getResponse?.(widgetId) || form.querySelector('[name="cf-turnstile-response"]')?.value || '';
  }
  function waitForVerifiedToken() {
    clearInterval(verificationTimer);
    let checks = 0;
    verificationTimer = setInterval(() => {
      checks += 1;
      token = currentToken();
      if (token) {
        clearInterval(verificationTimer);
        waitingForVerification = false;
        form.requestSubmit();
      } else if (checks >= 120) {
        clearInterval(verificationTimer);
        waitingForVerification = false;
        announce('The security check did not return a verification code. Please refresh the page and try once more.');
      }
    }, 250);
  }
  async function initialiseDelivery() {
    try {
      const response = await fetch('/api/enquiry', { headers: { Accept: 'application/json' }, cache: 'no-store', signal: AbortSignal.timeout(5000) });
      if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) return;
      const config = await response.json();
      if (!config.enabled || typeof config.siteKey !== 'string' || !config.siteKey) return;
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      script.async = true;
      script.addEventListener('load', () => {
        if (!window.turnstile) return;
        verification.hidden = false;
        widgetId = window.turnstile.render(verification, {
          sitekey: config.siteKey,
          action: 'enquiry',
          callback: value => {
            token = value;
            if (waitingForVerification) {
              clearInterval(verificationTimer);
              waitingForVerification = false;
              form.requestSubmit();
            }
          },
          'expired-callback': () => { token = ''; waitingForVerification = false; },
          'error-callback': () => {
            token = '';
            waitingForVerification = false;
            announce('The security check could not be completed. Please refresh the page and try again.');
          }
        });
        directSend = true;
        submit.textContent = 'Send enquiry';
        note.textContent = 'Your enquiry will be sent to our business inbox after the security check. Please do not include passwords or payment details.';
      });
      document.head.append(script);
    } catch {
      // Static hosting retains the explicit email-draft option.
    }
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending || !form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form));
    if (data.company_url) return;
    if (!directSend) {
      announce('Online sending is temporarily unavailable. Please refresh the page or email ryan@websolutionsydney.com.au.');
      return;
    }
    token = currentToken();
    if (!token) {
      waitingForVerification = true;
      announce('Please complete the security check. Your enquiry will send automatically when it turns green.');
      waitForVerifiedToken();
      return;
    }
    requestId ||= crypto.randomUUID();
    sending = true;
    submit.disabled = true;
    submit.textContent = 'Sending…';
    try {
      const response = await fetch('/api/enquiry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ ...data, token, requestId }),
        signal: AbortSignal.timeout(25000)
      });
      const result = await response.json();
      if (!response.ok || result.status !== 'accepted') {
        announce(typeof result.message === 'string' ? result.message : 'We could not confirm your enquiry. Please email or call us before trying again.');
        return;
      }
      announce('Your enquiry was accepted by our email service for delivery. Thank you — we will review your message and respond.');
      form.reset();
      requestId = undefined;
    } catch {
      announce('We could not confirm your enquiry. Please email or call us before trying again. Your details are still in the form.');
    } finally {
      sending = false;
      submit.disabled = false;
      submit.textContent = 'Send enquiry';
      token = '';
      clearInterval(verificationTimer);
      if (widgetId !== undefined) window.turnstile?.reset(widgetId);
    }
  });
  initialiseDelivery();
}
