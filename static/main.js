console.log("🚀 main.js loaded");

document.getElementById("taskForm").onsubmit = async (e) => {
  e.preventDefault();

  const start = +document.getElementById("start").value;
  const end = +document.getElementById("end").value;
  const companies = document.getElementById("companies").value.split(",");

  console.log("📥 Submitted filters:", { start, end, companies });

  const res = await fetch("/create-task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end, companies })
  });

  const { task_id } = await res.json();
  const statusDiv = document.getElementById("status");
  statusDiv.innerText = `⏳ Task ${task_id} submitted. Waiting for completion...`;

  const interval = setInterval(async () => {
    const r = await fetch(`/task-status/${task_id}`);
    const { status } = await r.json();
    console.log(`🔁 Task ${task_id} status: ${status}`);
    statusDiv.innerText = `🔁 Task ${task_id} status: ${status}`;

    if (status === "completed") {
      clearInterval(interval);
      console.log("🟢 Task completed, fetching analytics...");

      const response = await fetch(`/analytics/${task_id}`);
      const data = await response.json();
      console.log("🎯 Analytics data:", data);
      drawBarChart(data);
    }
  }, 2000);
};

function drawBarChart(data) {
  const svg = d3.select("#barChart");
  const width = +svg.attr("width");
  const height = +svg.attr("height");
  const margin = { top: 30, right: 30, bottom: 50, left: 60 };

  svg.selectAll("*").remove(); // clear existing chart

  const grouped = d3.rollup(data, v => d3.sum(v, d => d.price), d => d.company);
  const entries = Array.from(grouped, ([company, total]) => ({ company, total }));

  if (entries.length === 0) {
  svg.html("");
  svg.append("text")
    .text("No data available for the selected filters.")
    .attr("x", 20)
    .attr("y", 40)
    .style("font-size", "16px")
    .style("fill", "gray");
  return;
}

  const x = d3.scaleBand()
    .domain(entries.map(d => d.company))
    .range([margin.left, width - margin.right])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(entries, d => d.total)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  svg.append("g")
    .selectAll("rect")
    .data(entries)
    .enter()
    .append("rect")
    .attr("x", d => x(d.company))
    .attr("y", d => y(d.total))
    .attr("height", d => height - margin.bottom - y(d.total))
    .attr("width", x.bandwidth())
    .attr("fill", "steelblue")
    .attr("class", "bar")
    .on("mouseover", (e, d) => {
      tooltip.transition().duration(200).style("opacity", 0.9);
      tooltip.html(`<strong>${d.company}</strong><br>$${d.total.toFixed(2)}`)
        .style("left", e.pageX + "px")
        .style("top", (e.pageY - 28) + "px");
    })
    .on("mouseout", () => {
      tooltip.transition().duration(500).style("opacity", 0);
    });

  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x));

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y));

  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .attr("text-anchor", "middle")
    .text("Company");

  svg.append("text")
    .attr("text-anchor", "middle")
    .attr("transform", `translate(${margin.left - 40},${height / 2})rotate(-90)`)
    .text("Total Sales ($)");
}
