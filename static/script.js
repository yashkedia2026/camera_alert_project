// Fetch and display event log
async function fetchEvents() {
  const res = await fetch("/api/events");
  const data = await res.json();
  const container = document.getElementById("events-container");
  container.innerHTML = "";

  if (data.length === 0) {
    container.innerHTML = "<p>No recent events found.</p>";
    return;
  }

  for (const ev of data) {
    const card = document.createElement("div");
    card.className = "event-card";

    const img = document.createElement("img");
    img.src = ev.snapshot_path;
    img.alt = "Snapshot";
    img.onclick = () => openModal(ev.snapshot_path);

    const info = document.createElement("div");
    info.className = "event-info";
    info.innerHTML = `
      <h3>${ev.name}</h3>
      <p>${new Date(ev.timestamp).toLocaleString()}</p>
    `;

    card.appendChild(img);
    card.appendChild(info);
    container.appendChild(card);
  }
}

// Open image modal
function openModal(src) {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  modalImg.src = src;
  modal.style.display = "flex";
}

// Button bindings
document.getElementById("refresh-btn").onclick = fetchEvents;

document.getElementById("clear-btn").onclick = () => {
  const container = document.getElementById("events-container");
  container.innerHTML = "<p>Recent events cleared (not deleted from DB).</p>";
};

window.onload = fetchEvents;
