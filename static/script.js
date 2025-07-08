document.addEventListener("DOMContentLoaded", () => {
  applyFilters();  // initial load
});

function getDateRangeParams() {
  const start = document.getElementById("filterStart").value;
  const end   = document.getElementById("filterEnd").value;
  return (start && end) ? `?start=${start}&end=${end}` : "";
}

function applyFilters() {
  loadEvents();
  loadAttendance();
}

// ─── Unknown‐face events ────────────────────────────────────────────────────
function loadEvents() {
  const params = getDateRangeParams();
  fetch(`/api/events${params}`)
    .then(res => res.json())
    .then(events => {
      const container = document.getElementById("eventsList");
      container.innerHTML = "";
      if (events.length === 0) {
        container.innerHTML = "<li>No events in this range.</li>";
        return;
      }
      events.forEach(ev => {
        const li = document.createElement("li");
        li.innerHTML = `
          <div class="event-entry">
            <a href="${ev.snapshot_path}" target="_blank" class="event-link">
              <strong>${ev.name}</strong> — ${ev.timestamp}
            </a>
            <button class="btn btn-delete"
                    title="Delete"
                    onclick="deleteEvent(${ev.id})">
              ❌
            </button>
          </div>`;
        container.appendChild(li);
      });
    });
}

function deleteEvent(id) {
  if (!confirm("Delete this event?")) return;
  fetch(`/api/delete_event/${id}`, { method: "DELETE" })
    .then(() => loadEvents());
}

function clearEvents() {
  if (!confirm("Delete ALL unknown-face events?")) return;
  fetch("/api/clear_events", { method: "DELETE" })
    .then(() => loadEvents());
}

function exportEventsCSV() {
  const params = getDateRangeParams();
  window.open(`/api/events${params}&format=csv`, "_blank");
}

// ─── Employee attendance ────────────────────────────────────────────────────
function loadAttendance() {
  const params = getDateRangeParams();
  fetch(`/api/employee_log${params}`)
    .then(res => res.json())
    .then(logs => {
      const tbody = document.getElementById("attendanceBody");
      tbody.innerHTML = "";
      if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center">No records</td></tr>`;
        return;
      }
      logs.forEach(emp => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${emp.name}</td>
          <td>${emp.date}</td>
          <td>${emp.first_seen}</td>
          <td>${emp.last_seen}</td>`;
        tbody.appendChild(row);
      });
    });
}

function exportAttendance() {
  const params = getDateRangeParams();
  // will download .xlsx via new /api/export_attendance endpoint
  window.location = `/api/export_attendance${params}`;
}
