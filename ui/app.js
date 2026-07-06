/**
 * EduGuardian — Frontend Application Logic
 * ==========================================
 * Handles: chat UI, API calls to the Python backend,
 * message rendering, quick buttons, session reset, and routing toasts.
 */

// ─────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────
const state = {
  userId: `student_${Date.now()}`,  // Unique ID for this browser session
  isLoading: false,
  welcomeHidden: false,
  messageCount: 0
};

// ─────────────────────────────────────────────────────────────────
// DOM References
// ─────────────────────────────────────────────────────────────────
const messagesArea = document.getElementById('messages-area');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const routingToast = document.getElementById('routing-toast');
const routingIcon = document.getElementById('routing-icon');
const routingText = document.getElementById('routing-text');
const welcomeCard = document.getElementById('welcome-card');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');
const menuBtn = document.getElementById('menu-btn');
const sidebar = document.querySelector('.sidebar');

// Quick start buttons
const quickBtns = {
  explain: document.getElementById('q-explain'),
  quiz: document.getElementById('q-quiz'),
  plan: document.getElementById('q-plan'),
  stressed: document.getElementById('q-stressed'),
};

// ─────────────────────────────────────────────────────────────────
// Routing Detection (determines which agent is being used)
// ─────────────────────────────────────────────────────────────────
const ROUTING_RULES = [
  {
    keywords: ['explain', 'what is', 'how does', 'quiz', 'test me', 'study', 'homework',
      'math', 'science', 'history', 'biology', 'chemistry', 'physics',
      'english', 'essay', 'formula', 'equation', 'help me understand'],
    icon: '📚', label: 'Routing to Tutor Agent...'
  },
  {
    keywords: ['stressed', 'anxious', 'anxiety', 'overwhelmed', 'scared', 'nervous',
      'can\'t focus', 'can\'t sleep', 'feel like giving up', 'exhausted',
      'mental health', 'worried', 'depressed', 'sad', 'panic'],
    icon: '🧘', label: 'Routing to Wellness Agent...'
  },
  {
    keywords: ['study plan', 'schedule', 'timetable', 'exam on', 'deadline', 'organize',
      'how should i study', 'prepare for', 'plan my', 'when to study'],
    icon: '📅', label: 'Routing to Study Planner...'
  }
];

function detectRouting(message) {
  const lower = message.toLowerCase();
  for (const rule of ROUTING_RULES) {
    if (rule.keywords.some(kw => lower.includes(kw))) {
      return { icon: rule.icon, label: rule.label };
    }
  }
  return null;
}

// ─────────────────────────────────────────────────────────────────
// Toast Notifications
// ─────────────────────────────────────────────────────────────────
function showRoutingToast(icon, label) {
  routingIcon.textContent = icon;
  routingText.textContent = label;
  routingToast.classList.remove('hidden');
  routingToast.classList.add('visible');
  setTimeout(() => {
    routingToast.classList.remove('visible');
    setTimeout(() => routingToast.classList.add('hidden'), 300);
  }, 2500);
}

// ─────────────────────────────────────────────────────────────────
// Message Rendering
// ─────────────────────────────────────────────────────────────────
function formatMessageText(text) {
  // Convert basic markdown-like formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')   // **bold**
    .replace(/\*(.*?)\*/g, '<em>$1</em>')             // *italic*
    .replace(/`(.*?)`/g, '<code>$1</code>')         // `code`
    .replace(/\n/g, '<br />')                  // newlines
    .replace(/#{1,3} (.+)/g, '<strong>$1</strong>');    // headings
}

function createMessageElement(role, text) {
  const isCrisis = text.toLowerCase().includes('crisis') ||
    text.toLowerCase().includes('741741') ||
    text.toLowerCase().includes('human_review_required');

  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = role === 'user' ? '🧑‍🎓' : '🤖';

  const right = document.createElement('div');
  right.style.display = 'flex';
  right.style.flexDirection = 'column';

  const bubble = document.createElement('div');
  bubble.className = `message-bubble${isCrisis ? ' crisis' : ''}`;
  bubble.innerHTML = formatMessageText(text);

  // Render LaTeX math using KaTeX if available
  if (window.renderMathInElement) {
    try {
      renderMathInElement(bubble, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false},
          {left: '\\(', right: '\\)', display: false},
          {left: '\\[', right: '\\]', display: true}
        ],
        throwOnError: false
      });
    } catch (e) {
      console.error('KaTeX rendering error:', e);
    }
  }

  const time = document.createElement('div');
  time.className = 'message-time';
  time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  right.appendChild(bubble);
  right.appendChild(time);

  wrapper.appendChild(avatar);
  wrapper.appendChild(right);

  return wrapper;
}

