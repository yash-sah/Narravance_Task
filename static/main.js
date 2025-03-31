console.log("🚀 main.js loaded");

document.getElementById("taskForm").onsubmit = async (e) => {
  e.preventDefault();

  const start = +document.getElementById("start").value;
  const end = +document.getElementById("end").value;
  const companies = document.getElementById("companies").value.split(",").map(c => c.trim());

  console.log("📥 Submitted filters:", { start, end, companies });

  try {
    const res = await fetch("/create-task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start, end, companies })
    });

    const { task_id } = await res.json();
    console.log("🆕 Task created with ID:", task_id);

    const statusDiv = document.getElementById("status");

const interval = setInterval(async () => {
  const r = await fetch(`/task-status/${task_id}`);
  const json = await r.json();
  console.log("📡 Polled status response:", json); // ✅ Inspect response here

  const { status } = json;
  statusDiv.innerText = `Task Status: ${status}`;

  if (status === "completed") {
    clearInterval(interval);

    console.log("🟢 Task completed, fetching analytics...");
    const response = await fetch(`/analytics/${task_id}`);
    const data = await response.json();
    console.log("🎯 Final analytics data:", data);
    drawBarChart(data);
  }
}, 2000);

  } catch (submitError) {
    console.error("❌ Error creating task:", submitError);
  }
};

function drawBarChart(data) {
  console.log("📊 Chart Data Received:", data);

  try {
    const grouped = d3.rollup(
      data,
      v => d3.sum(v, d => +d.price),
      d => d.company
    );

    const entries = Array.from(grouped, ([company, total]) => ({ company, total }));
    console.log("🧮 Grouped entries for bar chart:", entries);

    const svg = d3.select("#barChart");
    svg.selectAll("*").remove();

    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const x = d3.scaleBand()
      .domain(entries.map(d => d.company))
      .range([0, width])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(entries, d => d.total)])
      .range([height, 0]);

    svg.selectAll("rect")
      .data(entries)
      .enter()
      .append("rect")
      .attr("x", d => x(d.company))
      .attr("y", d => y(d.total))
      .attr("width", x.bandwidth())
      .attr("height", d => height - y(d.total))
      .attr("fill", "steelblue");

    svg.selectAll("text")
      .data(entries)
      .enter()
      .append("text")
      .text(d => d.total)
      .attr("x", d => x(d.company) + x.bandwidth() / 2)
      .attr("y", d => y(d.total) - 5)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "black");

    console.log("✅ Chart rendered successfully.");
  } catch (chartError) {
    console.error("❌ Error rendering chart:", chartError);
  }
}
