// Church Security Album — shared client-side behavior

// Tracks which member is currently shown in the modal, among the
// currently-visible (filtered) cards, so Prev/Next and the arrow keys
// know where to go next.
let visibleCards = [];
let currentCardIndex = -1;

function getVisibleCards() {
  return Array.from(document.querySelectorAll("#memberGrid .card")).filter(
    (c) => c.style.display !== "none"
  );
}

function showDetails(card) {
  const name = card.dataset.fullName;
  const id = card.dataset.memberId;
  const group = card.dataset.group;
  const phone = card.dataset.phone;
  const photo = card.dataset.photo;
  const pk = card.dataset.pk;

  document.getElementById("modalPhoto").src = photo;
  document.getElementById("modalName").textContent = name;
  document.getElementById("modalId").textContent = id;
  document.getElementById("modalGroup").textContent = group;
  document.getElementById("modalPhone").textContent = phone || "N/A";
  document.getElementById("modalEditLink").href = "/edit/" + pk;
  document.getElementById("modalDeleteForm").action = "/delete/" + pk;

  visibleCards = getVisibleCards();
  currentCardIndex = visibleCards.indexOf(card);
  updateNavButtons();

  document.getElementById("detailModal").classList.add("show");
  document.body.style.overflow = "hidden";
}

// Moves the modal to the next (step=1) or previous (step=-1) member among
// the currently visible cards, wrapping around at each end.
function showRelative(step) {
  if (visibleCards.length === 0) return;
  currentCardIndex = (currentCardIndex + step + visibleCards.length) % visibleCards.length;
  showDetails(visibleCards[currentCardIndex]);
}

function updateNavButtons() {
  const show = visibleCards.length > 1 ? "flex" : "none";
  const prevBtn = document.getElementById("modalPrev");
  const nextBtn = document.getElementById("modalNext");
  if (prevBtn) prevBtn.style.display = show;
  if (nextBtn) nextBtn.style.display = show;
}

function closeModal() {
  document.getElementById("detailModal").classList.remove("show");
  document.body.style.overflow = "";
}

document.addEventListener("keydown", (e) => {
  if (!document.getElementById("detailModal").classList.contains("show")) return;
  if (e.key === "Escape") closeModal();
  if (e.key === "ArrowRight") showRelative(1);
  if (e.key === "ArrowLeft") showRelative(-1);
});

function filterMembers() {
  const searchInput = document.getElementById("searchInput");
  const activeChip = document.querySelector("#groupFilter .chip.active");
  const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
  const group = activeChip ? activeChip.getAttribute("data-group") : "";
  const cards = document.querySelectorAll("#memberGrid .card");
  let visibleCount = 0;

  cards.forEach((card) => {
    const name = card.getAttribute("data-name");
    const id = card.getAttribute("data-id");
    const cardGroup = card.getAttribute("data-group");

    const matchesSearch = !query || name.includes(query) || id.includes(query);
    const matchesGroup = !group || cardGroup === group;

    if (matchesSearch && matchesGroup) {
      card.style.display = "";
      visibleCount++;
    } else {
      card.style.display = "none";
    }
  });

  const totalEl = document.getElementById("totalCount");
  if (totalEl) totalEl.textContent = visibleCount;

  const noResultsEl = document.getElementById("noResults");
  if (noResultsEl) noResultsEl.style.display = visibleCount === 0 ? "block" : "none";
}

// Group filter chips (All / Men / Women / Youth / Children) — clicking one
// marks it active and re-runs the filter, same as the search box does.
function initFilterChips() {
  const chips = document.querySelectorAll("#groupFilter .chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      filterMembers();
    });
  });
}

document.addEventListener("DOMContentLoaded", initFilterChips);

// Live preview of the chosen photo on the Add Member form, so staff can
// confirm the right picture was picked before saving.
function initPhotoPreview() {
  const input = document.getElementById("photoInput");
  const preview = document.getElementById("photoPreview");
  if (!input || !preview) return;

  input.addEventListener("change", () => {
    const file = input.files && input.files[0];
    if (!file) {
      preview.style.display = "none";
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.style.display = "block";
    };
    reader.readAsDataURL(file);
  });
}

document.addEventListener("DOMContentLoaded", initPhotoPreview);

// Register the service worker so the app shell can be installed to the
// home screen and loads instantly / works offline after the first visit.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* offline install is a nice-to-have, not required for the app to work */
    });
  });
}
