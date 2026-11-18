const $ = (id) => document.getElementById(id);
let allPlaces = [];
let chosenInterests = new Set();

function money(n) {
  return n == null || Number.isNaN(Number(n)) ? "Fee not listed" : `PKR ${Number(n).toLocaleString()}`;
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
}
function placeCard(p) {
  const image = p.image ? `<img src="${esc(p.image)}" alt="${esc(p.place_name)}" loading="lazy" onerror="this.parentElement.classList.add('no-image');this.remove()">` : "";
  return `<article class="place-card"><div class="place-image ${p.image ? "" : "no-image"}">${image}<span class="place-city">${esc(p.city)}</span></div><div class="place-info"><div class="place-meta">${esc(p.category)} <span>★ ${p.rating == null ? "N/A" : Number(p.rating).toFixed(1)}</span></div><h3>${esc(p.place_name)}</h3><p>${esc(p.description)}</p><div class="place-bottom"><b>${money(p.entry_fee)}</b><span>${esc(p.interests)}</span></div></div></article>`;
}
async function getJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const data = await response.json(); message = data.detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}
function renderCards(items) {
  $("results").innerHTML = items.length ? items.map(placeCard).join("") : `<div class="empty">No destinations match these filters. Try increasing your budget or changing your selections.</div>`;
  $("resultCount").textContent = `${items.length} place${items.length === 1 ? "" : "s"} found`;
}
async function loadInitial() {
  try {
    const [places, filters] = await Promise.all([getJSON("/api/places"), getJSON("/api/filters")]);
    allPlaces = places;
    $("city").innerHTML = filters.cities.map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join("");
    $("interests").innerHTML = filters.interests.map(i => `<button type="button" class="chip" data-interest="${esc(i)}">${esc(i)}</button>`).join("");
    $("feedbackPlace").innerHTML = `<option value="">Choose a place</option>` + places.map(p => `<option value="${esc(p.place_name)}">${esc(p.place_name)}</option>`).join("");
    $("feedbackCount").textContent = `${filters.feedback_count} feedback entries received so far`;
    renderCards(places.slice(0, 6));
    $("interests").addEventListener("click", e => {
      const chip = e.target.closest("[data-interest]");
      if (!chip) return;
      const name = chip.dataset.interest;
      if (chosenInterests.has(name)) chosenInterests.delete(name); else chosenInterests.add(name);
      chip.classList.toggle("selected", chosenInterests.has(name));
    });
  } catch (e) {
    $("results").innerHTML = `<div class="empty error">Could not load destinations: ${esc(e.message)}. Check that the FastAPI server is running and your dataset path is correct.</div>`;
  }
}
async function findRecommendations() {
  $("findBtn").disabled = true;
  $("findBtn").textContent = "Finding places…";
  try {
    const payload = {
      budget: Number($("budget").value),
      city: $("city").value,
      interests: [...chosenInterests],
      minimum_rating: Number($("rating").value),
      number_of_recommendations: Number($("number").value)
    };
    const data = await getJSON("/api/recommend", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    $("resultsTitle").textContent = "Recommended for you";
    renderCards(data.recommendations);
  } catch (e) {
    $("results").innerHTML = `<div class="empty error">${esc(e.message)}</div>`;
  } finally {
    $("findBtn").disabled = false;
    $("findBtn").textContent = "Find destinations →";
  }
}
$("budget").addEventListener("input", () => $("budgetValue").textContent = Number($("budget").value).toLocaleString());
$("findBtn").addEventListener("click", findRecommendations);
$("resetBtn").addEventListener("click", () => {
  $("budget").value = 1000; $("budgetValue").textContent = "1,000";
  $("city").value = "All"; $("rating").value = "0"; $("number").value = "6";
  chosenInterests.clear(); document.querySelectorAll(".chip").forEach(c => c.classList.remove("selected"));
  $("resultsTitle").textContent = "Explore destinations"; renderCards(allPlaces.slice(0, 6));
});
$("feedbackForm").addEventListener("submit", async e => {
  e.preventDefault();
  $("feedbackMessage").textContent = "Submitting…";
  try {
    const result = await getJSON("/api/feedback", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({
      place_name:$("feedbackPlace").value, rating:Number($("feedbackRating").value), review:$("feedbackReview").value
    })});
    $("feedbackMessage").textContent = result.message;
    $("feedbackCount").textContent = `${result.feedback_count} feedback entries received so far`;
    $("feedbackForm").reset();
  } catch (err) { $("feedbackMessage").textContent = err.message; }
});
loadInitial();

// const API_BASE = "";

// const recommendationForm = document.getElementById("recommendationForm");
// const resultsContainer = document.getElementById("recommendationResults");
// const recommendationMessage = document.getElementById("recommendationMessage");

// const feedbackForm = document.getElementById("feedbackForm");
// const feedbackMessage = document.getElementById("feedbackMessage");

// let selectedRating = 0;

// async function loadFilters() {
//     try {
//         const response = await fetch(`${API_BASE}/api/filters`);
//         if (!response.ok) throw new Error("Could not load filters");

//         const data = await response.json();

//         const citySelect = document.getElementById("city");
//         const interestSelect = document.getElementById("interests");

//         if (citySelect && Array.isArray(data.cities)) {
//             citySelect.innerHTML = '<option value="All">All Cities</option>';
//             data.cities.forEach(city => {
//                 const option = document.createElement("option");
//                 option.value = city;
//                 option.textContent = city;
//                 citySelect.appendChild(option);
//             });
//         }

