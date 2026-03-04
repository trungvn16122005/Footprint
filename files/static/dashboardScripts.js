// Ishaal
// dashboardScripts.js
document.addEventListener('DOMContentLoaded', () => {


    // ===== Theme toggle =====
    const toggle = document.getElementById("themeToggle");
    if (toggle) {
        toggle.addEventListener("click", () => {
            document.body.classList.toggle("dark");
        });
    }

    // ===== Logout button =====
    const logOutBtn = document.getElementById("logOutBtn");
    if (logOutBtn) {
        logOutBtn.addEventListener("click", () => {
            window.location.href = "/logout";
        });
    }


// ===== Breach Check Form (Combined Ishaal, Terry, & Khang Logic) =====
const form = document.getElementById("breachCheckForm");
const loadingIndicator = document.getElementById("loadingIndicator");
const resultsCard = document.getElementById("resultsCard");
const breachResults = document.getElementById("breachResults");
const resultsPlaceholder = document.getElementById("resultsPlaceholder");

const MIN_LOADING_TIME = 5000;

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // 1. Capture All Inputs
        const userEmail = document.getElementById("userEmail").value.trim();
        const additionalEmail = document.getElementById("additionalEmail").value.trim();
        const userPassword = document.getElementById("userPassword").value;
        const websiteURL = document.getElementById("websiteURL").value.trim();

        if (!userEmail && !additionalEmail && !userPassword && !websiteURL) {
            showError("Please enter info to check.");
            return;
        }

        // 2. UI Reset
        if (resultsPlaceholder) resultsPlaceholder.style.display = "none";
        resultsCard.style.display = "none";
        loadingIndicator.style.display = "flex";

        const startTime = Date.now();

        try {
            let emailResults = [];
            let passwordResult = null;
            let trackerResult = null;

            const promises = [];

            // ISHAAL: Email scans
            if (userEmail) {
                promises.push(checkEmailBreach(userEmail)
                    .then(res => emailResults.push({ ...res, email: userEmail }))
                    .catch(err => emailResults.push({ email: userEmail, breached: false, error: err.message })));
            }
            if (additionalEmail) {
                promises.push(checkEmailBreach(additionalEmail)
                    .then(res => emailResults.push({ ...res, email: additionalEmail }))
                    .catch(err => emailResults.push({ email: additionalEmail, breached: false, error: err.message })));
            }

            // ISHAAL: Password scan
            if (userPassword) {
                promises.push(checkPasswordPwned(userPassword).then(res => passwordResult = res));
            }

            // TERRY: DuckDuckGo Radar scan
            if (websiteURL) {
                promises.push(
                    fetch("/api/scan-url", {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "X-CSRFToken": document.querySelector('input[name="csrf_token"]')?.value || ""
                        },
                        body: JSON.stringify({ url: websiteURL })
                    })
                    .then(res => res.json())
                    .then(data => trackerResult = data)
                    .catch(err => console.error("Tracker scan failed:", err))
                );
            }

            // 3. Wait for all scans to finish
            await Promise.all(promises);

            const elapsed = Date.now() - startTime;
            if (elapsed < MIN_LOADING_TIME) {
                await delay(MIN_LOADING_TIME - elapsed);
            }

            loadingIndicator.style.display = "none";

            // 4. DISPLAY ALL RESULTS (Ishaal & Terry)
            displayResults(emailResults, passwordResult, trackerResult);

            // 5. KHANG: Data Removal Protocol Trigger
            const hasEmailBreaches = emailResults.some(r => r.breached && r.breaches.length > 0);
            if (hasEmailBreaches) {
                const allBreaches = emailResults
                    .filter(r => r.breached && r.breaches.length > 0)
                    .flatMap(r => r.breaches);
                const uniqueBreaches = [...new Set(allBreaches)];
                renderRemovalProtocol(uniqueBreaches);
            }

        } catch (error) {
            loadingIndicator.style.display = "none";
            showError(error.message);
        }
    });
}

    // ===== Helpers (Ishaal) =====
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function checkEmailBreach(email) {
        const response = await fetch("/api/check-breach", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `API error: ${response.status}`);
        }

        return data;
    }

    async function checkPasswordPwned(password) {
        const response = await fetch("/api/check-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `API error: ${response.status}`);
        }

        return data;
    }

