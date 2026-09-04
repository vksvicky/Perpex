// showcase/app.js - Dynamic Card Renderer & Interactive Hotspots
document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('cards-grid');
  if (!grid || typeof SHOWCASE_CARDS === 'undefined') return;

  // Render cards
  SHOWCASE_CARDS.forEach(card => {
    const cardEl = document.createElement('article');
    cardEl.className = 'showcase-card';
    cardEl.dataset.category = card.category;

    let hotspotsHtml = '';
    card.slots.forEach(slot => {
      hotspotsHtml += `
        <div class="hotspot" style="left: ${slot.left}%; top: ${slot.top}%;">
          <div class="pin" aria-label="Slot ${slot.slot}: ${slot.name}"></div>
          <div class="tooltip">
            <div class="tooltip-header">
              <span class="slot-badge">Slot ${slot.slot}</span>
              <span class="tooltip-name">${slot.name}</span>
            </div>
            <div class="tooltip-value">${slot.val}</div>
            <div class="tooltip-desc">${slot.desc}</div>
            <div class="tooltip-setting"><code>${slot.setting}</code></div>
          </div>
        </div>`;
    });

    cardEl.innerHTML = `
      <div class="card-header">
        <span class="badge ${card.category}">${card.category.replace('_', ' ')}</span>
        <h3>${card.title}</h3>
        <p>${card.subtitle}</p>
      </div>
      <div class="watch-stage">
        <img class="watch-img" src="${card.image}" alt="${card.title}">
        <div class="hotspots-overlay">${hotspotsHtml}</div>
      </div>
      <div class="card-footer">
        <a href="${card.annotated}" target="_blank" class="btn-card">View Annotated Blueprint &rarr;</a>
      </div>`;

    grid.appendChild(cardEl);
  });

  // Filter functionality
  const buttons = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.showcase-card');

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;

      cards.forEach(card => {
        if (filter === 'all' || card.dataset.category === filter) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});
