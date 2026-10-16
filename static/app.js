const app = document.querySelector("#app");
let site = null;
let gifts = [];
let recommendations = [];
let selectedGift = null;
let rsvpGroup = null;
let selectedRsvpCandidate = null;

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js").catch(() => {});
}

function formatMoney(value) {
  return value === null || value === undefined ? "Valor livre" : money.format(value);
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || "Erro inesperado");
  }
  return data;
}

function renderResult(title, text) {
  app.innerHTML = `
    <main class="result-page">
      <section class="result">
        <p class="eyebrow">Casamento</p>
        <h1>${escapeHtml(title)}</h1>
        <div class="divider"></div>
        <p>${escapeHtml(text)}</p>
        <a class="primary" href="/">Voltar para o site</a>
      </section>
    </main>
  `;
}

function renderHome(error = "") {
  app.innerHTML = `
    <div class="shell">
      <nav class="nav">
        <a class="brand" href="#top" aria-label="${escapeHtml(site.couple_names)}">
          ${renderLogo()}
          <span>${escapeHtml(site.couple_names)}</span>
        </a>
        <div>
          <a href="#casal">O Casal</a>
          <a href="#cerimonia">Cerimônia & Baile</a>
          <a href="#presentes">Presentes</a>
          ${site.show_rsvp ? '<a href="#presenca">Presença</a>' : ""}
        </div>
      </nav>

      <header class="hero" id="top" style="background-image: linear-gradient(rgba(250,248,243,.20), rgba(250,248,243,.86)), url('${escapeHtml(site.hero_image_url)}')">
        <div class="hero-card">
          <p class="eyebrow">${escapeHtml(site.save_the_date_text)}</p>
          <h1>${formatCoupleNames(site.couple_names)}</h1>
          <div class="divider"></div>
          <p class="date">${escapeHtml(site.wedding_date)}</p>
        </div>
      </header>

      <main>
        ${error ? `<section class="section slim"><div class="alert">${escapeHtml(error)}</div></section>` : ""}
        ${renderIntro()}
        ${renderCouple()}
        ${renderCeremony()}
        ${renderGifts()}
        ${renderRsvp()}
        ${renderRecommendations()}
      </main>
      <footer class="footer-site">${escapeHtml(site.couple_names)} - ${escapeHtml(site.wedding_date)}</footer>
    </div>
  `;

  document.querySelectorAll("[data-gift-id]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedGift = gifts.find((gift) => gift.id === Number(button.dataset.giftId));
      startGiftCheckout(selectedGift);
    });
  });
  document.querySelector("#open-rsvp")?.addEventListener("click", openRsvpStartModal);
  requestAnimationFrame(initCoupleCarousel);
}

function renderIntro() {
  return "";
}

function renderCouple() {
  const images = parseCoupleImages();
  return `
    <section class="section split" id="casal">
      <div>
        <p class="eyebrow">O Casal</p>
        <h2>${escapeHtml(site.couple_title)}</h2>
        <div class="divider left"></div>
        <p>${escapeHtml(site.couple_text)}</p>
      </div>
      <div class="couple-carousel" data-couple-carousel aria-label="Fotos do casal">
        <div class="couple-carousel__slides">
          ${images.map((image, index) => `<img class="couple-carousel__slide${index === 0 ? " is-active" : ""}" src="${escapeHtml(image)}" alt="Foto de Maisa e João" loading="eager" />`).join("")}
        </div>
        ${images.length > 1 ? `
          <div class="couple-carousel__dots" aria-label="Selecionar foto">
            ${images.map((_, index) => `<button type="button" class="couple-carousel__dot${index === 0 ? " is-active" : ""}" data-carousel-dot="${index}" aria-label="Ir para foto ${index + 1}"></button>`).join("")}
          </div>
        ` : ""}
      </div>
    </section>
  `;
}

function parseCoupleImages() {
  const raw = site.couple_image_urls || site.couple_image_url || "";
  const images = String(raw).split(/\r?\n|,/).map((item) => item.trim()).filter(Boolean).slice(0, 10);
  return images.length ? images : [site.couple_image_url];
}

let coupleCarouselTimer = null;

