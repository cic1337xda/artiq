// --- DOM Elements ---
const webcam = document.getElementById('webcam');
const processedFeed = document.getElementById('processedFeed');
const repCounter = document.getElementById('repCounter');
const gripStatus = document.getElementById('gripStatus');

// --- Clock & Dynamic Copyright Year ---
function updateDynamicYear() {
    const year = new Date().getFullYear();
    document.querySelectorAll('.dynamic-year').forEach((el) => {
        el.textContent = year;
    });
}
updateDynamicYear();

function updateClock() {
    const now = new Date();
    const dateEl = document.getElementById('currentDate');
    const timeEl = document.getElementById('currentTime');
    if (dateEl && timeEl) {
        dateEl.innerText = now.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
        timeEl.innerText = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }
}
setInterval(updateClock, 1000);
updateClock();

// --- Modal Management ---
const modalOverlay = document.getElementById('modalOverlay');
let activeModal = null;

function openModal(id) {
    if (!modalOverlay) return;
    modalOverlay.classList.add('modal-active');
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('pointer-events-none');
        setTimeout(() => { modal.classList.add('modal-scale'); modal.classList.remove('opacity-0'); }, 10);
        activeModal = modal;
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('modal-scale');
        modal.classList.add('opacity-0');
        modal.classList.add('pointer-events-none');
        setTimeout(() => { modalOverlay.classList.remove('modal-active'); activeModal = null; }, 300);
    }
}

// Ensure elements exist before adding event listeners
const btnSettings = document.getElementById('openSettingsBtn');
const btnProfile = document.getElementById('profileBtn');
const btnHistory = document.getElementById('openHistoryBtn');

if (btnSettings) btnSettings.addEventListener('click', () => openModal('settingsContainer'));
if (btnProfile) {
    btnProfile.addEventListener('click', async () => {
        if (currentUser) {
            // Logout logic
            let res = await fetch('/api/logout', { method: 'POST', credentials: 'include' });
            if (res.ok) {
                showToast("Logged out successfully", "success");
                loadProfile();
            }
        } else {
            openModal('authContainer');
        }
    });
}
if (btnHistory) btnHistory.addEventListener('click', () => { fetchHistory(); openModal('historyContainer'); });

// --- Toast Notification System ---
window.showToast = function(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    const icon = type === 'success' ? '✓' : '⚠️';
    const textColor = type === 'success' ? 'text-appleGreen' : 'text-appleRed';
    
    toast.className = `mx-auto w-max max-w-[90vw] bg-black/70 backdrop-blur-xl border border-white/10 shadow-[0_15px_40px_rgba(0,0,0,0.6)] text-white px-5 py-3 rounded-full font-medium text-[13px] flex items-center gap-3 transform transition-all duration-500 -translate-y-20 opacity-0 z-[99999]`;
    toast.innerHTML = `<span class="text-[15px] font-black">${icon}</span> <span class="${textColor} drop-shadow-sm">${message}</span>`;
    
    toastContainer.appendChild(toast);
    
    // Force browser repaint for initial state before slide-down animation
    setTimeout(() => {
        toast.classList.remove('-translate-y-20', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
    }, 10);
    
    // Slide back up after 3.5 seconds
    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('-translate-y-20', 'opacity-0');
        setTimeout(() => toast.remove(), 500); 
    }, 3500);
};

// --- Authentication Logic (Admin Wall) ---
let emgPollingTimer = null;

async function syncSavedMacAddress() {
    const savedMac = localStorage.getItem("artiq_target_mac");
    if (!savedMac) return;
    const inputEl = document.getElementById("inputMacAddress");
    if (inputEl) inputEl.value = savedMac;

    try {
        await fetch('/api/emg/set-mac', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mac: savedMac })
        });
    } catch (e) {}
}

async function checkAuthWall() {
    try {
        let res = await fetch('/api/user', { credentials: 'include' });
        if (res.ok) {
            // Login successful: Hide login wall, show dashboard
            document.getElementById('loginModalBox').classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                document.getElementById('loginView').classList.add('hidden');
                document.getElementById('dashboardView').classList.remove('hidden', 'opacity-0');
                // Session authenticated: Start AR Camera engine & EMG telemetry polling
                startAREngine();
                syncSavedMacAddress();
                if (typeof startEmgPolling === 'function') startEmgPolling();
            }, 500);
        } else {
            // Unauthenticated: Show login wall
            stopAREngine();
            if (typeof stopEmgPolling === 'function') stopEmgPolling();
            document.getElementById('dashboardView').classList.add('hidden', 'opacity-0');
            
            // Remove pointer-events-none to make clickable
            document.getElementById('loginView').classList.remove('hidden', 'opacity-0', 'pointer-events-none');
            
            setTimeout(() => document.getElementById('loginModalBox').classList.remove('scale-95', 'opacity-0'), 100);
        }
    } catch (e) {
        console.warn("System Locked.");
    }
}
checkAuthWall(); // Execute on initial page load

