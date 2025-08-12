import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function StockPage() {
  const router = useRouter();
  const { ticker } = router.query as { ticker?: string };

  const [loading, setLoading] = useState(true);
  const [series, setSeries] = useState<any[]>([]);
  const [fundamentals, setFundamentals] = useState<any>(null);
  const [news, setNews] = useState<any[]>([]);

  useEffect(() => {
    if (!ticker) return;
    (async () => {
      setLoading(true);
      const [p, f, n] = await Promise.all([
        fetch(`${API_BASE}/api/stock/${ticker}/price?range=5y`).then(r => r.json()),
        fetch(`${API_BASE}/api/stock/${ticker}/fundamentals`).then(r => r.json()),
        fetch(`${API_BASE}/api/stock/${ticker}/news`).then(r => r.json()),
      ]);
      setSeries(p.series || []);
      setFundamentals(f);
      setNews(n.items || []);
      setLoading(false);
    })();
  }, [ticker]);

  const data = {
    labels: series.map(p => p.date),
    datasets: [{ label: `${ticker} Close`, data: series.map(p => p.close), tension: 0.2 }]
  };

  return (
    <main style={{ padding: 24, maxWidth: 1000, margin: "0 auto" }}>
      <h1>Stock: {ticker}</h1>
      {loading ? <p>Loading…</p> : (
        <>
          <section>
            <h3>Price (EOD)</h3>
            <Line data={data} />
          </section>
          <section>
            <h3>Fundamentals</h3>
            {fundamentals ? (
              <ul>
                <li>Market Cap: {fundamentals.market_cap}</li>
                <li>P/E: {fundamentals.pe}</li>
                <li>ROE: {fundamentals.roe}%</li>
                <li>EPS (TTM): {fundamentals.eps_ttm}</li>
                <li>D/E: {fundamentals.debt_to_equity}</li>
              </ul>
            ) : <p>No fundamentals.</p>}
          </section>
          <section>
            <h3>News</h3>
            <ul>
              {news.map((n, i) => (
                <li key={i}>
                  <a href={n.url} target="_blank" rel="noreferrer">{n.title}</a> — {n.source}
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </main>
  );
}