function appendMessage(role, text) {
  // Hide welcome card on first message
  if (!state.welcomeHidden) {
    welcomeCard.style.opacity = '0';
    welcomeCard.style.transition = 'opacity 0.3s ease';
    setTimeout(() => { welcomeCard.style.display = 'none'; }, 300);
    state.welcomeHidden = true;
  }

  const el = createMessageElement(role, text);
  messagesArea.appendChild(el);
  state.messageCount++;

  // Scroll to bottom smoothly
  setTimeout(() => {
    messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
  }, 50);
}

// ─────────────────────────────────────────────────────────────────
// Agent Highlighting
// ─────────────────────────────────────────────────────────────────
function highlightAgent(agentName) {
  // Remove active class from all agent cards
  document.querySelectorAll('.agent-card').forEach(card => {
    card.classList.remove('active');
  });

  // Map backend agent names to UI element IDs
  let targetId = 'agent-all'; // default to orchestrator
  if (agentName === 'tutor_agent') targetId = 'agent-tutor';
  if (agentName === 'wellness_agent') targetId = 'agent-wellness';
  if (agentName === 'study_plan_agent') targetId = 'agent-planner';

  // Add active class to the correct card
  const targetCard = document.getElementById(targetId);
  if (targetCard) targetCard.classList.add('active');
}

// ─────────────────────────────────────────────────────────────────
// API Call to Backend
// ─────────────────────────────────────────────────────────────────
async function sendMessage(messageText) {
  if (state.isLoading || !messageText.trim()) return;

  state.isLoading = true;

  // Show user message immediately
  appendMessage('user', messageText);

  // Detect routing and show toast
  const routing = detectRouting(messageText);
  if (routing) showRoutingToast(routing.icon, routing.label);

  // Show typing indicator
  typingIndicator.classList.remove('hidden');
  sendBtn.disabled = true;
  userInput.disabled = true;

  // Scroll to show typing indicator
  setTimeout(() => {
    messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
  }, 100);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: messageText,
        user_id: state.userId
      })
    });

    const data = await response.json();

    if (data.response) {
      appendMessage('assistant', data.response);
      if (data.active_agent) {
        highlightAgent(data.active_agent);
      }
    } else if (data.error) {
      appendMessage('assistant', `⚠️ Something went wrong: ${data.error}. Please try again.`);
    }
  } catch (error) {
    console.error('Chat error:', error);
    appendMessage('assistant',
      '⚠️ I couldn\'t connect to the EduGuardian server. ' +
      'Please make sure the Python server is running (`python main.py`) and refresh the page.'
    );
  } finally {
    // Hide typing indicator and restore input
    typingIndicator.classList.add('hidden');
    state.isLoading = false;
    sendBtn.disabled = false;
    userInput.disabled = false;
    userInput.focus();
    updateSendButton();
  }
}

// ─────────────────────────────────────────────────────────────────
// Input Handling
// ─────────────────────────────────────────────────────────────────
function updateSendButton() {
  sendBtn.disabled = !userInput.value.trim() || state.isLoading;
}

// Auto-resize textarea as user types
function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 140) + 'px';
}

userInput.addEventListener('input', () => {
  autoResize();
  updateSendButton();
});

