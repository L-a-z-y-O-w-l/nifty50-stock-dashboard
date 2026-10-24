const BACKEND_URL = 'https://YOUR-BACKEND-URL.onrender.com';

const stockSelect = document.getElementById('stockSelect');
const loadBtn = document.getElementById('loadBtn');
const messageBox = document.getElementById('message');

async function fetchStocks() {
  try {
    messageBox.textContent = 'Loading stock list...';
    const response = await fetch(`${BACKEND_URL}/api/stocks`);
    const stocks = await response.json();

    stockSelect.innerHTML = '<option value="">Select a stock</option>';
    stocks.forEach(stock => {
      const option = document.createElement('option');
      option.value = stock.symbol;
      option.textContent = `${stock.name} (${stock.symbol})`;
      stockSelect.appendChild(option);
    });

    messageBox.textContent = 'Stock list loaded. Select a stock and click Load Chart.';
  } catch (error) {
    messageBox.textContent = `Could not load stock list: ${error.message}`;
  }
}

async function loadChart() {
  const symbol = stockSelect.value;
  if (!symbol) {
    messageBox.textContent = 'Please select a stock first.';
    return;
  }

  try {
    messageBox.textContent = `Loading chart for ${symbol}...`;
    const response = await fetch(`${BACKEND_URL}/api/stock-data?symbol=${encodeURIComponent(symbol)}`);
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || 'Failed to load stock data');
    }

    const dates = result.data.map(item => item.date);
    const open = result.data.map(item => item.open);
    const high = result.data.map(item => item.high);
    const low = result.data.map(item => item.low);
    const close = result.data.map(item => item.close);

    const trace = {
      x: dates,
      close: close,
      decreasing: { line: { color: '#d32f2f' } },
      high: high,
      increasing: { line: { color: '#2e7d32' } },
      line: { color: '#333' },
      low: low,
      open: open,
      type: 'candlestick',
      xaxis: 'x',
      yaxis: 'y'
    };

    const layout = {
      title: `${symbol} - 1 Year Candlestick Chart`,
      dragmode: 'zoom',
      margin: { r: 20, t: 50, b: 40, l: 60 },
      showlegend: false,
      xaxis: {
        rangeslider: { visible: false },
        title: 'Date'
      },
      yaxis: {
        title: 'Price'
      }
    };

    Plotly.newPlot('chart', [trace], layout, { responsive: true });
    messageBox.textContent = `Loaded ${result.count} candles for ${symbol}.`;
  } catch (error) {
    messageBox.textContent = `Could not load chart: ${error.message}`;
  }
}

loadBtn.addEventListener('click', loadChart);
fetchStocks();