window.logoutAdmin = async function() {
    let res = await fetch('/api/logout', { method: 'POST', credentials: 'include' });
    if (res.ok) {
        showToast("System Locked", "success");
        checkAuthWall();
    }
};

window.requestOTP = async function() {
    const email = document.getElementById('regEmail').value;
    if (!email) return showToast("Enter clinic email first", "error");
    
    try {
        let res = await fetch('/api/send-otp', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        let data = await res.json().catch(() => ({ detail: "Server API Error (500)" }));
        
        if (res.ok) showToast(data.message || "OTP Sent to Email!", "success");
        else showToast(data.detail || data.error || "Failed to send OTP", "error");
    } catch (e) { showToast("Network Disconnected", "error"); }
};

window.requestResetOTP = async function() {
    const email = document.getElementById('forgotEmail').value;
    if (!email) return showToast("Enter registered email first", "error");

    try {
        let res = await fetch('/api/forgot-password', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        let data = await res.json().catch(() => ({ detail: "Server API Error (500)" }));
        if (res.ok) showToast(data.message || "Reset code sent if account exists.", "success");
        else showToast(data.detail || data.error || "Failed to send reset code", "error");
    } catch (e) { showToast("Network Disconnected", "error"); }
};

window.submitLogin = async function() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        let res = await fetch('/api/login', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (res.ok) {
            showToast("Welcome Admin!", "success");
            checkAuthWall();
        } else {
            let data = await res.json().catch(() => ({ detail: "Login failed (Server Error)" }));
            showToast(data.detail || data.error || "Login failed", "error");
        }
    } catch (e) { showToast("Network Disconnected", "error"); }
};

window.submitRegister = async function() {
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const otp = document.getElementById('regOTP').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        let res = await fetch('/api/register', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, otp, password })
        });
        
        if (res.ok) {
            showToast("Admin account verified! Please login.", "success");
            toggleAuth('login');
        } else {
            let data = await res.json().catch(() => ({ detail: "Registration Error" }));
            showToast(data.detail || data.error || "Error", "error");
        }
    } catch (e) { showToast("Network Disconnected", "error"); }
};

window.submitForgotPassword = async function() {
    const email = document.getElementById('forgotEmail').value;
    const otp = document.getElementById('forgotOTP').value;
    const new_password = document.getElementById('forgotNewPassword').value;

    try {
        let res = await fetch('/api/reset-password', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password })
        });
        let data = await res.json().catch(() => ({ detail: "Reset Password Error" }));
        if (res.ok) {
            showToast(data.message || "Password reset successful! Please sign in.", "success");
            toggleAuth('login');
        } else {
            showToast(data.detail || data.error || "Failed to reset password", "error");
        }
    } catch (e) { showToast("Network Disconnected", "error"); }
};

window.toggleAuth = function(type) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotForm = document.getElementById('forgotForm');
    const authTitle = document.getElementById('authTitle');

    loginForm.classList.add('hidden');
    registerForm.classList.add('hidden');
    if (forgotForm) forgotForm.classList.add('hidden');

    if (type === 'register') {
        registerForm.classList.remove('hidden');
        authTitle.innerText = "Create Admin";
    } else if (type === 'forgot' && forgotForm) {
        forgotForm.classList.remove('hidden');
        authTitle.innerText = "Reset Password";
    } else {
        loginForm.classList.remove('hidden');
        authTitle.innerText = "Sign In";
    }
};

// Patient Profile Configuration
window.savePatient = function() {
    const name = document.getElementById('patientName').value || "Unknown";
    document.getElementById('patientText').innerText = `Patient: ${name}`;
    closeModal('patientContainer');
};

// --- Database Integrations (Session Logic) ---
let sessionId = null;
const sessionToggleBtn = document.getElementById('sessionToggleBtn');
const sessionIndicator = document.getElementById('sessionIndicator');
const sessionText = document.getElementById('sessionText');