//         if (interestSelect && Array.isArray(data.interests)) {
//             interestSelect.innerHTML = '<option value="">All Interests</option>';
//             data.interests.forEach(interest => {
//                 const option = document.createElement("option");
//                 option.value = interest;
//                 option.textContent = interest;
//                 interestSelect.appendChild(option);
//             });
//         }
//     } catch (error) {
//         console.error(error);
//     }
// }

// function showMessage(element, message, isError = false) {
//     if (!element) return;
//     element.textContent = message;
//     element.style.color = isError ? "#c0392b" : "#087e8b";
// }

// function safeText(value) {
//     const element = document.createElement("span");
//     element.textContent = value ?? "";
//     return element.innerHTML;
// }

// function displayPlaces(places) {
//     if (!resultsContainer) return;

//     resultsContainer.innerHTML = "";

//     if (!Array.isArray(places) || places.length === 0) {
//         resultsContainer.innerHTML =
//             '<p class="empty-message">No destinations found. Try changing your filters.</p>';
//         return;
//     }

//     places.forEach(place => {
//         const card = document.createElement("article");
//         card.className = "place-card";

//         const name = safeText(place.place_name || "Tourist Destination");
//         const city = safeText(place.city || "");
//         const category = safeText(place.category || "");
//         const description = safeText(place.description || "Discover this destination.");
//         const rating = Number(place.rating || 0).toFixed(1);
//         const fee = Number(place.entry_fee || 0);
//         const image = place.image_url || "";

//         const imageElement = image
//             ? `<img src="${safeText(image)}" alt="${name}" onerror="this.style.display='none'">`
//             : "";

//         card.innerHTML = `
//             <div class="place-image">${imageElement}</div>
//             <div class="place-content">
//                 <span class="place-category">${category}</span>
//                 <h3>${name}</h3>
//                 <p class="place-city">📍 ${city}</p>
//                 <p>${description}</p>
//                 <div class="place-meta">
//                     <span>⭐ ${rating}</span>
//                     <span>💰 Rs. ${fee}</span>
//                 </div>
//                 <button type="button" class="btn btn-primary feedback-place-btn">
//                     Review this place
//                 </button>
//             </div>
//         `;

//         card.querySelector(".feedback-place-btn").addEventListener("click", () => {
//             const placeInput = document.getElementById("feedbackPlace");
//             if (placeInput) placeInput.value = place.place_name || "";
//             document.getElementById("feedback")?.scrollIntoView({ behavior: "smooth" });
//         });

//         resultsContainer.appendChild(card);
//     });
// }

// if (recommendationForm) {
//     recommendationForm.addEventListener("submit", async event => {
//         event.preventDefault();

//         const budget = Math.min(
//             500,
//             Number(document.getElementById("budget").value)
//         );

//         const payload = {
//             budget,
//             city: document.getElementById("city").value,
//             interests: document.getElementById("interests").value
//                 ? [document.getElementById("interests").value]
//                 : [],
//             minimum_rating: Number(document.getElementById("minimum_rating").value),
//             number_of_recommendations: Number(
//                 document.getElementById("number_of_recommendations").value
//             )
//         };

//         showMessage(recommendationMessage, "Finding your destinations...");

//         try {
//             const response = await fetch(`${API_BASE}/api/recommend`, {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify(payload)
//             });

//             const data = await response.json();

//             if (!response.ok) {
//                 throw new Error(data.detail || "Recommendation request failed");
//             }

//             const places = Array.isArray(data) ? data : (data.recommendations || data.places || []);
//             displayPlaces(places);
//             showMessage(recommendationMessage, `${places.length} destination(s) found.`);
//         } catch (error) {
//             showMessage(recommendationMessage, error.message, true);
//         }
//     });
// }

// const starButtons = document.querySelectorAll("#starRating button");

// starButtons.forEach(button => {
//     button.addEventListener("click", () => {
//         selectedRating = Number(button.dataset.rating);
//         document.getElementById("feedbackRating").value = selectedRating;

//         starButtons.forEach(star => {
//             star.classList.toggle(
//                 "active",
//                 Number(star.dataset.rating) <= selectedRating
//             );
//         });
//     });
// });

// if (feedbackForm) {
//     feedbackForm.addEventListener("submit", async event => {
//         event.preventDefault();

//         const placeName = document.getElementById("feedbackPlace").value.trim();
//         const review = document.getElementById("feedbackReview").value.trim();

//         if (!selectedRating) {
//             showMessage(feedbackMessage, "Please select a star rating.", true);
//             return;
//         }

//         try {
//             const response = await fetch(`${API_BASE}/api/feedback`, {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({
//                     place_name: placeName,
//                     rating: selectedRating,
//                     review: review
//                 })
//             });

//             const data = await response.json();

//             if (!response.ok) {
//                 throw new Error(data.detail || "Could not submit feedback");
//             }

//             showMessage(feedbackMessage, "Thank you! Your feedback has been submitted.");

//             feedbackForm.reset();
//             selectedRating = 0;
//             document.getElementById("feedbackRating").value = 0;
//             starButtons.forEach(star => star.classList.remove("active"));

//         } catch (error) {
//             showMessage(feedbackMessage, error.message, true);
//         }
//     });
// }

// loadFilters();
