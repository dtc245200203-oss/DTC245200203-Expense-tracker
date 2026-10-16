// State
let categories = [];
let categoryChartInstance = null;
let trendChartInstance = null;

// Helpers
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const d = new Date(dateString);
  return d.toLocaleDateString('vi-VN');
};

// DOM Elements
const netBalanceEl = document.getElementById('netBalance');
const totalIncomeEl = document.getElementById('totalIncome');
const totalExpenseEl = document.getElementById('totalExpense');
const transactionCountEl = document.getElementById('transactionCount');
const transactionsBody = document.getElementById('transactionsBody');
const filterType = document.getElementById('filterType');
const filterCategory = document.getElementById('filterCategory');
const filterSearch = document.getElementById('filterSearch');
const btnRefresh = document.getElementById('btnRefresh');

// Modal Elements
const modal = document.getElementById('transactionModal');
const btnOpenModal = document.getElementById('btnOpenModal');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnCancelModal = document.getElementById('btnCancelModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const transactionForm = document.getElementById('transactionForm');
const categoryIdSelect = document.getElementById('categoryId');
const transactionDateInput = document.getElementById('transactionDate');

// Initialize default date in modal
transactionDateInput.value = new Date().toISOString().split('T')[0];

// Fetch Categories
async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    categories = await res.json();
    populateCategoryDropdowns();
  } catch (err) {
    console.error('Failed to load categories', err);
  }
}

function populateCategoryDropdowns() {
  // Populate Filter Category
  filterCategory.innerHTML = '<option value="">Tất cả danh mục</option>';
  categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = `${c.name} (${c.type === 'income' ? 'Thu' : 'Chi'})`;
    filterCategory.appendChild(opt);
  });

  // Populate Modal Category based on selected radio type
  updateModalCategories();
}

function updateModalCategories() {
  const selectedType = document.querySelector('input[name="type"]:checked').value;
  categoryIdSelect.innerHTML = '<option value="">-- Chọn danh mục --</option>';
  const filtered = categories.filter(c => c.type === selectedType);
  filtered.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.name;
    categoryIdSelect.appendChild(opt);
  });
}

// Fetch Stats & Render Charts
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    // 1. Update Cards
    netBalanceEl.textContent = formatCurrency(data.summary.netBalance);
    totalIncomeEl.textContent = formatCurrency(data.summary.totalIncome);
    totalExpenseEl.textContent = formatCurrency(data.summary.totalExpense);
    transactionCountEl.innerHTML = `<i class="fa-solid fa-receipt"></i> ${data.summary.totalTransactions} giao dịch`;

    // 2. Render Doughnut Chart (Categories)
    renderCategoryChart(data.categoryBreakdown);

    // 3. Render Bar Chart (Monthly Trend)
    renderTrendChart(data.monthlyTrend);
  } catch (err) {
    console.error('Failed to load stats', err);
  }
}