if (sessionToggleBtn) {
    sessionToggleBtn.addEventListener('click', async () => {
        if (!sessionId) {
            // Send patient name and age for active exercise session
            let currentName = document.getElementById('patientName') ? (document.getElementById('patientName').value || "Unknown") : "Unknown";
            let currentAge = document.getElementById('patientAge') ? (parseInt(document.getElementById('patientAge').value) || 0) : 0;
            
            let res = await fetch('/api/session/start', { 
                method: 'POST',
                credentials: 'include',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: currentName, age: currentAge })
            });
            let json = await res.json();
            let payload = json?.data ?? json;
            sessionId = payload.session_id;
            
            sessionIndicator.className = "w-3 h-3 rounded-full bg-appleRed shadow-[0_0_8px_#FF3B30] animate-pulse";
            sessionText.innerText = "Stop Session";
            window.currentReps = 0;
            if (repCounter) repCounter.innerText = "0";
            showToast("Exercise session started", "success");
        } else {
            let currentReps = parseInt(repCounter.innerText) || 0;
            let res = await fetch('/api/session/stop', { 
                method: 'POST', 
                credentials: 'include',
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({session_id: sessionId, reps: currentReps}) 
            });
            sessionId = null;
            sessionIndicator.className = "w-3 h-3 rounded-full bg-appleGreen shadow-[0_0_8px_#34C759]";
            sessionText.innerText = "Start Session";
            if (res.ok) showToast("Session saved to clinical logs", "success");
        }
    });
}

// --- Database Integrations (Ultra-Wide Premium History) ---
async function fetchHistory() {
    try {
        // Dynamically resize history modal container
        document.getElementById('historyContainer').classList.remove('w-96', 'w-[580px]');
        document.getElementById('historyContainer').classList.add('w-[720px]');

        let res = await fetch('/api/history', { credentials: 'include' });
        let json = await res.json();
        let data = json?.data ?? json;
        let html = '';
        data.forEach(session => {
            let dateObj = new Date(session.start_time);
            let day = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
            let date = dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' });
            let time = dateObj.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
            
            let avatar = (session.name && session.name !== "Unknown") ? session.name.charAt(0).toUpperCase() : "G";

            html += `
            <div class="bg-white/70 dark:bg-black/40 rounded-[20px] p-5 mb-4 flex justify-between items-center border border-white/50 dark:border-white/10 shadow-lg hover:scale-[1.015] transition-transform backdrop-blur-md relative overflow-hidden">
                <!-- Glossy Glare Effect -->
                <div class="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-white/40 to-transparent dark:from-white/5 pointer-events-none"></div>
                
                <div class="flex items-center gap-5 z-10">
                    <div class="h-14 w-14 rounded-full bg-gradient-to-tr from-appleBlue to-cyan-400 text-white flex items-center justify-center font-extrabold text-2xl shadow-[0_4px_15px_rgba(0,122,255,0.4)] border-2 border-white/40">
                        ${avatar}
                    </div>
                    <div class="flex flex-col">
                        <div class="flex items-center gap-3">
                            <span class="text-xl font-extrabold text-gray-900 dark:text-white tracking-wide">${session.name}</span>
                            <span class="bg-black/10 dark:bg-white/10 px-2 py-0.5 rounded border border-black/5 dark:border-white/10 text-[11px] font-bold text-gray-700 dark:text-gray-300 shadow-inner">${session.age} Y/O</span>
                        </div>
                        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider mt-1">${day}, ${date} • ${time}</span>
                    </div>
                </div>
                <div class="flex flex-col items-end pr-2 z-10">
                    <span class="text-5xl font-black text-appleBlue tracking-tighter leading-none drop-shadow-sm">${session.total_reps}</span>
                    <span class="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest mt-2">Reps</span>
                </div>
            </div>`;
        });
        document.getElementById('historyList').innerHTML = html || '<p class="text-center text-gray-500 text-sm mt-4 font-medium">No sessions found.</p>';
    } catch(e) {
        console.error("Error fetching history", e);
    }
}

// --- Theme Segmented Control & iOS Slider ---
const themeLight = document.getElementById('themeLight');
const themeDark = document.getElementById('themeDark');

window.toggleGlobalTheme = function() {
    const isDark = document.documentElement.classList.contains('dark');
    setTheme(!isDark);
};