// Helper to make the "Show More" buttons work for long breach lists
function attachToggleListeners() {
  document.querySelectorAll('.breachToggleBtn').forEach(btn => {
      btn.addEventListener('click', (e) => {
          const targetId = e.target.dataset.target;
          const hiddenCount = e.target.dataset.hiddenCount;
          const container = document.getElementById(targetId);

          if (container && container.classList.contains('expanded')) {
              container.classList.remove('expanded');
              e.target.textContent = `Show ${hiddenCount} more`;
          } else if (container) {
              container.classList.add('expanded');
              e.target.textContent = 'Show less';
          }
      });
  });
}

// ===== Display Results (Combined Ishaal & Terry) =====
function displayResults(emailResults, passwordResult, trackerResult) {
  if (resultsPlaceholder) {
      resultsPlaceholder.style.display = "none";
  }
  resultsCard.style.display = "block";
  breachResults.innerHTML = "";

  let resultsHTML = "";

  // 1. TERRY: Tracker Radar / Risk Score Section (Static UI)
  if (trackerResult) {
      const score = trackerResult.risk_score || 1;
      // Define colors based on risk level
      const color = score >= 7 ? "#dc3545" : (score >= 4 ? "#ffc107" : "#28a745");
      const riskText = score >= 7 ? "High Risk" : (score >= 4 ? "Moderate Risk" : "Low Risk");

      resultsHTML += `
          <div class="tracker-analysis-card" style="border: 1px solid #ddd; border-left: 6px solid ${color}; background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <h4 style="margin: 0; color: #333;">Privacy Analysis: ${trackerResult.url}</h4>
                  <span style="background: ${color}; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                      ${riskText} (${score}/10)
                  </span>
              </div>
              
              <div style="background: #e9ecef; height: 12px; border-radius: 6px; overflow: hidden; margin: 15px 0;">
                  <div style="width: ${score * 10}%; background: ${color}; height: 100%;"></div>
              </div>

              <p style="font-size: 0.95rem; color: #555; margin: 0; line-height: 1.5;">
                  ${trackerResult.is_tracker 
                      ? `⚠️ <strong>Warning:</strong> This site is a known tracker owned by <b>${trackerResult.owner}</b>. It may be collecting your browsing habits.` 
                      : `✅ <strong>Safe:</strong> This domain was not found in the DuckDuckGo Radar tracker database.`}
              </p>
          </div>
      `;
  }

  // 2. Password Results Section (Ishaal)
  if (passwordResult) {
      if (passwordResult.breached) {
          resultsHTML += `
              <div class="passwordBreachResult breached ${passwordResult.severity}">
                  <div class="passwordBreachHeader">
                      <span class="passwordBreachIcon">⚠️</span>
                      <h4>Password Compromised</h4>
                  </div>
                  <p class="passwordBreachMessage">${passwordResult.message}</p>
                  <p class="passwordBreachAdvice">We strongly recommend changing this password immediately.</p>
                  <div class="passwordBreachSeverity">
                      <span class="severityLabel">Severity:</span>
                      <span class="severityBadge ${passwordResult.severity}">${passwordResult.severity.toUpperCase()}</span>
                  </div>
              </div>
          `;
      } else {
          resultsHTML += `
              <div class="passwordBreachResult safe">
                  <div class="passwordBreachHeader">
                      <span class="passwordBreachIcon">✅</span>
                      <h4>Password Not Found in Breaches</h4>
                  </div>
                  <p class="passwordBreachMessage">${passwordResult.message}</p>
              </div>
          `;
      }
  }

  // 3. Email Results Section (Ishaal)
  if (emailResults && emailResults.length > 0) {
      emailResults.forEach(result => {
          if (result.error) {
              resultsHTML += `
                  <div class="emailBreachNotice">
                      <h4>Email Check Error for ${result.email}</h4>
                      <p>${result.error}</p>
                  </div>
              `;
          } else if (!result.breached || result.breaches.length === 0) {
              resultsHTML += `
                  <div class="noBreachFound">
                      <h4>Good News!</h4>
                      <p>No breaches found for <strong>${result.email}</strong></p>
                  </div>
              `;
          } else {
              resultsHTML += `
                  <div class="emailBreachSection">
                      <div class="emailBreachHeader breached">
                          <span class="breachIcon">⚠️</span>
                          <h4>Breaches Found for ${result.email}</h4>
                      </div>
                      <p class="breachSummary">Found in <strong>${result.breaches.length}</strong> data breaches:</p>
                      <div class="breachList">
                          ${result.breaches.map(b => `<span class="breachTag">${b}</span>`).join('')}
                      </div>
                  </div>
              `;
          }
      });
  }

  breachResults.innerHTML = resultsHTML;

  // Re-attach toggle listeners if you have "Show More" buttons
  attachToggleListeners();

  // Scroll to results
  resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
    // ===== Show Error =====
    function showError(message) {
        if (resultsPlaceholder) {
            resultsPlaceholder.style.display = "none";
        }
        loadingIndicator.style.display = "none";
        resultsCard.style.display = "block";
        breachResults.innerHTML = `
            <div class="errorMessage">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }

    
    // Khang — Data Removal Protocol (API)
    
    async function fetchRemovalProviders() {
        const res = await fetch("/api/removal/providers");
        if (!res.ok) throw new Error("Failed to load removal providers");
        return res.json();
    }

    async function fetchRemovalSummary() {
        const res = await fetch("/api/removal/summary");
        if (!res.ok) throw new Error("Failed to load removal summary");
        return res.json();
    }

    async function postRemovalAction(providerId, status) {
        await fetch("/api/removal/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ provider_id: providerId, status })
        });
    }

    async function fetchBreachActions(breaches) {
        const res = await fetch("/api/removal/breach-actions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ breaches })
        });
        if (!res.ok) throw new Error("Failed to load breach actions");
        return res.json();
    }

    async function renderRemovalProtocol(breaches) {
        // New structure: breaches + summary in left column, providers in separate dashboard
        const summarySection = document.getElementById("removalProtocolSummary");
        const breachesListEl = document.getElementById("removalBreachesList");
        const summaryEl = document.getElementById("removalSummary");
        const breachActionsDashboard = document.getElementById("breachActionsDashboard");
        const breachActionsEl = document.getElementById("breachSpecificActions");
        const providersDashboard = document.getElementById("providersDashboard");
        const providersEl = document.getElementById("removalProviders");

        if (breaches.length === 0) return;

        // Show the left column summary section
        if (summarySection) summarySection.style.display = "block";
        // Show the breach-specific actions dashboard
        if (breachActionsDashboard) breachActionsDashboard.style.display = "block";
        // Show the providers dashboard
        if (providersDashboard) providersDashboard.style.display = "block";

        if (breachesListEl) {
            breachesListEl.innerHTML = '<p class="removalLoading">Loading...</p>';
        }
        if (providersEl) {
            providersEl.innerHTML = '<p class="removalLoading">Loading removal options...</p>';
        }
        if (breachActionsEl) {
            breachActionsEl.innerHTML = '<p class="removalLoading">Loading breach-specific actions...</p>';
        }

        try {
            // Fetch providers, summary, and breach-specific actions in parallel
            const [providers, summary, breachActionsData] = await Promise.all([
                fetchRemovalProviders(),
                fetchRemovalSummary(),
                fetchBreachActions(breaches)
            ]);

            // Build a map of latest status per provider from summary
            const statusMap = {};
            if (summary.actions) {
                summary.actions.forEach(action => {
                    // Only keep the latest status per provider (actions are ordered desc)
                    if (!statusMap[action.provider_id]) {
                        statusMap[action.provider_id] = action.status;
                    }
                });
            }

            // Display breach names in the LEFT column (with toggle for long lists)
            const MAX_VISIBLE_REMOVAL_BREACHES = 15;
            const visibleRemovalBreaches = breaches.slice(0, MAX_VISIBLE_REMOVAL_BREACHES);
            const hiddenRemovalBreaches = breaches.slice(MAX_VISIBLE_REMOVAL_BREACHES);

            let breachTagsHTML = visibleRemovalBreaches.map(b => `<span class="breachTagSmall">${b}</span>`).join('');

            if (hiddenRemovalBreaches.length > 0) {
                breachTagsHTML += `
                    <div class="hiddenBreaches" id="hiddenRemovalBreaches">
                        ${hiddenRemovalBreaches.map(b => `<span class="breachTagSmall">${b}</span>`).join('')}
                    </div>
                    <button class="breachToggleBtn removalToggleBtn" data-target="hiddenRemovalBreaches" data-hidden-count="${hiddenRemovalBreaches.length}">
                        Show ${hiddenRemovalBreaches.length} more
                    </button>
                `;
            }

            if (breachesListEl) {
                breachesListEl.innerHTML = `
                    <div class="breachesFound">
                        <h4>Your Data Found In:</h4>
                        <div class="breachTagList">
                            ${breachTagsHTML}
                        </div>
                    </div>
                `;

                // Add toggle listener for breach expand/collapse
                const removalToggleBtn = breachesListEl.querySelector('.removalToggleBtn');
                if (removalToggleBtn) {
                    removalToggleBtn.addEventListener('click', (e) => {
                        const targetId = e.target.dataset.target;
                        const hiddenCount = e.target.dataset.hiddenCount;
                        const container = document.getElementById(targetId);

                        if (container.classList.contains('expanded')) {
                            container.classList.remove('expanded');
                            e.target.textContent = `Show ${hiddenCount} more`;
                        } else {
                            container.classList.add('expanded');
                            e.target.textContent = 'Show less';
                        }
                    });
                }
            }

            // Render breach-specific actions (high priority - shown first)
            const breachActions = breachActionsData.actions || [];
            if (breachActionsEl && breachActions.length > 0) {
                const breachActionsHTML = breachActions.map(action => {
                    const priorityClass = action.priority === 'high' ? 'priority-high' :
                                         action.priority === 'medium' ? 'priority-medium' : 'priority-low';
                    const actionTypeLabel = action.action_type === 'account_security' ? '🔐 Security Action' :
                                           action.action_type === 'account_deletion' ? '🗑️ Account Deletion' : '⚠️ Action Required';

                    return `
                        <div class="breachActionCard ${priorityClass}">
                            <div class="breachActionHeader">
                                <div class="breachActionInfo">
                                    <span class="breachActionType">${actionTypeLabel}</span>
                                    <h4 class="breachActionName">${action.company}</h4>
                                    <span class="breachActionPriority priority-badge-${action.priority}">${action.priority.toUpperCase()} PRIORITY</span>
                                </div>
                            </div>
                            <div class="breachActionBody">
                                <a href="${action.url}" target="_blank" rel="noopener noreferrer" class="breachActionLink">
                                    Go to Security Settings
                                </a>
                                <div class="breachActionSteps">
                                    <strong>Recommended Steps:</strong>
                                    <ol>
                                        ${action.steps.map(step => `<li>${step}</li>`).join('')}
                                    </ol>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');

                breachActionsEl.innerHTML = breachActionsHTML;
            } else if (breachActionsEl) {
                breachActionsEl.innerHTML = '<p class="noBreachActions">No specific remediation actions found for these breaches. Follow the data broker removal steps below.</p>';
            }

            // Render provider cards in the SEPARATE dashboard below
            const providersHTML = providers.map(p => {
                const currentStatus = statusMap[p.id] || "Not started";
                const steps = p.steps || [];

                return `
                    <div class="providerCard" data-provider-id="${p.id}">
                        <div class="providerHeader">
                            <div class="providerInfo">
                                <h4 class="providerName">${p.name}</h4>
                                ${p.eta ? `<span class="providerEta">ETA: ${p.eta}</span>` : ''}
                            </div>
                            <div class="statusBadge status-${currentStatus.toLowerCase().replace(' ', '-')}" data-provider-id="${p.id}" data-status="${currentStatus}">
                                ${currentStatus.toUpperCase()}
                            </div>
                        </div>
                        <div class="providerBody">
                            <a href="${p.optOutUrl}" target="_blank" rel="noopener noreferrer" class="optOutLink">
                                Open Opt-Out Page
                            </a>
                            ${steps.length > 0 ? `
                                <div class="providerSteps">
                                    <strong>Steps:</strong>
                                    <ol>
                                        ${steps.map(step => `<li>${step}</li>`).join('')}
                                    </ol>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            if (providersEl) {
                providersEl.innerHTML = providersHTML;

                // Add click listeners to status badges to cycle through statuses
                providersEl.querySelectorAll('.statusBadge').forEach(badge => {
                    badge.style.cursor = 'pointer';
                    badge.title = 'Click to change status';
                    badge.addEventListener('click', async (e) => {
                        const providerId = e.target.dataset.providerId;
                        const currentStatus = e.target.dataset.status;

                        // Cycle through statuses: Not started → Submitted → Completed → Not started
                        const statusOrder = ['Not started', 'Submitted', 'Completed'];
                        const currentIndex = statusOrder.indexOf(currentStatus);
                        const newStatus = statusOrder[(currentIndex + 1) % statusOrder.length];

                        try {
                            await postRemovalAction(providerId, newStatus);
                            // Update badge appearance
                            e.target.dataset.status = newStatus;
                            e.target.className = `statusBadge status-${newStatus.toLowerCase().replace(' ', '-')}`;
                            e.target.textContent = newStatus.toUpperCase();
                            // Refresh summary
                            const updatedSummary = await fetchRemovalSummary();
                            renderSummary(summaryEl, updatedSummary);
                        } catch (err) {
                            console.error("Failed to update status:", err);
                            alert("Failed to save status. Please try again.");
                        }
                    });
                });
            }

            // Render formatted summary in left column
            renderSummary(summaryEl, summary);

        } catch (err) {
            console.error("Failed to load removal protocol:", err);
            if (breachesListEl) {
                breachesListEl.innerHTML = '<p class="removalError">Failed to load. Please refresh.</p>';
            }
            if (providersEl) {
                providersEl.innerHTML = '<p class="removalError">Failed to load removal protocol. Please refresh the page.</p>';
            }
        }
    }

    function renderSummary(summaryEl, summary) {
        const submitted = summary.submitted || 0;
        const completed = summary.completed || 0;
        const total = summary.actions ? summary.actions.length : 0;
        const notStarted = total - submitted - completed;

        summaryEl.innerHTML = `
            <div class="summaryStats">
                <div class="summaryItem">
                    <span class="summaryCount summaryNotStarted">${notStarted >= 0 ? notStarted : 0}</span>
                    <span class="summaryLabel">Not Started</span>
                </div>
                <div class="summaryItem">
                    <span class="summaryCount summarySubmitted">${submitted}</span>
                    <span class="summaryLabel">Submitted</span>
                </div>
                <div class="summaryItem">
                    <span class="summaryCount summaryCompleted">${completed}</span>
                    <span class="summaryLabel">Completed</span>
                </div>
            </div>
        `;
    }

// ==================================================
// Trung Nguyen — Ratings Sidebar (DB-backed by URL)
// - scanned URLs stored locally (list only)
// - ratings/comments stored in DB using /api/url-reviews
// - clicking a site shows preview (top 2 reviews)
// - View opens internal page: /ratings?url=...
// ==================================================
(function TrungRatingsDB() {
  const form = document.getElementById("breachCheckForm");
  const urlInput = document.getElementById("websiteURL");

  const ratingListEl = document.getElementById("sidebarRatingList");
  const emptyStateEl = document.getElementById("sidebarEmptyState");
  const sortSelect = document.getElementById("sidebarSort");

  const selectedSiteLabel = document.getElementById("selectedSiteLabel");
  const previewEl = document.getElementById("selectedReviewsPreview");

  const reviewStars = document.getElementById("reviewStars");
  const reviewText = document.getElementById("reviewText");
  const submitReviewBtn = document.getElementById("submitReviewBtn");
  const reviewMsg = document.getElementById("reviewMsg");

  if (!ratingListEl || !emptyStateEl) return;

  const STORAGE_SCANNED = "fp_scanned_sites_v1";

  let selectedUrl = null;
  let summaryCache = {}; // { url: {avg, count} }

  function readJSON(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  }

  function writeJSON(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function normalizeUrl(raw) {
    if (!raw) return null;
    let s = raw.trim();
    if (!s) return null;
    if (!/^https?:\/\//i.test(s)) s = `https://${s}`;
    try {
      const u = new URL(s);
      return `${u.origin}${u.pathname}`.replace(/\/+$/, "");
    } catch {
      return null;
    }
  }

  function hostLabel(url) {
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch {
      return url;
    }
  }

  function stars(v) {
    const n = Number(v || 0);
    if (!n) return "☆☆☆☆☆";
    const rounded = Math.round(n * 2) / 2;
    let out = "";
    for (let i = 1; i <= 5; i++) out += (rounded >= i ? "★" : "☆");
    return out;
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function setMessage(msg, isError = false) {
    if (!reviewMsg) return;
    reviewMsg.textContent = msg || "";
    reviewMsg.style.color = isError ? "#dc2626" : "";
  }

  function validateReviewForm() {
    if (!submitReviewBtn) return;
    const ratingVal = reviewStars ? reviewStars.value : "";
    const commentVal = reviewText ? reviewText.value.trim() : "";
    submitReviewBtn.disabled = !(selectedUrl && ratingVal && commentVal.length >= 3);
  }

  function getScannedSites() {
    return readJSON(STORAGE_SCANNED, []); // [{url,lastScannedAt}]
  }

  function setScannedSites(sites) {
    writeJSON(STORAGE_SCANNED, sites);
  }

  function upsertScanned(url) {
    const sites = getScannedSites();
    const now = Date.now();
    const idx = sites.findIndex(s => s.url === url);
    if (idx >= 0) sites[idx].lastScannedAt = now;
    else sites.push({ url, lastScannedAt: now });
    setScannedSites(sites);
  }

  async function fetchSummaries(urls) {
    // uses /api/url-review-summaries so sidebar is fast
    const res = await fetch("/api/url-review-summaries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load summaries");
    return data.summaries || {};
  }

  function sortSites(sites, mode) {
    const m = mode || "relevant";
    const withStats = sites.map(s => {
      const stats = summaryCache[s.url] || { avg: 0, count: 0 };
      return { ...s, avg: stats.avg || 0, count: stats.count || 0 };
    });

    if (m === "highest") {
      withStats.sort((a, b) => (b.avg - a.avg) || (b.count - a.count) || (b.lastScannedAt - a.lastScannedAt));
      return withStats;
    }
    if (m === "lowest") {
      withStats.sort((a, b) => (a.avg - b.avg) || (a.count - b.count) || (b.lastScannedAt - a.lastScannedAt));
      return withStats;
    }
    if (m === "newest") {
      withStats.sort((a, b) => b.lastScannedAt - a.lastScannedAt);
      return withStats;
    }

    // relevant: reviewed first, then newest
    withStats.sort((a, b) => (b.count - a.count) || (b.lastScannedAt - a.lastScannedAt));
    return withStats;
  }

  async function loadPreview(url) {
    if (!previewEl) return;
    previewEl.style.display = "none";
    previewEl.innerHTML = "";

    if (!url) return;

    try {
      const res = await fetch(`/api/url-reviews?url=${encodeURIComponent(url)}&limit=2`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load preview");

      const reviews = data.reviews || [];
      if (!reviews.length) {
        previewEl.style.display = "block";
        previewEl.innerHTML = `<div class="reviewPreviewMeta">No reviews yet. Be the first to write one.</div>`;
        return;
      }

      previewEl.style.display = "block";
      previewEl.innerHTML = reviews.map(r => `
        <div class="reviewPreviewItem">
          <div class="reviewPreviewStars">${stars(r.rating)} <span style="color:var(--muted); font-weight:800;">(${r.rating}/5)</span></div>
          <div class="reviewPreviewText">${escapeHtml(r.comment)}</div>
          <div class="reviewPreviewMeta">${escapeHtml(r.username || "User")}</div>
        </div>
      `).join("");
    } catch (e) {
      previewEl.style.display = "block";
      previewEl.innerHTML = `<div class="reviewPreviewMeta">Unable to load preview.</div>`;
    }
  }

  function setSelected(url) {
    selectedUrl = url;
    setMessage("");

    if (!selectedSiteLabel) return;

    if (!url) {
      selectedSiteLabel.textContent = "Select a website from the list to review.";
      if (submitReviewBtn) submitReviewBtn.disabled = true;
      if (previewEl) { previewEl.style.display = "none"; previewEl.innerHTML = ""; }
      return;
    }

    const stats = summaryCache[url] || { avg: 0, count: 0 };
    const avgText = stats.count ? stats.avg.toFixed(1) : "--";

    selectedSiteLabel.textContent =
      `Reviewing: ${hostLabel(url)} • Overall: ${avgText} ${stars(stats.avg)} • ${stats.count} reviews`;

    validateReviewForm();
    loadPreview(url);
    renderSidebar(); // highlight selected
  }

  async function renderSidebar() {
    const sites = getScannedSites();
    if (!sites.length) {
      emptyStateEl.style.display = "block";
      ratingListEl.innerHTML = "";
      setSelected(null);
      return;
    }

    // refresh summaries from DB
    try {
      summaryCache = await fetchSummaries(sites.map(s => s.url));
    } catch {
      // if summaries fail, keep old cache (still render)
    }

    emptyStateEl.style.display = "none";

    const sorted = sortSites(sites, sortSelect ? sortSelect.value : "relevant");

    ratingListEl.innerHTML = sorted.map(s => {
      const stats = summaryCache[s.url] || { avg: 0, count: 0 };
      const avgText = stats.count ? stats.avg.toFixed(1) : "--";
      const cls = selectedUrl === s.url ? "selected" : "";

      return `
        <div class="sidebarRatingItem ${cls}" data-url="${s.url}">
          <div class="sidebarRatingThumb" aria-hidden="true"></div>

          <div class="sidebarRatingInfo">
            <div class="sidebarRatingTitle">${hostLabel(s.url)}</div>
            <div class="sidebarRatingUrl">${s.url}</div>
            <div class="sidebarRatingStars" aria-label="stars">${stars(stats.avg)}</div>
            <div class="sidebarRatingMeta">
              <span>Rating: ${avgText}</span>
              <span>•</span>
              <span>Reviews: ${stats.count}</span>
            </div>
          </div>

          <div class="sidebarRatingAction">
            <button type="button" class="sidebarViewBtn">View</button>
          </div>
        </div>
      `;
    }).join("");
  }

  // Events
  if (sortSelect) sortSelect.addEventListener("change", renderSidebar);

  ratingListEl.addEventListener("click", (e) => {
    const item = e.target.closest(".sidebarRatingItem");
    if (!item) return;

    const url = item.dataset.url;
    if (!url) return;

    const btn = e.target.closest("button");
    if (btn && btn.classList.contains("sidebarViewBtn")) {
      // Open internal ratings page (looks like “external” reviews site)
      window.open(`/ratings?url=${encodeURIComponent(url)}`, "_blank", "noopener,noreferrer");
      return;
    }

    setSelected(url);
  });

  if (reviewStars) reviewStars.addEventListener("change", validateReviewForm);
  if (reviewText) reviewText.addEventListener("input", validateReviewForm);

// Khang /Create an submission for review 2/23/2026
  if (submitReviewBtn) {
    submitReviewBtn.addEventListener("click", async () => {
      setMessage("");

      if (!selectedUrl) return setMessage("Select a website first.", true);

      const rating = parseInt(reviewStars.value || "0", 10);
      const comment = (reviewText.value || "").trim();

      if (!rating) return setMessage("Pick a rating.", true);
      if (comment.length < 3) return setMessage("Write a short comment (min 3 chars).", true);

      try {
        const res = await fetch("/api/url-reviews", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: selectedUrl, rating, comment })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to submit review");

        reviewStars.value = "";
        reviewText.value = "";
        validateReviewForm();

        setMessage("Review submitted!");
        await renderSidebar();
        setSelected(selectedUrl); // refresh label + preview
      } catch (err) {
        setMessage(err.message || "Failed to submit review.", true);
      }
    });
  }

  // Register scanned URL when scan form is submitted (only if scan is valid by Ishaal rules)
  if (form) {
    form.addEventListener("submit", () => {
        const userEmailEl = document.getElementById("userEmail");
        const additionalEmailEl = document.getElementById("additionalEmail");
        const userPasswordEl = document.getElementById("userPassword");

        const userEmail = userEmailEl ? userEmailEl.value.trim() : "";
        const additionalEmail = additionalEmailEl ? additionalEmailEl.value.trim() : "";
        const userPassword = userPasswordEl ? userPasswordEl.value : "";

      // match Ishaal validation: if scan won't run, don't store
      if (!userEmail && !additionalEmail && !userPassword) return;

      const normalized = normalizeUrl(urlInput ? urlInput.value : "");
      if (!normalized) return;

      upsertScanned(normalized);
      renderSidebar();
      setSelected(normalized);
    });
  }

  // first render
  renderSidebar();
})();

// ==================================================
// Trung Nguyen — Ratings Page (loads DB reviews for a URL)
// Page: /ratings?url=...
// ==================================================
(function TrungRatingsPage() {
  const root = document.getElementById("ratingsPageRoot");
  if (!root) return; // only run on ratings page

  function normalizeUrl(raw) {
    if (!raw) return null;
    let s = raw.trim();
    if (!s) return null;
    if (!/^https?:\/\//i.test(s)) s = `https://${s}`;
    try {
      const u = new URL(s);
      return `${u.origin}${u.pathname}`.replace(/\/+$/, "");
    } catch {
      return null;
    }
  }

  function hostLabel(url) {
    try { return new URL(url).hostname.replace(/^www\./, ""); }
    catch { return url; }
  }

  function stars(v) {
    const n = Number(v || 0);
    if (!n) return "☆☆☆☆☆";
    const rounded = Math.round(n * 2) / 2;
    let out = "";
    for (let i = 1; i <= 5; i++) out += (rounded >= i ? "★" : "☆");
    return out;
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  const params = new URLSearchParams(window.location.search);
  const raw = params.get("url") || "";
  const url = normalizeUrl(raw);

  const titleEl = document.getElementById("ratingsTitle");
  const subEl = document.getElementById("ratingsSub");
  const summaryEl = document.getElementById("ratingsSummaryLine");
  const listEl = document.getElementById("ratingsList");
  const emptyEl = document.getElementById("ratingsEmpty");
  const sortEl = document.getElementById("ratingsSortSelect");
  const filterRadios = Array.from(document.querySelectorAll('input[name="ratingFilter"]'));

  if (!url) {
    if (titleEl) titleEl.textContent = "Website Reviews";
    if (subEl) subEl.textContent = "Invalid or missing URL";
    if (emptyEl) { emptyEl.style.display = "block"; emptyEl.textContent = "Missing URL. Open this page from the sidebar View button."; }
    return;
  }

  if (titleEl) titleEl.textContent = `Reviews for ${hostLabel(url)}`;

  let allReviews = [];
  let avgRating = 0;
  let reviewCount = 0;

  function currentFilter() {
    const chosen = filterRadios.find(r => r.checked);
    return chosen ? chosen.value : "any";
  }

  function currentSort() {
    return sortEl ? sortEl.value : "newest";
  }

  function render() {
    let reviews = [...allReviews];

    const f = currentFilter();
    if (f !== "any") {
      const wanted = Number(f);
      reviews = reviews.filter(r => Number(r.rating) === wanted);
    }

    const s = currentSort();
    if (s === "highest") {
      reviews.sort((a, b) => (b.rating - a.rating) || (new Date(b.created_at) - new Date(a.created_at)));
    } else if (s === "lowest") {
      reviews.sort((a, b) => (a.rating - b.rating) || (new Date(b.created_at) - new Date(a.created_at)));
    } else {
      reviews.sort((a, b) => (new Date(b.created_at) - new Date(a.created_at)));
    }

    if (!reviews.length) {
      listEl.innerHTML = "";
      emptyEl.style.display = "block";
      return;
    }

    emptyEl.style.display = "none";

    listEl.innerHTML = reviews.map(r => `
      <div class="reviewRow">
        <div class="reviewThumb" aria-hidden="true"></div>
        <div>
          <div class="reviewHeaderLine">
            <div class="reviewUser">${escapeHtml(r.username || "User")}</div>
            <div class="reviewDate">${formatDate(r.created_at)}</div>
          </div>
          <div class="reviewStarsLine">
            ${stars(r.rating)} <span style="color:var(--muted); font-weight:900;">(${r.rating}/5)</span>
          </div>
          <div class="reviewComment">${escapeHtml(r.comment)}</div>
        </div>
      </div>
    `).join("");
  }

  async function load() {
    const res = await fetch(`/api/url-reviews?url=${encodeURIComponent(url)}&limit=200`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load reviews");

    allReviews = data.reviews || [];
    avgRating = data.avg_rating || 0;
    reviewCount = data.review_count || 0;

    subEl.textContent = `${reviewCount} review${reviewCount === 1 ? "" : "s"}`;
    summaryEl.textContent = reviewCount
      ? `Overall: ${avgRating.toFixed(1)} ${stars(avgRating)} • ${reviewCount} total`
      : "No ratings yet.";

    render();
  }

  filterRadios.forEach(r => r.addEventListener("change", render));
  if (sortEl) sortEl.addEventListener("change", render);

  load().catch(err => {
    emptyEl.style.display = "block";
    emptyEl.textContent = err.message || "Failed to load reviews.";
  });
})();
    
});
