let currentIndex = -1;
const map = document.getElementById("factory-map");
const info = document.getElementById("info-panel");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const dots = [];

// Show point data in the info panel
function showPoint(point) {
  const text = `
    <b>ID: ${point.id}</b><br>
    Planta: ${point.planta || "?"}<br>
    Planta número: ${point["planta-numero"] || "?"}<br>
    DN: ${point.DN || "?"}<br>
    OD: ${point["OD mm"] || "?"} mm<br>
    WT: ${point["WT mm"] || "?"} mm<br>
    Flow velocity: ${point["Flow velocity ms"] || "?"} m/s<br>
    Volume flow rate: ${point["volume flow rate m3h"] || "?"} m3/h
  `;
  info.innerHTML = text;
}

// Enable / disable navigation buttons
function updateButtons() {
  prevBtn.disabled = currentIndex <= 0;
  nextBtn.disabled = currentIndex >= points.length - 1;
}

// Update dot positions on resize
function updateDots() {
  if (!map || !points || points.length === 0) return;

  const { offsetWidth, offsetHeight } = map;

  points.forEach((point, i) => {
    const x = point.x_rel * offsetWidth;
    const y = point.y_rel * offsetHeight;

    if (dots[i]) {
      dots[i].style.left = x + "px";
      dots[i].style.top = y + "px";
    }
  });
}

// Helper: remove .selected from all dots
function clearSelectedDots() {
  dots.forEach(dot => {
    dot.classList.remove("selected");
  });
}

// Helper: mark the dot at `index` as selected
function markDotSelected(index) {
  if (dots[index]) {
    dots[index].classList.add("selected");
  }
}

window.addEventListener("load", () => {
  if (!map || !points || points.length === 0) {
    info.innerHTML = "❌ No points loaded. Check <code>points.js</code>.";
    return;
  }

  const { offsetWidth, offsetHeight } = map;

  points.forEach((point, i) => {
    const x = point.x_rel * offsetWidth;
    const y = point.y_rel * offsetHeight;

    const dot = document.createElement("div");
    dot.className = "point";
    dot.style.left = x + "px";
    dot.style.top = y + "px";

    // Clicking a dot selects that point, updates panel, and marks the dot
    dot.addEventListener("click", (e) => {
      clearSelectedDots();
      currentIndex = i;
      updateButtons();
      showPoint(point);
      markDotSelected(currentIndex);
      e.stopPropagation();
    });

    const mapContainer = document.querySelector(".map-container");
    mapContainer.appendChild(dot);
    dots.push(dot);
  });

  // Prev / Next buttons (only define once, inside load)
  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      clearSelectedDots();
      currentIndex--;
      updateButtons();
      showPoint(points[currentIndex]);
      markDotSelected(currentIndex);
    }
  });

  nextBtn.addEventListener("click", () => {
    if (currentIndex < points.length - 1) {
      clearSelectedDots();
      currentIndex++;
      updateButtons();
      showPoint(points[currentIndex]);
      markDotSelected(currentIndex);
    }
  });

  // Start with the first point selected
  if (points.length > 0) {
    currentIndex = 0;
    updateButtons();
    showPoint(points[0]);
    markDotSelected(0);
  }

  // When the window resizes, reposition the dots
  window.addEventListener("resize", updateDots);
});