function initCoupleCarousel() {
  const carousel = document.querySelector("[data-couple-carousel]");
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll(".couple-carousel__slide")];
  if (slides.length < 2) return;

  let current = 0;
  const dots = [...carousel.querySelectorAll("[data-carousel-dot]")];
  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => slide.classList.toggle("is-active", slideIndex === current));
    dots.forEach((dot, dotIndex) => dot.classList.toggle("is-active", dotIndex === current));
  };
  const next = () => show(current + 1);

  dots.forEach((dot) => dot.addEventListener("click", () => show(Number(dot.dataset.carouselDot))));
  coupleCarouselTimer = setInterval(next, 5000);
}

function renderCeremony() {
  return `
    <section class="section band" id="cerimonia">
      <div class="ceremony-layout">
        <div class="ceremony-layout__copy">
          <p class="eyebrow">Local</p>
          <h2>${escapeHtml(site.ceremony_title)}</h2>
          <div class="divider"></div>
          <p>${escapeHtml(site.ceremony_text)}</p>
          <img class="ceremony-layout__mobile-image" src="${escapeHtml(site.ceremony_image_url)}" alt="${escapeHtml(site.ceremony_title)}" />
          <p class="address">${escapeHtml(site.ceremony_address)}</p>
          <a class="secondary" href="${escapeHtml(site.ceremony_maps_url)}" target="_blank" rel="noreferrer">Abrir no Maps</a>
        </div>
        <img class="ceremony-layout__desktop-image" src="${escapeHtml(site.ceremony_image_url)}" alt="${escapeHtml(site.ceremony_title)}" />
      </div>
    </section>
  `;
}

function renderGifts() {
  return `
    <section class="section" id="presentes">
      <h2>${escapeHtml(site.gifts_title)}</h2>
      <div class="divider"></div>
      <p class="section-copy">${escapeHtml(site.gifts_text)}</p>
      <div class="grid gifts">
        ${gifts.map(renderGift).join("")}
      </div>
    </section>
  `;
}

function renderGift(gift) {
  return `
    <article class="card gift">
      <img src="${escapeHtml(gift.image_url)}" alt="" />
      <div class="card-body">
        <h3>${escapeHtml(gift.title)}</h3>
        ${gift.subtitle ? `<small>${escapeHtml(gift.subtitle)}</small>` : ""}
        <p>${escapeHtml(gift.description)}</p>
        <div class="card-footer">
          <strong>${gift.is_variable_amount ? "Escolha o valor" : formatMoney(gift.price)}</strong>
          <button class="primary" data-gift-id="${gift.id}">Presentear</button>
        </div>
      </div>
    </article>
  `;
}

async function startGiftCheckout(gift) {
  if (!gift) return;

  let amount = null;
  if (gift.is_variable_amount) {
    const raw = window.prompt("Informe o valor da sua contribuição (mínimo de R$ 1):", "1");
    if (raw === null) return;
    amount = Number(String(raw).replace(",", "."));
    if (!Number.isFinite(amount) || amount < 1) {
      window.alert("Informe um valor válido de no mínimo R$ 1.");
      return;
    }
  }

  try {
    const response = await api("/api/payments/create-preference", {
      method: "POST",
      body: JSON.stringify({
        gift_id: gift.id,
        guest_name: "Convidado",
        guest_email: null,
        guest_phone: null,
        guest_message: null,
        amount,
      }),
    });
    const checkoutUrl = response.checkout_url || response.sandbox_init_point || response.init_point;
    if (!checkoutUrl) throw new Error("Mercado Pago não retornou a URL de pagamento.");
    window.location.href = checkoutUrl;
  } catch (err) {
    window.alert(err.message || "Não foi possível abrir o pagamento.");
  }
}

function renderRsvp() {
  if (!site.show_rsvp) return "";
  return `
    <section class="section band" id="presenca">
      <p class="eyebrow">RSVP</p>
      <h2>${escapeHtml(site.rsvp_title)}</h2>
      <div class="divider"></div>
      <p class="section-copy">${escapeHtml(site.rsvp_text)}</p>
      <button class="primary" type="button" id="open-rsvp">Confirme sua presença!</button>
    </section>
  `;
}