function renderCategoryChart(data) {
  const ctx = document.getElementById('categoryChart').getContext('2d');
  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  if (!data || data.length === 0) {
    categoryChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Chưa có dữ liệu'],
        datasets: [{ data: [1], backgroundColor: ['#e2e8f0'] }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
    return;
  }

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: data.map(d => d.color || '#4f46e5'),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.raw)}`
          }
        }
      },
      cutout: '65%'
    }
  });
}

function renderTrendChart(data) {
  const ctx = document.getElementById('trendChart').getContext('2d');
  if (trendChartInstance) {
    trendChartInstance.destroy();
  }

  const labels = data.map(d => d.month);
  const incomeData = data.map(d => d.income);
  const expenseData = data.map(d => d.expense);

  trendChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['Hiện tại'],
      datasets: [
        {
          label: 'Thu nhập',
          data: incomeData.length ? incomeData : [0],
          backgroundColor: '#10b981',
          borderRadius: 4
        },
        {
          label: 'Chi tiêu',
          data: expenseData.length ? expenseData : [0],
          backgroundColor: '#ef4444',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (val) => val >= 1000000 ? `${val / 1000000}M` : `${val / 1000}k`
          }
        }
      },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
          }
        }
      }
    }
  });
}

// Fetch Transactions
async function loadTransactions() {
  try {
    const params = new URLSearchParams();
    if (filterType.value) params.append('type', filterType.value);
    if (filterCategory.value) params.append('category_id', filterCategory.value);
    if (filterSearch.value.trim()) params.append('search', filterSearch.value.trim());

    const res = await fetch(`/api/transactions?${params.toString()}`);
    const transactions = await res.json();

    if (transactions.length === 0) {
      transactionsBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 24px;">Không tìm thấy giao dịch nào</td></tr>`;
      return;
    }

    transactionsBody.innerHTML = transactions.map(t => {
      const isIncome = t.type === 'income';
      const typeBadge = isIncome 
        ? `<span class="badge" style="background:#ecfdf5; color:#059669;"><i class="fa-solid fa-arrow-up"></i> Thu</span>`
        : `<span class="badge" style="background:#fef2f2; color:#dc2626;"><i class="fa-solid fa-arrow-down"></i> Chi</span>`;
      
      const categoryBadge = `
        <span class="category-badge" style="background: ${t.category_color}15; color: ${t.category_color};">
          <i class="fa-solid fa-${t.category_icon || 'tag'}"></i> ${t.category_name}
        </span>
      `;

      const amountFormatted = isIncome 
        ? `+${formatCurrency(t.amount)}` 
        : `-${formatCurrency(t.amount)}`;
      const amountClass = isIncome ? 'text-green font-bold' : 'text-red font-bold';

      return `
        <tr>
          <td>${formatDate(t.transaction_date)}</td>
          <td>${typeBadge}</td>
          <td>${categoryBadge}</td>
          <td>${t.description || '<span class="text-muted">(Không có mô tả)</span>'}</td>
          <td class="${amountClass}">${amountFormatted}</td>
          <td class="text-center">
            <button class="action-btn delete" onclick="deleteTransaction(${t.id})" title="Xóa giao dịch">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load transactions', err);
    transactionsBody.innerHTML = `<tr><td colspan="6" class="text-center text-red">Lỗi tải dữ liệu giao dịch</td></tr>`;
  }
}

// Delete Transaction
async function deleteTransaction(id) {
  if (!confirm('Bạn có chắc chắn muốn xóa giao dịch này không?')) return;
  try {
    const res = await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
    if (res.ok) {
      loadStats();
      loadTransactions();
    } else {
      alert('Không thể xóa giao dịch');
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ');
  }
}

// Event Listeners for Filters
filterType.addEventListener('change', loadTransactions);
filterCategory.addEventListener('change', loadTransactions);
let searchTimeout;
filterSearch.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadTransactions, 300);
});
btnRefresh.addEventListener('click', () => {
  loadStats();
  loadTransactions();
});

// Modal Actions
function openModal() {
  modal.classList.add('active');
  updateModalCategories();
}

function closeModal() {
  modal.classList.remove('active');
  transactionForm.reset();
  transactionDateInput.value = new Date().toISOString().split('T')[0];
}

btnOpenModal.addEventListener('click', openModal);
btnCloseModal.addEventListener('click', closeModal);
btnCancelModal.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', closeModal);

document.querySelectorAll('input[name="type"]').forEach(r => {
  r.addEventListener('change', updateModalCategories);
});

// Submit Transaction
transactionForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(transactionForm);
  const payload = {
    type: formData.get('type'),
    amount: parseFloat(formData.get('amount')),
    category_id: parseInt(formData.get('category_id'), 10),
    transaction_date: formData.get('transaction_date'),
    description: formData.get('description')
  };

  try {
    const res = await fetch('/api/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      closeModal();
      loadStats();
      loadTransactions();
    } else {
      const errData = await res.json();
      alert(`Lỗi: ${errData.error || 'Không thể tạo giao dịch'}`);
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ');
  }
});

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  loadCategories();
  loadStats();
  loadTransactions();
});
