// videorender.js - Background Processing Thread
let canvas = null;
let ctx = null;
let heartbeatInterval = null;


// --- Moved to Worker: Canvas Dynamic Test Pattern Generation ---
function drawTestPattern() {
    if (!ctx) return;

    // Clear background
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw sliding color grids
    const timeOffset = Date.now() * 0.002;
    for (let i = 0; i < 8; i++) {
        ctx.fillStyle = `hsl(${(i * 45 + timeOffset * 20) % 360}, 65%, 45%)`;
        ctx.fillRect(i * (canvas.width / 8), 30, canvas.width / 8, canvas.height - 90);
    }

    // Orbital vector display shape
    const centerX = canvas.width / 2 + Math.cos(timeOffset) * 120;
    const centerY = canvas.height / 2 + Math.sin(timeOffset * 1.3) * 60;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 25, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();


    // Overlay Burn-In Timestamp
    ctx.fillStyle = '#000000';
    ctx.fillRect(10, canvas.height - 50, canvas.width - 20, 40);
    
    ctx.fillStyle = '#00ff00';
    ctx.font = '16px monospace';
    ctx.fillText(`WORKER THREAD TIMER // UTC: ${new Date().toISOString()}`, 20, canvas.height - 24);
}

self.onmessage = function(e) {
    if (e.data.type === 'init') {
        canvas = e.data.canvas;
        ctx = canvas.getContext('2d');
        console.log("[Worker] Canvas control successfully transferred!");
    } 
    else if (e.data.type === 'start') {
        console.log("[Worker] Starting background rendering...");
        
        if (heartbeatInterval) clearInterval(heartbeatInterval);
        
        // Let's run it at 3 seconds for now to watch the background step work
        heartbeatInterval = setInterval(() => {
            console.log(`[Worker Heartbeat] Rendering frame at: ${new Date().toISOString()}`);
            drawTestPattern();
        }, 33); 
    } 
    else if (e.data.type === 'stop') {
        if (heartbeatInterval) clearInterval(heartbeatInterval);
    }
};