function renderRecommendations() {
  if (!recommendations.length) return "";
  return `
    <section class="section" id="sugestoes">
      <p class="eyebrow">Para se organizar</p>
      <h2>Sugestão</h2>
      <div class="divider"></div>
      <div class="grid">
        ${recommendations.map((item) => `
          <article class="card rec">
            <img src="${escapeHtml(item.image_url)}" alt="" />
            <div class="card-body">
              <span class="pill">${escapeHtml(item.category)}</span>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.subtitle || "")}</p>
              ${item.link_url ? `<a class="secondary" href="${escapeHtml(item.link_url)}" target="_blank" rel="noreferrer">Ver detalhes</a>` : ""}
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderGiftModal(error = "") {
  const modal = document.createElement("div");
  modal.className = "backdrop";
  modal.innerHTML = `
    <form class="modal gift-modal">
      <div class="gift-modal__media">
        <img src="${escapeHtml(selectedGift.image_url)}" alt="" />
        <div class="gift-modal__media-shade"></div>
        <div class="gift-modal__media-copy">
          <small>Seu presente</small>
          <strong>${escapeHtml(selectedGift.title)}</strong>
          <span>${escapeHtml(selectedGift.subtitle || "Um carinho especial para os noivos")}</span>
        </div>
        <button class="icon modal-close" type="button" id="close-modal" aria-label="Fechar">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="gift-modal__content">
        <div class="modal-head">
          <div>
            <small>Presentear</small>
            <h2>Quase lá</h2>
            <p class="gift-modal__intro">Informe seus dados e continue para o pagamento seguro.</p>
          </div>
        </div>
        <p class="gift-description">${escapeHtml(selectedGift.description)}</p>
        <div class="gift-price-box">
          <span>${selectedGift.is_variable_amount ? "Valor da contribuição" : "Valor do presente"}</span>
          <strong>${selectedGift.is_variable_amount ? "Escolha o valor" : formatMoney(selectedGift.price)}</strong>
        </div>
        <section class="giver-box giver-box--compact">
          <div class="giver-box__head">
            <small>Identificação</small>
            <p>Pesquise seu nome se já estiver na lista ou preencha manualmente abaixo.</p>
          </div>
          <div class="giver-search">
            <input name="guestSearch" placeholder="Pesquisar nome ou família" />
            <button class="secondary" type="button" id="gift-guest-search">Buscar</button>
          </div>
          <div id="gift-guest-results"></div>
        </section>
        <div class="form-stack">
          <label class="wide-field">Seu nome <input name="guestName" required minlength="2" placeholder="Como podemos identificar seu carinho?" /></label>
          <label>E-mail <input name="guestEmail" type="email" ${site.require_email ? "required" : ""} placeholder="voce@exemplo.com" /></label>
          <label>Telefone <input name="guestPhone" inputmode="tel" ${site.require_phone ? "required" : ""} /></label>
          ${selectedGift.is_variable_amount ? '<label>Valor da cota <input name="amount" type="number" min="10" step="0.01" value="100" required /></label>' : ""}
          <label class="wide-field">Mensagem <textarea name="guestMessage" rows="3" ${site.require_message ? "required" : ""} placeholder="Deixe um recado para os noivos"></textarea></label>
        </div>
        ${error ? `<div class="alert">${escapeHtml(error)}</div>` : ""}
        <button class="primary" type="submit">Abrir checkout</button>
      </div>
    </form>
  `;
  document.body.appendChild(modal);
  modal.querySelector("#close-modal").addEventListener("click", () => modal.remove());
  modal.querySelector("#gift-guest-search").addEventListener("click", () => searchGiftGuests(modal));
  modal.querySelector("[name='guestSearch']").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      searchGiftGuests(modal);
    }
  });
  modal.querySelector("form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const response = await api("/api/payments/create-preference", {
        method: "POST",
        body: JSON.stringify({
          gift_id: selectedGift.id,
          guest_name: form.get("guestName"),
          guest_email: form.get("guestEmail") || null,
          guest_phone: form.get("guestPhone") || null,
          guest_message: form.get("guestMessage") || null,
          amount: selectedGift.is_variable_amount ? Number(form.get("amount")) : null,
        }),
      });
      window.location.href = response.checkout_url || response.sandbox_init_point || response.init_point;
    } catch (err) {
      modal.remove();
      renderGiftModal(err.message);
    }
  });
}

