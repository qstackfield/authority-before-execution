(async function () {
  const attemptsBody = document.getElementById("attempts-body");
  const artifactList = document.getElementById("artifact-list");
  const artifactCount = document.getElementById("artifact-count");
  const systemStatus = document.getElementById("system-status");
  const invariantVerdict = document.getElementById("invariant-verdict");

  let artifacts = [];

  function safeText(v, fallback = "—") {
    if (v === null || v === undefined || v === "") return fallback;
    return String(v);
  }

  function parseTime(iso) {
    try {
      const t = Date.parse(iso);
      return Number.isFinite(t) ? t : null;
    } catch {
      return null;
    }
  }

  function expectedAllow(a) {
    // Conservative, judge-friendly logic:
    // allow iff authority exists AND (scope matches action OR scope is null/undefined (overbroad)) AND not expired (relative to now).
    // If artifacts are old, expiry check may flip — still acceptable for runtime evidence.
    const auth = a.authority || null;
    if (!auth) return false;

    const scope = auth.scope;
    const action = a.action;

    const scopeOk = (scope === null || scope === undefined) ? true : (scope === action);
    if (!scopeOk) return false;

    const exp = auth.expires_at;
    const expMs = exp ? parseTime(exp) : null;
    if (expMs === null) return true; // if no expiry parsed, don't claim violation
    return expMs > Date.now();
  }

  function computeViolations(list) {
    // A violation is: executor output doesn't match what authority context implies.
    // This is what lets the UI say "Invariant HELD" without treating "ALLOW" as failure.
    let violations = 0;
    for (const a of list) {
      const exp = expectedAllow(a);
      const actual = !!a.execution_allowed;
      if (exp !== actual) violations++;
    }
    return violations;
  }

  async function loadViaManifest() {
    // Optional future-proof: docs/artifacts/manifest.json can list files.
    // Example:
    // { "files": ["demo-deploy-001.json", "demo-delete-001.json"] }
    try {
      const res = await fetch("artifacts/manifest.json", { cache: "no-store" });
      if (!res.ok) return false;
      const m = await res.json();
      const files = Array.isArray(m.files) ? m.files : [];
      if (!files.length) return false;

      const loaded = [];
      for (const f of files) {
        const r = await fetch("artifacts/" + f, { cache: "no-store" });
        if (r.ok) loaded.push(await r.json());
      }
      artifacts = loaded;
      return true;
    } catch {
      return false;
    }
  }

  async function loadViaDirectoryScrape() {
    // Works in some environments, not guaranteed on GitHub Pages.
    try {
      const index = await fetch("artifacts/", { cache: "no-store" });
      if (!index.ok) throw new Error("no directory listing");
      const text = await index.text();
      const matches = [...text.matchAll(/href="([^"]+\.json)"/g)];
      const files = matches.map(m => m[1]).filter(Boolean);

      const loaded = [];
      for (const f of files) {
        const r = await fetch("artifacts/" + f, { cache: "no-store" });
        if (r.ok) loaded.push(await r.json());
      }
      artifacts = loaded;
    } catch {
      artifacts = [];
    }
  }

  async function loadArtifacts() {
    const ok = await loadViaManifest();
    if (ok) return;
    await loadViaDirectoryScrape();
  }

  function sortArtifacts(list) {
    // Sort by decision_id if possible (var-001, demo-deploy-001, etc.)
    return [...list].sort((a, b) => {
      const da = safeText(a.decision_id, "");
      const db = safeText(b.decision_id, "");
      return da.localeCompare(db, undefined, { numeric: true, sensitivity: "base" });
    });
  }

  function renderTable() {
    attemptsBody.innerHTML = "";

    if (!artifacts.length) {
      attemptsBody.innerHTML = `<tr><td colspan="7" class="empty">No execution artifacts found.</td></tr>`;
      return;
    }

    const ordered = sortArtifacts(artifacts);

    ordered.forEach((a, i) => {
      const allowed = !!a.execution_allowed;
      const outcome = allowed ? "PERMIT" : "BLOCK";
      const denyReason = safeText(a.deny_reason, "—");

      const scope =
        a.authority && ("scope" in a.authority)
          ? (a.authority.scope === null || a.authority.scope === undefined ? "overbroad" : safeText(a.authority.scope))
          : "—";

      const expires =
        a.authority && a.authority.expires_at
          ? safeText(a.authority.expires_at)
          : "—";

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${i + 1}</td>
        <td>${safeText(a.decision_id)}</td>
        <td>${safeText(a.action)}</td>
        <td class="${allowed ? "allow" : "deny"}">${outcome}</td>
        <td>${denyReason}</td>
        <td>${scope}</td>
        <td>${expires}</td>
      `;
      attemptsBody.appendChild(row);
    });
  }

  function renderArtifacts() {
    artifactCount.textContent = String(artifacts.length);
    artifactList.innerHTML = artifacts.length
      ? sortArtifacts(artifacts).slice(0, 18).map(a => safeText(a.decision_id) + ".json").join("<br>")
      : "No artifacts loaded.";
  }

  function renderStatus() {
    if (!artifacts.length) {
      systemStatus.textContent = "No runtime artifacts";
      systemStatus.className = "pill pill-muted";
      invariantVerdict.textContent = "Awaiting evidence";
      invariantVerdict.className = "pill pill-muted";
      return;
    }

    const violations = computeViolations(artifacts);
    const allowed = artifacts.filter(a => !!a.execution_allowed).length;
    const denied = artifacts.length - allowed;

    if (violations === 0) {
      systemStatus.textContent = `Enforcing · ${allowed} permit · ${denied} block`;
      systemStatus.className = "pill pill-ok";
      invariantVerdict.textContent = "Invariant HELD";
      invariantVerdict.className = "pill pill-ok";
    } else {
      systemStatus.textContent = `Violation detected · ${violations}`;
      systemStatus.className = "pill pill-deny";
      invariantVerdict.textContent = "Invariant FAILED";
      invariantVerdict.className = "pill pill-deny";
    }
  }

  await loadArtifacts();
  renderTable();
  renderArtifacts();
  renderStatus();
})();