window.setTheme = function(isDark) {
    const knob = document.getElementById('iosThemeKnob');
    if (isDark) {
        document.documentElement.classList.add('dark');
        if (themeDark && themeLight) {
            themeDark.className = "flex-1 py-1.5 text-sm font-medium z-10 transition-colors rounded-lg text-gray-200 dark:text-white bg-transparent shadow-none dark:bg-[#3A3A3C] dark:shadow-sm";
            themeLight.className = "flex-1 py-1.5 text-sm font-medium z-10 transition-colors rounded-lg text-black dark:text-gray-400 bg-transparent shadow-none";
        }
        if (knob) {
            knob.classList.remove('translate-x-0');
            knob.classList.add('translate-x-6'); // Slide right (Dark mode)
        }
    } else {
        document.documentElement.classList.remove('dark');
        if (themeDark && themeLight) {
            themeLight.className = "flex-1 py-1.5 text-sm font-medium z-10 transition-colors rounded-lg text-black dark:text-gray-400 bg-white shadow-sm dark:bg-transparent dark:shadow-none";
            themeDark.className = "flex-1 py-1.5 text-sm font-medium z-10 transition-colors rounded-lg text-gray-500 dark:text-white bg-transparent shadow-none";
        }
        if (knob) {
            knob.classList.remove('translate-x-6');
            knob.classList.add('translate-x-0'); // Slide left (Light mode)
        }
    }
};


// --- Edge AI & CV Pipeline (Client-Side Processing) ---
const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d', { willReadFrequently: true });

let is_gripping = false;
window.currentReps = 0; // Expose globally for session recording
let last_rep_time = 0;

// Reset Button Logic
const resetBtn = document.getElementById('resetBtn');
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        window.currentReps = 0;
        if (repCounter) repCounter.innerText = window.currentReps;
        closeModal('settingsContainer');
    });
}

function calculateDistance(p1, p2) {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
}


function onResults(results) {
    // Match canvas dimensions to actual camera hardware resolution
    if (canvasElement.width !== videoElement.videoWidth) {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
    }

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Render HD camera frame with mirrored orientation
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

    let hand_in_frame = false;

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        hand_in_frame = true;
        for (const landmarks of results.multiHandLandmarks) {
            // Draw Hand Tracking AR Skeleton
            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#007AFF', lineWidth: 4});
            drawLandmarks(canvasCtx, landmarks, {color: '#34C759', lineWidth: 2, radius: 3});

            // Grip Detection Logic (Enterprise Grade Precaution)
            const wrist = landmarks[0];
            const indexTip = landmarks[8];   // Index Finger Tip
            const middleTip = landmarks[12]; // Middle Finger Tip
            const ringTip = landmarks[16];   // Ring Finger Tip

            // 1. Calculate average distance across 3 fingertips (Anti-jitter)
            const dIndex = calculateDistance(wrist, indexTip);
            const dMiddle = calculateDistance(wrist, middleTip);
            const dRing = calculateDistance(wrist, ringTip);
            const avgDistance = (dIndex + dMiddle + dRing) / 3;

            const currentTime = Date.now();

            // 2. Grip threshold: Close grip required (Average < 0.15)
            if (avgDistance < 0.15 && !is_gripping) {
                is_gripping = true;
            
            // 3. Release threshold and cooldown logic
            // Open hand threshold (Average > 0.20)
            } else if (avgDistance > 0.20 && is_gripping) {
                is_gripping = false;
                
                // 800ms cooldown threshold to filter ghost reps
                if (currentTime - last_rep_time > 800) {
                    window.currentReps++;
                    if (repCounter) repCounter.innerText = window.currentReps;
                    last_rep_time = currentTime;
                }
            }
        }
    }

    // Reset grip status if hand leaves frame during active squeeze
    if (!hand_in_frame && is_gripping) {
        is_gripping = false;
    }

    // Update UI Status
    if (gripStatus) {
        if (is_gripping) {
            gripStatus.innerText = "GRIPPING";
            gripStatus.className = "text-lg font-bold text-appleRed transition-all";
        } else {
            gripStatus.innerText = "OPEN";
            gripStatus.className = "text-lg font-bold text-appleBlue transition-all";
        }
    }

    canvasCtx.restore();
}

// Initialize Google MediaPipe Hands SDK
const hands = new Hands({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
}});

hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1, // 0 = Fast/Light, 1 = Balanced/Accurate
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7,
    selfieMode: true // Let the Edge AI handle the mirror transformation natively
});
hands.onResults(onResults);

let cameraEngine = null;

function startAREngine() {
    if(cameraEngine) return;
    cameraEngine = new Camera(videoElement, {
        onFrame: async () => { await hands.send({image: videoElement}); },
        width: 1280, height: 720, facingMode: "environment"
    });
    cameraEngine.start();
}

function stopAREngine() {
    if(cameraEngine) {
        cameraEngine.stop();
        cameraEngine = null;
    }
}


// --- Chroma Key (Green Screen Removal) Engine ---
const guideVideo = document.getElementById('guideVideo');
const chromaCanvas = document.getElementById('chromaCanvas');
if (guideVideo && chromaCanvas) {
    const chromaCtx = chromaCanvas.getContext('2d', { willReadFrequently: true });
    
    // Auto-play the guide video
    guideVideo.play().catch(e => console.log("Video auto-play blocked by browser", e));

    function processChromaKey() {
        if (guideVideo.paused || guideVideo.ended) return;
        
        chromaCtx.drawImage(guideVideo, 0, 0, chromaCanvas.width, chromaCanvas.height);
        let frame = chromaCtx.getImageData(0, 0, chromaCanvas.width, chromaCanvas.height);
        
        for (let i = 0; i < frame.data.length; i += 4) {
            let r = frame.data[i + 0], g = frame.data[i + 1], b = frame.data[i + 2];
            let maxRb = Math.max(r, b);
            
            // Advanced Soft Masking
            if (g > 90 && g > maxRb * 1.1) {
                let greenDiff = g - maxRb;
                // High color distance = fully transparent. Small distance = blend alpha.
                let alpha = greenDiff > 30 ? 0 : 255 - (greenDiff * 8);
                frame.data[i + 3] = Math.max(0, Math.min(255, alpha));
            }
        }
        
        chromaCtx.putImageData(frame, 0, 0);
        requestAnimationFrame(processChromaKey);
    }
    guideVideo.addEventListener('play', processChromaKey);
}

// --- Live Scrolling Chart (Apple Style Graph) ---
const emgCanvas = document.getElementById('emgGraph');
const mockMvc = document.getElementById('mockMvc');