async function searchGiftGuests(modal) {
  const input = modal.querySelector("[name='guestSearch']");
  const target = modal.querySelector("#gift-guest-results");
  const query = input.value.trim();
  if (query.length < 2) {
    target.innerHTML = '<div class="mini-alert">Digite ao menos 2 letras.</div>';
    return;
  }

  target.innerHTML = '<div class="mini-alert">Buscando...</div>';
  try {
    const results = await api("/api/content/guests/search", {
      method: "POST",
      body: JSON.stringify({ responsible_name: query }),
    });

    if (!results.length) {
      target.innerHTML = '<div class="mini-alert">Não encontramos esse nome. Você pode preencher manualmente.</div>';
      return;
    }

    target.innerHTML = results.map(renderGiftGuestGroup).join("");
    target.querySelectorAll("[data-fill-family]").forEach((button) => {
      button.addEventListener("click", () => {
        const group = button.closest(".gift-guest-group");
        const members = [...(group?.querySelectorAll("[data-member-check]") || [])];
        members.forEach((checkbox) => {
          checkbox.checked = true;
        });
        if (!members.length) {
          modal.querySelector("[name='guestName']").value = button.dataset.fillFamily;
        }
        syncGiftConfirmation(modal);
        button.textContent = "Família selecionada";
        button.disabled = true;
      });
    });
    target.querySelectorAll("[data-member-check]").forEach((checkbox) => {
      checkbox.addEventListener("change", () => syncGiftConfirmation(modal));
    });
  } catch (err) {
    target.innerHTML = `<div class="mini-alert">${escapeHtml(err.message)}</div>`;
  }
}

function renderGiftGuestGroup(group) {
  const members = Array.isArray(group.members) ? group.members : [];
  return `
    <div class="gift-guest-group">
      <div class="gift-guest-group__top">
        <strong>${escapeHtml(group.group_name)}</strong>
        <button class="secondary compact" type="button" data-fill-family="${escapeHtml(group.group_name)}">Usar família</button>
      </div>
      <div class="member-chips">
        ${members.map((member) => `
          <label class="member-chip">
            <input type="checkbox" data-member-check value="${escapeHtml(member.name)}" />
            <span>${escapeHtml(member.name)}</span>
          </label>
        `).join("")}
      </div>
    </div>
  `;
}

function syncGiftConfirmation(modal) {
  const selectedNames = [...modal.querySelectorAll("[data-member-check]:checked")].map((item) => item.value);
  if (selectedNames.length) {
    modal.querySelector("[name='guestName']").value = selectedNames.join(", ");
  }
}

async function handleRsvpLookup(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const modal = event.currentTarget.closest(".rsvp-modal");
  const target = modal.querySelector("[data-rsvp-stage]");
  try {
    const results = await api("/api/content/rsvp/search", {
      method: "POST",
      body: JSON.stringify({
        responsible_name: form.get("responsible_name"),
      }),
    });
    if (!results.length) {
      target.innerHTML = `${renderRsvpSearchForm("Não encontramos nenhum grupo com esse nome.")}`;
      target.querySelector("form").addEventListener("submit", handleRsvpLookup);
      return;
    }
    target.innerHTML = renderRsvpResults(results);
    target.querySelectorAll("[data-rsvp-candidate]").forEach((button) => {
      button.addEventListener("click", () => {
        selectedRsvpCandidate = results.find((item) => item.id === Number(button.dataset.rsvpCandidate));
        target.innerHTML = renderRsvpValidation(selectedRsvpCandidate);
        target.querySelector("form").addEventListener("submit", handleRsvpValidate);
      });
    });
  } catch (err) {
    target.innerHTML = `${renderRsvpSearchForm(err.message)}`;
    target.querySelector("form").addEventListener("submit", handleRsvpLookup);
  }
}

function openRsvpStartModal() {
  const modal = document.createElement("div");
  modal.className = "backdrop";
  modal.innerHTML = `
    <section class="modal rsvp-modal" role="dialog" aria-modal="true">
      <button class="icon modal-close" type="button" data-close-rsvp aria-label="Fechar">
        <span aria-hidden="true">&times;</span>
      </button>
      <div class="rsvp-modal__intro">
        <p class="eyebrow">Confirmação de presença</p>
        <h2>${escapeHtml(site.rsvp_title)}</h2>
        <p>${escapeHtml(site.rsvp_text)}</p>
      </div>
      <div data-rsvp-stage>
        ${renderRsvpSearchForm()}
      </div>
    </section>
  `;
  document.body.appendChild(modal);
  modal.querySelector("[data-close-rsvp]").addEventListener("click", () => modal.remove());
  modal.querySelector("form").addEventListener("submit", handleRsvpLookup);
}

