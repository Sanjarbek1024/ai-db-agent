const form = document.getElementById("ask-form");
const input = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const btnLabel = askBtn.querySelector(".btn-label");
const btnSpinner = askBtn.querySelector(".btn-spinner");

const statusEl = document.getElementById("status");
const sqlPanel = document.getElementById("sql-panel");
const sqlCode = document.getElementById("sql-code");
const resultPanel = document.getElementById("result-panel");
const rowCountEl = document.getElementById("row-count");
const tableWrap = document.getElementById("table-wrap");
const errorPanel = document.getElementById("error-panel");
const errorText = document.getElementById("error-text");

function hide(el) { el.hidden = true; }
function show(el) { el.hidden = false; }

function resetPanels() {
    hide(sqlPanel);
    hide(resultPanel);
    hide(errorPanel);
    statusEl.textContent = "";
    hide(statusEl);
}

function setLoading(isLoading) {
    askBtn.disabled = isLoading;
    btnLabel.textContent = isLoading ? "Asking..." : "Ask";
    btnSpinner.hidden = !isLoading;
}

function renderTable(columns, rows) {
    if (rows.length === 0) {
        tableWrap.innerHTML = '<p style="padding:16px;color:var(--text-muted);font-family:var(--font-mono);font-size:13px;">No results found (0 rows).</p>';
        return;
    }

    const thead = `<thead><tr>${columns.map(c => `<th>${escapeHtml(c)}</th>`).join("")}</tr></thead>`;
    const tbody = `<tbody>${rows.map(row => (
        `<tr>${columns.map(c => `<td>${escapeHtml(row[c])}</td>`).join("")}</tr>`
    )).join("")}</tbody>`;

    tableWrap.innerHTML = `<table>${thead}${tbody}</table>`;
}

function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}

async function askQuestion(question) {
    resetPanels();
    setLoading(true);
    show(statusEl);
    statusEl.textContent = "Gemini SQL generating...";

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await res.json();
        hide(statusEl);

        if (data.generated_sql) {
            sqlCode.textContent = data.generated_sql;
            show(sqlPanel);
        }

        if (data.success) {
            rowCountEl.textContent = `${data.row_count} rows`;
            renderTable(data.columns, data.rows);
            show(resultPanel);
        } else {
            errorText.textContent = data.error || "An unknown error occurred.";
            show(errorPanel);
        }
    } catch (err) {
        hide(statusEl);
        errorText.textContent = "Error connecting to the server: " + err.message;
        show(errorPanel);
    } finally {
        setLoading(false);
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (question) askQuestion(question);
});

document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        input.value = chip.dataset.q;
        askQuestion(chip.dataset.q);
    });
});
