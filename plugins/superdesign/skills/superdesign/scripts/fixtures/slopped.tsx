// FIXTURE — deliberately slopped. The anti-slop gate MUST flag every tell here.
// Not part of the app build; lives outside examples/app-ui so it is never bundled.
import { Card } from "@/components/ui/card"

export function SloppedPanel({ rows }: { rows: { id: string; amount: number }[] }) {
  return (
    <div style={{ fontFamily: "Inter, sans-serif" }} className="p-[13px]">
      {/* every tell the gate should catch: */}
      <button className="bg-indigo-600 text-white rounded-md px-4 py-2">Get Started</button>
      <button className="rounded-full size-8 outline-none transition-all" tabIndex={2} aria-label="More" />
      <img src="/hero.png" alt="" className="bg-gradient-to-r focus:ring ring" />
      <div role="combobox" aria-owns="opts">Pick one — it’s the “best” option</div>
      <Card className="border-l-4 border-red-500 shadow-[0_1px_2px_rgba(0,0,0,0.1)]">
        <h2>🚀 Overview</h2>
        {rows.map((r) => (
          <div
            key={r.id}
            data-state={r.id === "sel" ? "selected" : undefined}
            className="data-[state=selected]:bg-primary gap-[18px] flex"
          >
            <span>{r.id}</span>
            <span>{r.amount}</span>
          </div>
        ))}
        // Now we render the footer
        // ... rest of code
      </Card>
      <footer>Built with v0</footer>
    </div>
  )
}