userInput.addEventListener('keydown', (e) => {
  // Send on Enter (not Shift+Enter)
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (msg && !state.isLoading) {
      userInput.value = '';
      userInput.style.height = 'auto';
      updateSendButton();
      sendMessage(msg);
    }
  }
});

sendBtn.addEventListener('click', () => {
  const msg = userInput.value.trim();
  if (msg && !state.isLoading) {
    userInput.value = '';
    userInput.style.height = 'auto';
    updateSendButton();
    sendMessage(msg);
  }
});

// ─────────────────────────────────────────────────────────────────
// Quick Start Buttons
// ─────────────────────────────────────────────────────────────────
const QUICK_MESSAGES = {
  explain: 'Can you explain photosynthesis to me? I have a biology exam coming up.',
  quiz: "Quiz me on World War 2! Start easy and make it harder as I get answers right.",
  plan: "I need a study plan! I have exams in Math and History in 5 days and can study 2 hours each evening.",
  stressed: "I'm really stressed about my exams. I feel like I can't handle the pressure.",
};

Object.entries(quickBtns).forEach(([key, btn]) => {
  if (btn) {
    btn.addEventListener('click', () => {
      userInput.value = QUICK_MESSAGES[key];
      updateSendButton();
      userInput.focus();
    });
  }
});

// ─────────────────────────────────────────────────────────────────
// Start Button (on Welcome Card)
// ─────────────────────────────────────────────────────────────────
startBtn.addEventListener('click', () => {
  sendMessage("Hello EduGuardian! I'm ready to start. What can you help me with today?");
});

// ─────────────────────────────────────────────────────────────────
// Reset / New Conversation
// ─────────────────────────────────────────────────────────────────
resetBtn.addEventListener('click', async () => {
  try {
    await fetch('/api/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: state.userId })
    });
  } catch (e) { /* silent */ }

  // Clear messages
  messagesArea.innerHTML = '';
  state.welcomeHidden = false;
  state.messageCount = 0;

  // Restore welcome card
  welcomeCard.style.display = '';
  welcomeCard.style.opacity = '1';
  messagesArea.appendChild(welcomeCard);

  userInput.value = '';
  userInput.style.height = 'auto';
  updateSendButton();
});

// ─────────────────────────────────────────────────────────────────
// Mobile Sidebar Toggle
// ─────────────────────────────────────────────────────────────────
menuBtn.addEventListener('click', () => {
  sidebar.classList.toggle('open');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 &&
    sidebar.classList.contains('open') &&
    !sidebar.contains(e.target) &&
    e.target !== menuBtn) {
    sidebar.classList.remove('open');
  }
});

// ─────────────────────────────────────────────────────────────────
// Agent Card Highlight (visual only)
// ─────────────────────────────────────────────────────────────────
const agentCards = document.querySelectorAll('.agent-card');
// Agent cards are for visual indicator only, clicking is disabled.

// Auto-highlight based on detected routing
function highlightAgent(messageText) {
  const lower = messageText.toLowerCase();
  let targetId = 'agent-all';
  if (['stressed', 'anxious', 'overwhelmed', 'mental', 'focus', 'sleep'].some(w => lower.includes(w))) {
    targetId = 'agent-wellness';
  } else if (['plan', 'schedule', 'timetable', 'exam on', 'deadline'].some(w => lower.includes(w))) {
    targetId = 'agent-planner';
  } else if (['explain', 'what is', 'quiz', 'study', 'math', 'science', 'biology'].some(w => lower.includes(w))) {
    targetId = 'agent-tutor';
  }
  agentCards.forEach(c => c.classList.remove('active'));
  const target = document.getElementById(targetId);
  if (target) target.classList.add('active');
}

// Override sendMessage to also highlight agent
const _origSend = sendMessage;
// (already integrated above via routing detection)

// ─────────────────────────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────────────────────────
console.log('🎓 EduGuardian UI loaded. User ID:', state.userId);
userInput.focus();