if (emgCanvas && mockMvc) {
    const emgCtx = emgCanvas.getContext('2d');
    const emgHistory = new Array(40).fill(0);

    function drawEmgGraph() {
        // Dynamically scale canvas dimensions
        if (emgCanvas.clientWidth > 0 && emgCanvas.width !== emgCanvas.clientWidth * 2) {
            emgCanvas.width = emgCanvas.clientWidth * 2;
            emgCanvas.height = emgCanvas.clientHeight * 2;
        }
        if (emgCanvas.width === 0) return; // Skip rendering if modal or element is hidden

        emgCtx.clearRect(0, 0, emgCanvas.width, emgCanvas.height);
        const isDark = document.documentElement.classList.contains('dark');
        
        let gradient = emgCtx.createLinearGradient(0, 0, 0, emgCanvas.height);
        gradient.addColorStop(0, isDark ? 'rgba(10, 132, 255, 0.4)' : 'rgba(0, 122, 255, 0.4)');
        gradient.addColorStop(1, 'rgba(0, 122, 255, 0)');

        emgCtx.beginPath();
        emgCtx.lineWidth = 4;
        emgCtx.strokeStyle = isDark ? '#0A84FF' : '#007AFF';
        emgCtx.lineJoin = 'round';

        const sliceWidth = emgCanvas.width / (emgHistory.length - 1);
        let x = 0;
        
        for (let i = 0; i < emgHistory.length; i++) {
            let normalizedY = emgCanvas.height - (emgHistory[i] / 100) * (emgCanvas.height * 0.9);
            if (i === 0) emgCtx.moveTo(x, normalizedY);
            else emgCtx.lineTo(x, normalizedY);
            x += sliceWidth;
        }
        
        emgCtx.stroke();
        emgCtx.lineTo(emgCanvas.width, emgCanvas.height);
        emgCtx.lineTo(0, emgCanvas.height);
        emgCtx.fillStyle = gradient;
        emgCtx.fill();
    }

    // --- REST Telemetry Polling Engine ---
    async function updateEmgFromBackend() {
        try {
            let res = await fetch('/api/emg/telemetry', { credentials: 'include' });
            if (!res.ok) return;
            let json = await res.json();
            let data = json?.data ?? json;

            // 1. Update LWT Node Status
            const dot = document.getElementById('emgNodeDot');
            const icon = document.getElementById('nodeStatusIcon');
            const text = document.getElementById('nodeStatusText');
            const macDisplay = document.getElementById('nodeMacAddress');

            if (macDisplay) macDisplay.innerText = data.mac;

            if (data.is_online) {
                if (dot) dot.className = "flex h-2.5 w-2.5 rounded-full bg-appleGreen shadow-[0_0_8px_#34C759] animate-pulse transition-all duration-300";
                if (icon) icon.className = "w-3 h-3 rounded-full bg-appleGreen shadow-[0_0_8px_#34C759] animate-pulse transition-all duration-300";
                if (text) {
                    text.innerText = "ONLINE";
                    text.className = "text-[10px] font-semibold text-appleGreen uppercase tracking-wider mt-0.5";
                }
            } else {
                if (dot) dot.className = "flex h-2.5 w-2.5 rounded-full bg-appleRed shadow-[0_0_8px_#FF3B30] transition-all duration-300";
                if (icon) icon.className = "w-3 h-3 rounded-full bg-appleRed shadow-[0_0_8px_#FF3B30] transition-all duration-300";
                if (text) {
                    text.innerText = "OFFLINE";
                    text.className = "text-[10px] font-semibold text-appleRed uppercase tracking-wider mt-0.5";
                }
            }

            // 2. Update Graph Data
            if (data.percent !== null && data.percent !== undefined) {
                mockMvc.innerText = `${data.percent}%`;
                emgHistory.push(data.percent);
            } else {
                mockMvc.innerText = `--%`;
                // If MVC is not calibrated yet, show responsive raw grip preview (0-4095 scale for MyoWare 2.0)
                let preview = Math.min(100, Math.round(((data.raw || 0) / 4095) * 100));
                emgHistory.push(preview);
            }

            const rawEl = document.getElementById('mockBaseline');
            const mvcEl = document.getElementById('mockPeak');
            if (rawEl) rawEl.innerText = data.raw;
            if (mvcEl) mvcEl.innerText = data.mvc > 0 ? data.mvc : 'Not Set';

            if (data.calibrating) {
                mockMvc.innerText = "CAL!";
                mockMvc.classList.add('text-appleRed', 'animate-pulse');
            } else {
                mockMvc.classList.remove('text-appleRed', 'animate-pulse');
            }

            emgHistory.shift();
            drawEmgGraph();

        } catch (e) {
            // Silently ignore connection errors
        }
    }

    window.startEmgPolling = function() {
        if (emgPollingTimer) return;
        updateEmgFromBackend();
        // Refresh every 50ms for smooth 20fps telemetry animation
        emgPollingTimer = setInterval(updateEmgFromBackend, 50);
    };

    window.stopEmgPolling = function() {
        if (emgPollingTimer) {
            clearInterval(emgPollingTimer);
            emgPollingTimer = null;
        }
    };

    // Control Command Functions
    window.mqttPublishCommand = async function(cmd) {
        try {
            let res = await fetch(`/api/emg/command/${cmd}`, {
                method: 'POST',
                credentials: 'include'
            });
            let result = await res.json();
            if (res.ok) {
                showToast(`[${cmd.toUpperCase()}] sent successfully!`, 'success');
            } else {
                showToast(result.detail || result.error || 'Failed to send command', 'error');
            }
        } catch (e) {
            showToast('Network error!', 'error');
        }
    };
}

// --- Manual Node Linker (Persists across browser refresh) ---
window.saveMacAddress = async function() {
    const mac = document.getElementById('inputMacAddress').value;
    if(!mac) return showToast("Enter MAC Address first!", "error");
    
    const btn = document.querySelector('#inputMacAddress').nextElementSibling;
    const oriText = btn.innerText;
    btn.innerText = "LINKING...";
    
    try {
        let res = await fetch('/api/emg/set-mac', {
            method: 'POST',
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mac: mac})
        });
        
        if(res.ok) {
            localStorage.setItem("artiq_target_mac", mac.toUpperCase().replace(/[:\s]/g, ""));
            showToast("Hardware Node Linked!", "success");
        } else {
            showToast("Failed to link node", "error");
        }
    } catch(e) {
        showToast("Network Error", "error");
    } finally {
        btn.innerText = oriText;
    }
};