function renderRsvpSearchForm(error = "") {
  return `
    <form class="rsvp-card rsvp-card--modal">
      ${error ? `<div class="alert">${escapeHtml(error)}</div>` : ""}
      <label>Nome do responsavel ou convidado
        <input name="responsible_name" required minlength="2" placeholder="Digite parte do nome" autofocus />
      </label>
      <button class="primary" type="submit">Pesquisar grupo</button>
    </form>
  `;
}

function renderRsvpResults(results) {
  return `
    <div class="rsvp-card rsvp-card--modal">
      <h3>Encontramos estes grupos</h3>
      <p>Selecione o seu e valide com o telefone cadastrado.</p>
      <div class="rsvp-options">
        ${results.map((item) => `
          <button class="rsvp-option" type="button" data-rsvp-candidate="${item.id}">
            <strong>${escapeHtml(item.group_name)}</strong>
            <span>${escapeHtml(item.responsible_name)} - ${escapeHtml(item.masked_phone)}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderRsvpValidation(candidate, error = "") {
  return `
    <form class="rsvp-card rsvp-card--modal">
      <h3>${escapeHtml(candidate.group_name)}</h3>
      <p>Para proteger a lista, confirme o telefone cadastrado. Dica: ${escapeHtml(candidate.masked_phone)}</p>
      ${error ? `<div class="alert">${escapeHtml(error)}</div>` : ""}
      <label>Telefone cadastrado <input name="phone_digits" required minlength="4" inputmode="numeric" placeholder="Digite o número ou os últimos 4 dígitos" /></label>
      <button class="primary" type="submit">Validar e continuar</button>
    </form>
  `;
}

async function handleRsvpValidate(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    rsvpGroup = await api("/api/content/rsvp/validate", {
      method: "POST",
      body: JSON.stringify({
        group_id: selectedRsvpCandidate.id,
        phone_digits: form.get("phone_digits"),
      }),
    });
    openRsvpModal(form.get("phone_digits"));
  } catch (err) {
    const modal = event.currentTarget.closest(".rsvp-modal");
    const target = modal.querySelector("[data-rsvp-stage]");
    target.innerHTML = renderRsvpValidation(selectedRsvpCandidate, err.message);
    target.querySelector("form").addEventListener("submit", handleRsvpValidate);
  }
}

function renderRsvpGroup(group, phoneDigits) {
  const members = Array.isArray(group.members) ? group.members : [];
  return `
    <form class="rsvp-card rsvp-card--modal" data-phone="${escapeHtml(phoneDigits)}">
      ${members.map((member) => `
        <div class="rsvp-row ${member.will_attend === true ? "is-going" : member.will_attend === false ? "is-not-going" : ""}">
          <strong>${escapeHtml(member.name)}</strong>
          <select name="member_${member.id}">
            <option value="">A confirmar</option>
            <option value="true" ${member.will_attend === true ? "selected" : ""}>Vai</option>
            <option value="false" ${member.will_attend === false ? "selected" : ""}>Não vai</option>
          </select>
          <input name="note_${member.id}" value="${escapeHtml(member.note || "")}" placeholder="Observação" />
        </div>
      `).join("")}
      <button class="primary" type="submit">Salvar confirmação</button>
    </form>
  `;
}

function openRsvpModal(phoneDigits) {
  const modal = document.querySelector(".rsvp-modal");
  modal.querySelector(".rsvp-modal__intro").innerHTML = `
    <p class="eyebrow">Confirmação de presença</p>
    <h2>${escapeHtml(rsvpGroup.group_name)}</h2>
    <p>Marque cada pessoa do grupo e salve a confirmação. Você pode ajustar novamente se precisar.</p>
  `;
  const target = modal.querySelector("[data-rsvp-stage]");
  target.innerHTML = renderRsvpGroup(rsvpGroup, phoneDigits);
  target.querySelector("form").addEventListener("submit", handleRsvpConfirm);
}

