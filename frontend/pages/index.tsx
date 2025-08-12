import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Trading Platform MVP</h1>
      <p>Try a stock page:</p>
      <ul>
        <li><Link href="/stock/INFY">INFY</Link></li>
        <li><Link href="/stock/TCS">TCS</Link></li>
      </ul>
    </main>
  );
}
