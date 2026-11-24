    async function startEmergency() {
    const lane = document.getElementById("ambulanceLane").value;

    try {
        const response = await fetch("/api/emergency/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ lane: lane })
        });

        const data = await response.json();

        document.getElementById("emergencyMessage").textContent =
            data.message + (data.priority_lane
                ? " - Priority Lane: " + data.priority_lane
                : "");

        await updateDashboard();

    } catch (error) {
        alert("Unable to activate emergency!");
    }
}


async function stopEmergency() {
    try {
        const response = await fetch("/api/emergency/stop", {
            method: "POST"
        });

        const data = await response.json();

        document.getElementById("emergencyMessage").textContent =
            data.message;

        await updateDashboard();

    } catch (error) {
        alert("Unable to stop emergency!");
    }
}

   async function updateDashboard() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();

        document.getElementById("system").textContent = data.system;

        document.getElementById("ambulance").textContent =
            data.ambulance_detected ? "Detected" : "Not Detected";

        const emergencyAlert = document.getElementById("emergencyAlert");

        if (data.emergency_active) {
            emergencyAlert.style.display = "block";
            emergencyAlert.textContent =
                "🚨 AMBULANCE DETECTED! PRIORITY LANE: " + data.current_lane;
        } else {
            emergencyAlert.style.display = "none";
        }
        document.getElementById("traffic").textContent =
            data.traffic_signal;

        document.getElementById("lane").textContent =
            data.current_lane;

        document.getElementById("time").textContent =
            data.remaining_time;

        document.getElementById("emergency").textContent =
            data.emergency_active ? "Active" : "Inactive";

        
// Update live traffic density
const signalLanes = ["north", "south", "east", "west"];

signalLanes.forEach(lane => {

    const capitalLane =
        lane.charAt(0).toUpperCase() + lane.slice(1);

    document.getElementById(lane + "Count").textContent =
        data.traffic_counts[capitalLane];

    document.getElementById(lane + "Density").textContent =
        data.traffic_density[capitalLane];
});

        // Update all four traffic signals
        const lanes = ["north", "south", "east", "west"];

        lanes.forEach(lane => {
            const signal = data.lane_signals[
                lane.charAt(0).toUpperCase() + lane.slice(1)
            ];

            const light = document.getElementById(lane);
            const status = document.getElementById(lane + "Status");

            light.className = "light";

            if (signal === "GREEN") {
                light.classList.add("active");
                status.textContent = "GREEN";
            } else {
                status.textContent = "RED";
            }
        });

    } catch (error) {
        document.getElementById("system").textContent = "Offline";
        console.error("Dashboard error:", error);
    }
}

    updateDashboard();
    setInterval(updateDashboard, 2000);

async function loadEmergencyHistory() {

    try {
        const response = await fetch("/api/emergency/history");
        const data = await response.json();

        const table = document.getElementById("historyTable");

        table.innerHTML = "";

        if (data.events.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="4">No emergency records found.</td>
                </tr>
            `;
            return;
        }

        data.events.forEach(event => {

            const row = document.createElement("tr");

            [
                event.event,
                event.date_time,
                event.ambulance_lane,
                event.previous_signal_lane
            ].forEach(value => {

                const cell = document.createElement("td");
                cell.textContent = value;
                cell.style.padding = "12px";
                row.appendChild(cell);

            });

            table.appendChild(row);

        });

    } catch (error) {
        console.error("History loading error:", error);
    }
}

loadEmergencyHistory();