async function handleRsvpConfirm(event) {
  event.preventDefault();
  const modal = event.currentTarget.closest(".rsvp-modal");
  const target = modal.querySelector("[data-rsvp-stage]");
  const submit = event.currentTarget.querySelector("button[type='submit']");
  submit.disabled = true;
  submit.textContent = "Salvando...";
  try {
    const form = new FormData(event.currentTarget);
    const rsvpMembers = Array.isArray(rsvpGroup.members) ? rsvpGroup.members : [];
    const members = rsvpMembers.map((member) => {
      const raw = form.get(`member_${member.id}`);
      return {
        id: member.id,
        will_attend: raw === "" ? null : raw === "true",
        note: form.get(`note_${member.id}`) || null,
      };
    });
    rsvpGroup = await api("/api/content/rsvp/confirm", {
      method: "POST",
      body: JSON.stringify({
        group_id: rsvpGroup.id,
        phone_digits: event.currentTarget.dataset.phone,
        members,
      }),
    });
    modal.querySelector(".rsvp-modal__intro").remove();
    target.innerHTML = renderRsvpSuccess(rsvpGroup);
    target.querySelector("[data-close-success]").addEventListener("click", () => {
      modal.closest(".backdrop").remove();
    });
  } catch (err) {
    submit.disabled = false;
    submit.textContent = "Salvar confirmação";
    const error = document.createElement("div");
    error.className = "alert";
    error.textContent = err.message || "Não foi possível salvar sua confirmação.";
    target.prepend(error);
  }
}

function renderRsvpSuccess(group) {
  const members = Array.isArray(group.members) ? group.members : [];
  const going = members.filter((member) => member.will_attend === true);
  const notGoing = members.filter((member) => member.will_attend === false);
  const pending = members.filter((member) => member.will_attend === null);

  return `
    <div class="rsvp-success rsvp-success--modal" role="status">
      <div class="checkmark" aria-hidden="true">✓</div>
      <div>
        <h3>Presença confirmada!</h3>
        <p>
          ${going.length} confirmado${going.length === 1 ? "" : "s"},
          ${notGoing.length} não vai${notGoing.length === 1 ? "" : "o"},
          ${pending.length} a confirmar.
        </p>
        <p>Obrigado por responder. Isso ajuda os noivos a organizarem tudo com carinho.</p>
        <button class="primary" type="button" data-close-success>Concluir</button>
      </div>
    </div>
  `;
}

function formatCoupleNames(value = "") {
  const safe = escapeHtml(value);
  return safe.replace(/\s*&amp;\s*|\s&\s/g, '<span class="amp">&amp;</span>');
}

function renderLogo() {
  if (site.logo_url) {
    const logoUrl = `${site.logo_url}${site.logo_url.includes("?") ? "&" : "?"}v=20261015`;
    return `<img class="brand-logo" src="${escapeHtml(logoUrl)}" alt="Logo do casal" />`;
  }

  return `
    <span class="brand-logo brand-logo--default">
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <circle cx="32" cy="32" r="27"></circle>
        <path d="M19 35c8-1 13-6 16-14-8 1-14 6-16 14Z"></path>
        <path d="M45 35c-8-1-13-6-16-14 8 1 14 6 16 14Z"></path>
        <text x="32" y="42" text-anchor="middle">${escapeHtml(site.brand_name || "M&B")}</text>
      </svg>
    </span>
  `;
}

async function loadHome() {
  app.innerHTML = '<main class="section"><div class="loading">Carregando...</div></main>';
  try {
    [site, gifts, recommendations] = await Promise.all([
      api("/api/content/site"),
      api("/api/gifts"),
      api("/api/content/recommendations"),
    ]);
    renderHome();
  } catch (err) {
    app.innerHTML = `<main class="section"><div class="alert">${escapeHtml(err.message)}</div></main>`;
  }
}

const results = {
  "/pagamento/sucesso": ["Pagamento recebido", "Obrigado pelo carinho. A confirmação final acontece pelo Mercado Pago e pode levar alguns instantes para aparecer na lista."],
  "/pagamento/falha": ["Pagamento não concluído", "Você pode voltar para o site e tentar novamente."],
  "/pagamento/pendente": ["Pagamento em análise", "Assim que o Mercado Pago aprovar, o presente será marcado como recebido."],
};

if (results[window.location.pathname]) {
  renderResult(...results[window.location.pathname]);
} else {
  loadHome();
}
